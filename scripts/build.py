# -*- coding: utf-8 -*-
import json, html
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TPL_DIR = ROOT / "templates"
OUT_DATASETS = ROOT / "datasets"

# Templates
TPL_DETAIL = (TPL_DIR / "dataset_page.html").read_text(encoding="utf-8")
TPL_INDEX  = (TPL_DIR / "index_page.html").read_text(encoding="utf-8")

def esc(x): return html.escape(x or "")

def render_publications_with_abstracts(pubs):
    """Render publication list with full abstracts."""
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
        abstract = p.get("abstract","")
        # Keep raw abstract text; preserve punctuation; minimal sanitisation
        abstract_html = f"<p><strong>Abstract:</strong> {abstract}</p>" if abstract else ""
        li = f"<li><p><strong>{authors}</strong> ({year}). <em>{title}</em>. {venue}. {link}</p>{abstract_html}</li>"
        items.append(li)
    return "\n".join(items) if items else "<li>-</li>"

def build_jsonld(site, ds, lang):
    """Build schema.org Dataset JSON-LD block."""
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
        "variableMeasured": []  # TODO: populate variables list when available
    }
    return json.dumps(props, ensure_ascii=False, indent=2)

def i18n_labels(lang):
    if lang == "zh":
        return {
            "LANG_ATTR": "zh-CN",
            "NAV_HOME": "首页",
            "NAV_CONTACT": "联系方式/申请",
            "NAV_SWITCH": "English",
            "I18N_METHODS": "实验方法",
            "I18N_PUBLICATIONS": "已发表论文",
            "I18N_CONTACT": "联系方式",
            "I18N_OR": "或直接邮件联系",
            "I18N_APPENDIX": "附录（问卷 PDF）",
            "LEAD_HOME": "以下为 XX 实验室公开的数据库",
            "SECTION_TITLE": "数据库列表",
            "BTN_OPEN": "打开详情页",
            "LANG_SUFFIX": "zh",
            "ALT_LANG_SUFFIX": "en"
        }
    else:
        return {
            "LANG_ATTR": "en",
            "NAV_HOME": "Home",
            "NAV_CONTACT": "Contact",
            "NAV_SWITCH": "中文",
            "I18N_METHODS": "Methods",
            "I18N_PUBLICATIONS": "Publications",
            "I18N_CONTACT": "Contact",
            "I18N_OR": "or contact via email",
            "I18N_APPENDIX": "Appendix (Questionnaire PDF)",
            "LEAD_HOME": "List of databases released by XX Laboratory",
            "SECTION_TITLE": "Databases",
            "BTN_OPEN": "Open Details Page",
            "LANG_SUFFIX": "en",
            "ALT_LANG_SUFFIX": "zh"
        }

def build_dataset_page(site, ds, lang):
    L = i18n_labels(lang)
    html_out = TPL_DETAIL

    # Header and navigation slot replacements
    html_out = html_out.replace("{{LANG_ATTR}}", L["LANG_ATTR"])
    html_out = html_out.replace("{{SITE_TITLE}}", esc(site.get("site_title","XX实验室数据库")))
    html_out = html_out.replace("{{NAV_HOME}}", L["NAV_HOME"])
    html_out = html_out.replace("{{NAV_CONTACT}}", L["NAV_CONTACT"])
    html_out = html_out.replace("{{NAV_SWITCH}}", L["NAV_SWITCH"])
    html_out = html_out.replace("{{LANG_SUFFIX}}", L["LANG_SUFFIX"])
    html_out = html_out.replace("{{ALT_LANG_SUFFIX}}", L["ALT_LANG_SUFFIX"])
    contact_href = "../contact-en.html" if lang == "en" else "../contact.html"
    html_out = html_out.replace("{{CONTACT_HREF}}", contact_href)

    # Dataset metadata strings
    html_out = html_out.replace("{{DATASET_TITLE}}", esc(ds.get("title","")))
    html_out = html_out.replace("{{SUMMARY}}", esc(ds.get("summary","")))
    html_out = html_out.replace("{{I18N_METHODS}}", L["I18N_METHODS"])
    html_out = html_out.replace("{{I18N_PUBLICATIONS}}", L["I18N_PUBLICATIONS"])
    html_out = html_out.replace("{{I18N_CONTACT}}", L["I18N_CONTACT"])
    html_out = html_out.replace("{{I18N_OR}}", L["I18N_OR"])
    html_out = html_out.replace("{{I18N_APPENDIX}}", L["I18N_APPENDIX"])

    # Inline HTML fragments from dataset json
    html_out = html_out.replace("{{METHODS_HTML}}", ds.get("methods_html",""))
    html_out = html_out.replace("{{PUBLICATIONS_LIST}}", render_publications_with_abstracts(ds.get("publications",[])))
    html_out = html_out.replace("{{CONTACT_TEXT}}", f"<p>{esc(ds.get('contact',''))}</p>")
    html_out = html_out.replace("{{APPENDIX_HTML}}", ds.get("appendix_html",""))

    # Site-wide attributes
    html_out = html_out.replace("{{CONTACT_EMAIL}}", esc(site.get("contact_email","")))
    html_out = html_out.replace("{{LICENSE}}", esc(site.get("license","")))
    html_out = html_out.replace("{{OWNER}}", esc(site.get("owner","")))
    html_out = html_out.replace("{{AFFILIATION}}", esc(site.get("affiliation","")))
    html_out = html_out.replace("{{YEAR}}", str(datetime.now().year))

    # JSON-LD
    jsonld = build_jsonld(site, ds, lang)
    html_out = html_out.replace("{{JSONLD}}", jsonld)

    # Write dataset page to disk
    OUT_DATASETS.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DATASETS / f"{ds['slug']}-{lang}.html"
    out_file.write_text(html_out, encoding="utf-8")
    print(f"[OK] {out_file.relative_to(ROOT)}")

def build_index(site, datasets, lang):
    L = i18n_labels(lang)
    html_out = TPL_INDEX
    html_out = html_out.replace("{{LANG_ATTR}}", L["LANG_ATTR"])
    html_out = html_out.replace("{{SITE_TITLE}}", esc(site.get("site_title","XX实验室数据库")))
    html_out = html_out.replace("{{NAV_HOME}}", L["NAV_HOME"])
    html_out = html_out.replace("{{NAV_CONTACT}}", L["NAV_CONTACT"])
    html_out = html_out.replace("{{NAV_SWITCH}}", L["NAV_SWITCH"])
    html_out = html_out.replace("{{LANG_SUFFIX}}", L["LANG_SUFFIX"])
    html_out = html_out.replace("{{ALT_LANG_SUFFIX}}", L["ALT_LANG_SUFFIX"])
    contact_href = "contact-en.html" if lang == "en" else "contact.html"
    html_out = html_out.replace("{{CONTACT_HREF}}", contact_href)

    page_title = "XX实验室数据库（中文）" if lang == "zh" else "XX Laboratory Databases (English)"
    html_out = html_out.replace("{{PAGE_TITLE}}", page_title)
    html_out = html_out.replace("{{LEAD}}", L["LEAD_HOME"])
    html_out = html_out.replace("{{SECTION_TITLE}}", L["SECTION_TITLE"])

    # Render dataset cards for index page
    cards = []
    for d in datasets:
        card = (
            "<div class='dataset-card'>"
            f"<h3>{esc(d.get('title',''))}</h3>"
            f"<p>{esc(d.get('summary',''))}</p>"
            f"<a class='btn' href='datasets/{d['slug']}-{lang}.html'>{L['BTN_OPEN']}</a>"
            "</div>"
        )
        cards.append(card)
    html_out = html_out.replace("{{DATASET_LIST}}", "\n".join(cards))

    out_file = ROOT / f"index-{lang}.html"
    out_file.write_text(html_out, encoding="utf-8")
    print(f"[OK] {out_file.relative_to(ROOT)}")

def main():
    site = json.loads((DATA_DIR / "site.json").read_text(encoding="utf-8"))

    # Build Chinese then English pages
    for lang in ["zh","en"]:
        data_file = DATA_DIR / f"datasets-{lang}.json"
        if not data_file.exists():
            print(f"[WARN] Missing {data_file}")
            continue
        datasets = json.loads(data_file.read_text(encoding="utf-8"))
        for ds in datasets:
            # Basic field validation
            if "slug" not in ds or not ds["slug"]:
                raise RuntimeError(f"dataset missing slug: {ds}")
            build_dataset_page(site, ds, lang)
        build_index(site, datasets, lang)

    print("All pages built successfully.")

if __name__ == "__main__":
    main()
