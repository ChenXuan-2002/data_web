# -*- coding: utf-8 -*-
"""
Build bilingual dataset website (Professor Jinghua Li Laboratory)
-----------------------------------------------------------------
- 去除标题括号（不再显示“（中文）”“(English)”）
- 删除联系段落中“或直接邮件联系”字样 + 强行移除模板里的 mailto 残留行
- 摘要保留完整（不截断、不转义标点）
- UTF-8 强制、页脚防乱码（实体化版）
"""

import sys, io, json, html, re
from pathlib import Path
from datetime import datetime

# ---- 强制控制台 UTF-8（防 PowerShell cp936 影响）----
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TPL_DIR  = ROOT / "templates"
OUT_DATASETS = ROOT / "datasets"

# 读取模板（UTF-8）
TPL_DETAIL = (TPL_DIR / "dataset_page.html").read_text(encoding="utf-8")
TPL_INDEX  = (TPL_DIR / "index_page.html").read_text(encoding="utf-8")

CN_LAB_TITLE = "李菁華教授实验室数据库"
FORCE_ASCII_ENTITIES = True  # 确保浏览器显示正常

def esc(x: str) -> str:
    return html.escape(x or "")

def to_ascii_entities(s: str) -> str:
    """把非ASCII字符转为数字实体"""
    if not s: return ""
    return ''.join(ch if ord(ch) < 128 else f"&#{ord(ch)};" for ch in s)

def finalize_html(s: str) -> str:
    """
    仅对非摘要区域做数字实体化，防止中文摘要被拆分/截断。
    使用标记 <!--NO_ENTITY--> 包裹需要跳过实体化的片段（摘要）。
    """
    if not FORCE_ASCII_ENTITIES:
        return s
    if "<!--NO_ENTITY-->" not in s:
        return to_ascii_entities(s)
    parts = s.split("<!--NO_ENTITY-->")
    # 偶数索引（0,2,4,...)为普通区域，做实体化；奇数索引为需要保留的摘要区域
    for i in range(0, len(parts), 2):
        parts[i] = to_ascii_entities(parts[i])
    return "".join(parts)

# ---------- 新增：移除模板里残留的 mailto 段 ----------
_MAILTO_P = re.compile(
    r"<p>\s*(?:{{I18N_OR}}\s*)?(?:<a[^>]+href=['\"]mailto:[^'\"]+['\"][^>]*>[^<]*</a>)\s*</p>",
    flags=re.I
)
_EMPTY_P = re.compile(r"<p>\s*</p>", re.I)

def strip_mailto_paragraphs(html_text: str) -> str:
    html_text = _MAILTO_P.sub("", html_text)
    html_text = _EMPTY_P.sub("", html_text)
    return html_text

def render_publications_with_abstracts(pubs, lang="en"):
    """
    完整渲染论文列表：
    - 保留摘要原文（不转义、不实体化），仅合并换行；
    - 中文页摘要标签用“摘要：”，英文页用“Abstract:”
    """
    items = []
    for p in pubs or []:
        authors = esc(p.get("authors",""))
        year    = esc(str(p.get("year","")).strip())
        title   = esc(p.get("title",""))
        venue   = esc(p.get("venue",""))
        doi     = (p.get("doi") or "").strip()
        url     = (p.get("url") or "").strip()
        link = ""
        if doi:
            link = f'<a href="https://doi.org/{esc(doi)}" target="_blank" rel="noopener">DOI:{esc(doi)}</a>'
        elif url:
            link = f'<a href="{esc(url)}" target="_blank" rel="noopener">Link</a>'

        # 摘要：保留原文，不转义；仅把换行合并为空格避免破排
        abstract_raw = (p.get("abstract","") or "").replace("\n", " ").strip()
        if abstract_raw:
            label = "摘要：" if lang == "zh" else "Abstract:"
            abstract_html = f"<!--NO_ENTITY--><p><strong>{label}</strong> {abstract_raw}</p>"
        else:
            abstract_html = ""

        li = (
            f"<li><p><strong>{authors}</strong> ({year}). "
            f"<em>{title}</em>. {venue}. {link}</p>{abstract_html}</li>"
        )
        items.append(li)
    return "\n".join(items) if items else "<li>-</li>"

def build_jsonld(site, ds, lang):
    url = f"./{ds['slug']}-{lang}.html"
    props = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": ds.get("title",""),
        "description": (ds.get("summary") or "")[:300],
        "creator": {"@type": "Organization", "name": site.get("owner","")},
        "publisher": {"@type": "Organization", "name": site.get("affiliation","")},
        "license": site.get("license",""),
        "url": url,
        "variableMeasured": []
    }
    return json.dumps(props, ensure_ascii=False, indent=2)

def i18n_labels(lang):
    """中英文标签"""
    if lang == "zh":
        return {
            "LANG_ATTR": "zh-CN",
            "NAV_HOME": "首页",
            "NAV_CONTACT": "联系方式 / 申请",
            "NAV_SWITCH": "English",
            "I18N_METHODS": "实验方法",
            "I18N_QUESTIONNAIRE": "问卷和编码",  # ✅ 新增标签
            "I18N_PUBLICATIONS": "已发表论文",
            "I18N_CONTACT": "联系方式",
            "I18N_OR": "",
            "I18N_APPENDIX": "附录（问卷 PDF）",
            "LEAD_HOME": "以下为 李菁華教授实验室公开的数据库",
            "SECTION_TITLE": "数据库列表",
            "BTN_OPEN": "打开详情页",
            "LANG_SUFFIX": "zh",
            "ALT_LANG_SUFFIX": "en"
        }
    return {
        "LANG_ATTR": "en",
        "NAV_HOME": "Home",
        "NAV_CONTACT": "Contact",
        "NAV_SWITCH": "中文",
        "I18N_METHODS": "Methods",
        "I18N_QUESTIONNAIRE": "Questionnaire & Coding",  # ✅ 新增标签
        "I18N_PUBLICATIONS": "Publications",
        "I18N_CONTACT": "Contact",
        "I18N_OR": "",
        "I18N_APPENDIX": "Appendix (Questionnaire PDF)",
        "LEAD_HOME": "Datasets released by Professor Jinghua Li Laboratory",
        "SECTION_TITLE": "Databases",
        "BTN_OPEN": "Open Details Page",
        "LANG_SUFFIX": "en",
        "ALT_LANG_SUFFIX": "zh"
    }

def force_footer(html_text: str, year: int, owner: str, affiliation: str, license_text: str=None) -> str:
    """强制覆盖 footer 小字"""
    if license_text:
        new_small = f"<small>© {year} {owner} · {affiliation} · License: {license_text} · All Rights Reserved</small>"
    else:
        new_small = f"<small>© {year} {owner} · {affiliation} · All Rights Reserved</small>"
    return re.sub(r"<small>.*?</small>", new_small, html_text, count=1, flags=re.S)

def build_dataset_page(site, ds, lang):
    L = i18n_labels(lang)
    html_out = TPL_DETAIL

    site_title = site.get("site_title_en") if lang == "en" else site.get("site_title", CN_LAB_TITLE)
    owner_text = site.get("owner_en") if lang == "en" else site.get("owner_zh", site.get("owner", ""))
    affiliation_text = site.get("affiliation_en") if lang == "en" else site.get("affiliation_zh", site.get("affiliation", ""))

    html_out = html_out.replace("{{LANG_ATTR}}", L["LANG_ATTR"])
    html_out = html_out.replace("{{SITE_TITLE}}", esc(site_title))
    html_out = html_out.replace("{{NAV_HOME}}", L["NAV_HOME"])
    html_out = html_out.replace("{{NAV_CONTACT}}", L["NAV_CONTACT"])
    html_out = html_out.replace("{{NAV_SWITCH}}", L["NAV_SWITCH"])
    html_out = html_out.replace("{{LANG_SUFFIX}}", L["LANG_SUFFIX"])
    html_out = html_out.replace("{{ALT_LANG_SUFFIX}}", L["ALT_LANG_SUFFIX"])
    html_out = html_out.replace("{{CONTACT_HREF}}", "../contact-en.html" if lang == "en" else "../contact.html")

    html_out = html_out.replace("{{DATASET_TITLE}}", esc(ds.get("title", "")))
    html_out = html_out.replace("{{SUMMARY}}", esc(ds.get("summary", "")))
    html_out = html_out.replace("{{I18N_METHODS}}", L["I18N_METHODS"])
    html_out = html_out.replace("{{I18N_QUESTIONNAIRE}}", L["I18N_QUESTIONNAIRE"])  # ✅ 新增标签替换
    html_out = html_out.replace("{{I18N_PUBLICATIONS}}", L["I18N_PUBLICATIONS"])
    html_out = html_out.replace("{{I18N_CONTACT}}", L["I18N_CONTACT"])
    html_out = html_out.replace("{{I18N_OR}}", L["I18N_OR"])
    html_out = html_out.replace("{{I18N_APPENDIX}}", L["I18N_APPENDIX"])
    html_out = html_out.replace("{{METHODS_HTML}}", ds.get("methods_html", ""))
    html_out = html_out.replace("{{QUESTIONNAIRE_HTML}}", ds.get("questionnaire_html", ""))  # ✅ 新增插入行
    # 关键：这里传入 lang，摘要标签中英文自动切换，并且摘要内容跳过实体化
    html_out = html_out.replace("{{PUBLICATIONS_LIST}}", render_publications_with_abstracts(ds.get("publications", []), lang))
    # 联系方式正文保留文字（转义），不再追加任何 mailto 行
    html_out = html_out.replace("{{CONTACT_TEXT}}", f"<p>{esc(ds.get('contact', ''))}</p>")
    html_out = html_out.replace("{{APPENDIX_HTML}}", ds.get("appendix_html", ""))
    html_out = html_out.replace("{{CONTACT_EMAIL}}", esc(site.get("contact_email", "")))
    html_out = html_out.replace("{{JSONLD}}", build_jsonld(site, ds, lang))

    # 覆盖页脚
    html_out = force_footer(html_out, datetime.now().year, esc(owner_text), esc(affiliation_text), esc(site.get("license","")))

    # 关键：移除模板里残留的 mailto 段并清空空<p>
    html_out = strip_mailto_paragraphs(html_out)

    # 实体化，杜绝乱码（摘要段落已通过 NO_ENTITY 跳过）
    html_out = finalize_html(html_out)

    OUT_DATASETS.mkdir(parents=True, exist_ok=True)
    (OUT_DATASETS / f"{ds['slug']}-{lang}.html").write_text(html_out, encoding="utf-8")
    print(f"[OK] {ds['slug']}-{lang}.html")

def build_index(site, datasets, lang):
    L = i18n_labels(lang)
    html_out = TPL_INDEX

    site_title = site.get("site_title_en") if lang == "en" else site.get("site_title", CN_LAB_TITLE)
    owner_text = site.get("owner_en") if lang == "en" else site.get("owner_zh", site.get("owner", ""))
    affiliation_text = site.get("affiliation_en") if lang == "en" else site.get("affiliation_zh", site.get("affiliation", ""))
    contact_person = site.get("contact_person_en") if lang == "en" else site.get("contact_person_zh", site.get("contact_person_en", ""))
    contact_affiliation = site.get("contact_affiliation_en") if lang == "en" else site.get("contact_affiliation_zh", site.get("contact_affiliation_en", ""))
    contact_email = site.get("contact_email", "")

    html_out = html_out.replace("{{LANG_ATTR}}", L["LANG_ATTR"])
    html_out = html_out.replace("{{SITE_TITLE}}", esc(site_title))
    html_out = html_out.replace("{{NAV_HOME}}", L["NAV_HOME"])
    html_out = html_out.replace("{{NAV_CONTACT}}", L["NAV_CONTACT"])
    html_out = html_out.replace("{{NAV_SWITCH}}", L["NAV_SWITCH"])
    html_out = html_out.replace("{{LANG_SUFFIX}}", L["LANG_SUFFIX"])
    html_out = html_out.replace("{{ALT_LANG_SUFFIX}}", L["ALT_LANG_SUFFIX"])
    html_out = html_out.replace("{{CONTACT_HREF}}", "contact-en.html" if lang == "en" else "contact.html")

    page_title = site_title if lang == "zh" else site.get("site_title_en", site_title)
    html_out = html_out.replace("{{PAGE_TITLE}}", page_title)
    html_out = html_out.replace("{{LEAD}}", L["LEAD_HOME"])

    if contact_email:
        if lang == "zh":
            contact_note = f"数据管理员：{contact_person or owner_text}（{contact_affiliation or affiliation_text}）。邮箱：{contact_email}"
        else:
            contact_note = f"Data administrator: {contact_person or owner_text} ({contact_affiliation or affiliation_text}). Email: {contact_email}"
    else:
        contact_note = ""
    html_out = html_out.replace("{{HOME_CONTACT}}", esc(contact_note))
    html_out = html_out.replace("{{SECTION_TITLE}}", L["SECTION_TITLE"])

    cards = []
    for d in datasets:
        cards.append(
            "<section class='dataset-card'>"
            f"<h3>{esc(d.get('title',''))}</h3>"
            f"<p>{esc(d.get('summary',''))}</p>"
            f"<a class='btn' href='datasets/{d['slug']}-{lang}.html'>{L['BTN_OPEN']}</a>"
            "</section>"
        )
    html_out = html_out.replace("{{DATASET_LIST}}", "\n".join(cards))

    # 页脚 & 实体化
    html_out = force_footer(html_out, datetime.now().year, esc(owner_text), esc(affiliation_text))
    html_out = finalize_html(html_out)

    (ROOT / f"index-{lang}.html").write_text(html_out, encoding="utf-8")
    print(f"[OK] index-{lang}.html")

def main():
    site = json.loads((DATA_DIR / "site.json").read_text(encoding="utf-8"))
    for lang in ["zh","en"]:
        df = DATA_DIR / f"datasets-{lang}.json"
        if not df.exists():
            print(f"[WARN] Missing {df}")
            continue
        datasets = json.loads(df.read_text(encoding="utf-8"))
        for ds in datasets:
            build_dataset_page(site, ds, lang)
        build_index(site, datasets, lang)
    print("✅ All pages built successfully.")

if __name__ == "__main__":
    main()
