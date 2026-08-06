#!/usr/bin/env python3
"""
Generate HTML files for arte-02 (1080x1350) for kit-master-flex.
Applies design system from brand/design-system-conexao.json via aplicador-marca-conexao.
"""
import json
import shutil
from pathlib import Path

# Configuration
SLUG = "kit-master-flex"
VARIANTE = "arte-02"
LARGURA, ALTURA = 1080, 1350

# Paths
DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output" / SLUG
DIR_ARTE = DIR_OUTPUT / VARIANTE
TEMPLATE_PATH = DIR_PROJETO / "templates" / f"arte-{LARGURA}x{ALTURA}.html"
COPIES_PATH = DIR_OUTPUT / "arte" / "copies.json"
CONFIG_PATH = DIR_OUTPUT / "config_projeto.json"
IMAGES_PATH = DIR_OUTPUT / "insumos"

# Load data
with open(COPIES_PATH, 'r', encoding='utf-8') as f:
    copies_data = json.load(f)

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Get image path
image_info = config.get("imagens", [{}])[0]
image_filename = Path(image_info.get("path", "")).name
image_src = f"../insumos/{image_filename}"

# Load template
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    template = f.read()

# Generate HTML for each copy
for idx, copy in enumerate(copies_data["copies"], start=1):
    copy_id = copy["id"]
    headline = copy["headline"]
    subcopy = copy["subcopy"]
    cta = copy["cta"]
    
    # Create headline spans (one per word)
    headline_spans = ""
    for word in headline.split():
        headline_spans += f'<span class="palavra">{word}</span> '
    
    # Replace placeholders in template
    html = template.replace("{{FORMA_DECORATIVA}}", "")
    html = html.replace("{{LOGO}}", f'<img class="logo" src="assets/logos/Logo_Conexão_horizontal_texto_branco.png" alt="Conexão Implantes">')
    html = html.replace("{{IMAGEM_PRODUTO}}", f'<img class="produto" src="{image_src}" alt="Kit Master Flex">')
    html = html.replace("{{HEADLINE}}", f'<h1>{headline_spans}</h1>')
    html = html.replace("{{SUBCOPY}}", f'<p class="subcopy">{subcopy}</p>')
    html = html.replace("{{CTA}}", f'<span class="cta">{cta}</span>')
    html = html.replace("{{BADGE_CONTEXTO}}", '<span class="badge">USO INTERNO</span>')
    
    # Determine filename
    if idx == 1:
        filename = "index.html"
    else:
        filename = f"index_copy0{idx}.html"
    
    # Write HTML
    output_path = DIR_ARTE / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated: {output_path}")

print("HTML generation complete.")