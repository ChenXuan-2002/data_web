# -*- coding: utf-8 -*-
import json, csv, re, html
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TEMPLATES = ROOT / "templates"
OUT_DIR = ROOT / "datasets"
CSV_DIR = ROOT / "assets" / "variables"

def slugify(s, fallback):
    if not s: return fallback
    s = s.strip().lower()
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'[^a-z0-9\-]+', '', s)  # 仅保留 a-z0-9-，中文需手动提供 slug
    return s or fallback

def render_variables_table(vars_list):
    # 转 HTML 表格
    head = """<table data-kind="vars" aria-label="变量字典">
<thead><tr>
  <th class="sortable">变量名</th>
  <th class="sortable">中文名</th>
  <th>单位</th>
  <th class="sortable">类型</th>
  <th>取值范围</th>
  <th>说明</th>
</tr></thead><tbody>"""
    rows = []
    for v in vars_list:
        rows.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(v.get("name","")),
            html.escape(v.get("label","")),
            html.escape(v.get("unit","")),
            html.escape(v.get("type","")),
            html.escape(v.get("allowed_values","")),
            html.escape(v.get("description",""))
        ))
    return head + "\n".join(rows) + "</tbody></table>"

def render_publications(pubs):
    items = []
    for p in pubs:
        authors = html.escape(p.get("authors",""))
        year = str(p.get("year","")).strip()
        title = html.escape(p.get("title",""))
        venue = html.escape(p.get("venue",""))
        doi = (p.get("doi") or "").strip()
        url = (p.get("url") or "").strip()
        link = ""
        if doi:
            link = f'<a href="https://doi.org/{html.escape(doi)}" target="_blank" rel="noopener">DOI:{html.escape(doi)}</a>'
        elif url:
            link = f'<a href="{html.escape(url)}" target="_blank" rel="noopener">链接</a>'
        item = f"<li>{authors} ({year}). <em>{title}</em>. {venue}. {link}</li>"
        items.append(item)
    return "\n".join(items) if items else "<li>暂无公开论文。</li>"

def build_jsonld(site, ds):
    # schema.org/Dataset
    props = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": ds["title"],
        "description": (ds.get("summary") or "")[:300],
        "creator": {"@type": "Organization", "name": site.get("owner","")},
        "publisher": {"@type": "Organization", "name": site.get("affiliation","")},
        "license": site.get("license",""),
        "url": f"./{ds['slug']}.html",
        "variableMeasured": [
            {
                "@type": "PropertyValue",
                "name": v.get("name",""),
                "description": v.get("label",""),
                "unitText": v.get("unit","")
            } for v in ds.get("variables", [])
        ]
    }
    return json.dumps(props, ensure_ascii=False, indent=2)

def write_csv(path, vars_list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline='', encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name","label","unit","type","allowed_values","description"])
        for v in vars_list:
            w.writerow([
                v.get("name",""), v.get("label",""), v.get("unit",""),
                v.get("type",""), v.get("allowed_values",""), v.get("description","")
            ])

def main():
    site = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
    datasets = json.loads((DATA / "datasets.json").read_text(encoding="utf-8"))
    tpl = (TEMPLATES / "dataset_page.html").read_text(encoding="utf-8")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for i, ds in enumerate(datasets, start=1):
        slug = ds.get("slug") or slugify(ds.get("title",""), f"dataset-{i}")
        ds["slug"] = slug

        # 导出变量 CSV
        write_csv(CSV_DIR / f"{slug}.csv", ds.get("variables", []))

        # 组装 HTML
        html_out = tpl
        html_out = html_out.replace("{{DATASET_TITLE}}", html.escape(ds.get("title","")))
        html_out = html_out.replace("{{SITE_TITLE}}", html.escape(site.get("site_title","")))
        html_out = html_out.replace("{{SUMMARY}}", html.escape(ds.get("summary","")))
        html_out = html_out.replace("{{METHODS_HTML}}", ds.get("methods_html",""))
        html_out = html_out.replace("{{VARIABLES_TABLE}}", render_variables_table(ds.get("variables", [])))
        html_out = html_out.replace("{{PUBLICATIONS_LIST}}", render_publications(ds.get("publications", [])))
        html_out = html_out.replace("{{CONTACT_EMAIL}}", html.escape(site.get("contact_email","")))
        html_out = html_out.replace("{{LICENSE}}", html.escape(site.get("license","")))
        html_out = html_out.replace("{{OWNER}}", html.escape(site.get("owner","")))
        html_out = html_out.replace("{{AFFILIATION}}", html.escape(site.get("affiliation","")))
        html_out = html_out.replace("{{YEAR}}", str(datetime.now().year))
        html_out = html_out.replace("{{SLUG}}", slug)
        html_out = html_out.replace("{{JSONLD}}", build_jsonld(site, ds))

        # 写入文件
        (OUT_DIR / f"{slug}.html").write_text(html_out, encoding="utf-8")

    print(f"生成完成：{len(datasets)} 个页面，CSV 输出目录：{CSV_DIR}")

if __name__ == "__main__":
    main()
