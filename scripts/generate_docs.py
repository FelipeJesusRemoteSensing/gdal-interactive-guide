"""
generate_docs.py
================
Reads the existing JSON databases (gdal_database.json and gdal_cpp_database.json)
and generates MkDocs Markdown pages for:
  1. Subsection pages (raster.md, vetor.md, informacao.md, utilitario.md)
  2. C++ explorer pages (apps.md, drivers.md)
"""

import json
import os
import sys

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MKDOCS_ROOT = os.path.dirname(SCRIPT_DIR)
STREAMLIT_DIR = os.path.join(os.path.dirname(MKDOCS_ROOT), "streamlit_app")

DB_PATH = os.path.join(STREAMLIT_DIR, "gdal_database.json")
CPP_DB_PATH = os.path.join(STREAMLIT_DIR, "gdal_cpp_database.json")

DOCS_DIR = os.path.join(MKDOCS_ROOT, "docs")
SUBSECOES_DIR = os.path.join(DOCS_DIR, "subsecoes")
CPP_DIR = os.path.join(DOCS_DIR, "cpp")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def escape_md(text):
    """Escape characters that might break markdown rendering."""
    if not text:
        return ""
    return text.replace("<", "&lt;").replace(">", "&gt;")


def get_badge_class(category):
    cat = category.lower()
    if "raster" in cat:
        return "badge-raster", "Raster"
    elif "vetor" in cat or "vector" in cat:
        return "badge-vetor", "Vetor"
    elif "info" in cat or "informação" in cat:
        return "badge-info", "Informação"
    else:
        return "badge-util", "Utilitário"


# ====================================================================
# 1. GENERATE SUBSECTION PAGES (operators by category)
# ====================================================================
def generate_subsection_pages():
    print("Loading gdal_database.json...")
    db = load_json(DB_PATH)
    operators = db.get("operators", [])
    print(f"  Found {len(operators)} operators")

    # Map categories
    category_map = {
        "Raster": {
            "filename": "raster.md",
            "title": "🗺️ Comandos Raster",
            "icon": "🗺️",
            "desc": "Comandos para processamento de imagens matriciais (raster): conversão, reprojeção, recorte, mosaico, DEM, estatísticas e mais.",
            "operators": [],
        },
        "Vetor": {
            "filename": "vetor.md",
            "title": "📐 Comandos Vetor",
            "icon": "📐",
            "desc": "Comandos para processamento de dados vetoriais: conversão, buffer, dissolve, overlay, reprojeção e validação de geometrias.",
            "operators": [],
        },
        "Informação": {
            "filename": "informacao.md",
            "title": "🔍 Comandos de Informação",
            "icon": "🔍",
            "desc": "Comandos para inspeção e extração de metadados: gdalinfo, ogrinfo, gdalsrsinfo e verificações de dataset.",
            "operators": [],
        },
        "Utilitário": {
            "filename": "utilitario.md",
            "title": "🔧 Comandos Utilitários",
            "icon": "🔧",
            "desc": "Comandos utilitários auxiliares do ecossistema GDAL.",
            "operators": [],
        },
    }

    # Sort operators into categories
    for op in operators:
        cat = op.get("category", "Utilitário")
        # Handle encoding issues with "Informação"
        if cat not in category_map:
            # Try matching by substring
            matched = False
            for key in category_map:
                if key.lower() in cat.lower() or cat.lower() in key.lower():
                    category_map[key]["operators"].append(op)
                    matched = True
                    break
            if not matched:
                category_map["Utilitário"]["operators"].append(op)
        else:
            category_map[cat]["operators"].append(op)

    # Generate each category page
    os.makedirs(SUBSECOES_DIR, exist_ok=True)

    for cat_name, cat_data in category_map.items():
        ops = sorted(cat_data["operators"], key=lambda x: x["name"])
        badge_class, badge_label = get_badge_class(cat_name)

        lines = []
        lines.append(f"# {cat_data['title']}\n")
        lines.append(f"{cat_data['desc']}\n")
        lines.append(f"**Total:** {len(ops)} comandos\n")
        lines.append("---\n")

        for op in ops:
            name = op.get("name", "Sem nome")
            desc = escape_md(op.get("description", ""))
            keywords = op.get("keywords", [])
            examples = op.get("examples", [])

            # Collapsible block for each operator
            lines.append(f'??? note "{name}"')
            lines.append("")
            lines.append(f"    <span class=\"badge {badge_class}\">{badge_label}</span>\n")
            lines.append(f"    {desc}\n")

            if keywords:
                tags_html = " ".join(
                    [f'<span class="tag">{k}</span>' for k in keywords[:12]]
                )
                lines.append(f"    **Keywords:** {tags_html}\n")

            if examples:
                for ex in examples:
                    title = ex.get("title", "Exemplo")
                    code = ex.get("code", "")
                    lang = ex.get("lang", "bash")
                    if code and code.strip():
                        lines.append(f"    **{escape_md(title)}**\n")
                        lines.append(f"    ```{lang}")
                        for code_line in code.split("\n"):
                            lines.append(f"    {code_line}")
                        lines.append(f"    ```\n")

            lines.append("")

        filepath = os.path.join(SUBSECOES_DIR, cat_data["filename"])
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  Generated {cat_data['filename']} ({len(ops)} operators)")


# ====================================================================
# 2. GENERATE C++ EXPLORER PAGES
# ====================================================================
def generate_cpp_pages():
    print("Loading gdal_cpp_database.json...")
    cpp_db = load_json(CPP_DB_PATH)
    print(f"  Found {len(cpp_db)} C++ files")

    os.makedirs(CPP_DIR, exist_ok=True)

    # Separate into apps and drivers
    apps_files = []
    driver_files = []

    for entry in cpp_db:
        if "apps" in entry.get("path", "").lower():
            apps_files.append(entry)
        else:
            driver_files.append(entry)

    apps_files.sort(key=lambda x: x["name"])
    driver_files.sort(key=lambda x: x["name"])

    # --- Generate apps.md ---
    lines = []
    lines.append("# ⚙️ Aplicativos (gdal/apps)\n")
    lines.append(
        "Código-fonte completo dos utilitários de produção do GDAL. "
        "Estes são os programas executáveis que implementam `gdalinfo`, `gdalwarp`, "
        "`gdal_translate`, `ogr2ogr` e muitos outros.\n"
    )
    lines.append(f"**Total:** {len(apps_files)} arquivos\n")
    lines.append("---\n")

    for entry in apps_files:
        name = entry["name"]
        path = entry.get("path", "")
        code = entry.get("code", "")
        # Determine language from extension
        lang = "cpp" if name.endswith(".cpp") else "c" if name.endswith(".c") else "cpp"
        if name.endswith(".h"):
            lang = "cpp"

        lines.append(f'??? example "{name}"')
        lines.append("")
        lines.append(
            f'    <span class="badge badge-cpp">gdal/apps</span> '
            f'**Caminho:** `{path}`\n'
        )
        lines.append(f"    ```{lang}")
        for code_line in code.split("\n"):
            lines.append(f"    {code_line}")
        lines.append(f"    ```\n")
        lines.append("")

    filepath = os.path.join(CPP_DIR, "apps.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Generated apps.md ({len(apps_files)} files)")

    # --- Generate drivers.md ---
    lines = []
    lines.append("# 🔌 Drivers (gdal/frmts)\n")
    lines.append(
        "Código-fonte de drivers de formato selecionados do repositório GDAL. "
        "Estes são modelos reais de como implementar drivers para novos formatos "
        "de dados geoespaciais.\n"
    )
    lines.append(f"**Total:** {len(driver_files)} arquivos\n")
    lines.append("---\n")

    # Group by driver folder
    driver_groups = {}
    for entry in driver_files:
        cat = entry.get("category", "Outros")
        if cat not in driver_groups:
            driver_groups[cat] = []
        driver_groups[cat].append(entry)

    for group_name, files in sorted(driver_groups.items()):
        lines.append(f"## {group_name}\n")
        for entry in files:
            name = entry["name"]
            path = entry.get("path", "")
            code = entry.get("code", "")
            lang = "cpp" if name.endswith((".cpp", ".h")) else "cpp"

            lines.append(f'??? example "{name}"')
            lines.append("")
            lines.append(
                f'    <span class="badge badge-cpp">{group_name}</span> '
                f'**Caminho:** `{path}`\n'
            )
            lines.append(f"    ```{lang}")
            for code_line in code.split("\n"):
                lines.append(f"    {code_line}")
            lines.append(f"    ```\n")
            lines.append("")

    filepath = os.path.join(CPP_DIR, "drivers.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Generated drivers.md ({len(driver_files)} files)")


# ====================================================================
# MAIN
# ====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("GDAL MkDocs — Gerador de Páginas de Documentação")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"ERRO: Banco de dados não encontrado: {DB_PATH}")
        sys.exit(1)
    if not os.path.exists(CPP_DB_PATH):
        print(f"ERRO: Banco de dados C++ não encontrado: {CPP_DB_PATH}")
        sys.exit(1)

    generate_subsection_pages()
    generate_cpp_pages()

    print("\n✅ Todas as páginas geradas com sucesso!")
