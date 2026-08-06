#!/usr/bin/env python3
"""
Render arte-02 (1080x1350) HTML files to PNG using Playwright.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configuration
SLUG = "kit-master-flex"
VARIANTE = "arte-02"
LARGURA, ALTURA = 1080, 1350

# Paths
DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output" / SLUG
DIR_ARTE = DIR_OUTPUT / VARIANTE

# Load copies to get filenames
COPIES_PATH = DIR_OUTPUT / "arte" / "copies.json"
with open(COPIES_PATH, 'r', encoding='utf-8') as f:
    copies = json.load(f)["copies"]

# HTML files to render
html_files = [
    DIR_ARTE / "index.html",  # copy-01
    DIR_ARTE / "index_copy02.html",  # copy-02
    DIR_ARTE / "index_copy03.html",  # copy-03
]

# Render with Playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    
    for idx, html_file in enumerate(html_files, start=1):
        copy = copies[idx-1]
        copy_id = copy["id"]
        
        # Create page with exact dimensions
        page = browser.new_page(viewport={"width": LARGURA, "height": ALTURA})
        
        # Navigate to HTML file
        page.goto(f"file:///{html_file.resolve()}")
        
        # Wait for fonts and layout
        page.wait_for_timeout(500)
        
        # Screenshot
        png_path = DIR_ARTE / f"arte_{SLUG}_02_copy0{idx}.png"
        page.screenshot(path=str(png_path), full_page=False)
        
        print(f"Rendered: {png_path}")
        page.close()
    
    browser.close()

print("Rendering complete.")