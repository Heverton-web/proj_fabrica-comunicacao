#!/usr/bin/env python3
"""
Compilador de Kit do Consultor / Kit Distribuidor: renderiza as 10 copies
compartilhadas de output/<slug>/kits/copies.json em PNGs 1080x1350 (5 tons x
2 itens) para a variante de kit pedida, aplicando o CTA/assinatura fixos de
brand/kits-conexao.json e escrevendo o texto_whatsapp.txt de cada item.

Reaproveita a tecnica de renderizacao compartilhada em scripts/_arte_common.py
(mesmo helper usado por compilar-arte.py) -- ver SPEC_KITS.md.

Uso:
    python scripts/compilar-kit.py <slug> --kit kit-consultor
    python scripts/compilar-kit.py <slug> --kit kit-distribuidor
    python scripts/compilar-kit.py <slug> --kit ambos
"""

import argparse
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _arte_common import (
    DIR_OUTPUT, DIR_PROJETO, carregar_json, preparar_assets, resolver_badge,
    preencher_template, renderizar_pagina, escolher_decoracao_fundo,
    gerar_forma_decorativa_html,
)

LARGURA, ALTURA = 1080, 1350

TOM_PASTA = {
    "informativa": "artes-informativas",
    "contra-intuitiva": "artes-contra-intuitivas",
    "tecnica": "artes-tecnicas",
    "efeito-uau": "artes-efeito-uau",
    "educativa": "artes-educativas",
}
TONS_ORDENADOS = ["informativa", "contra-intuitiva", "tecnica", "efeito-uau", "educativa"]

# Gancho curto por tom (emoji + frase de abertura) para "causar" -- gera curiosidade
# antes do headline, sem inventar claim novo (framing generico, nao dado de produto).
TOM_GANCHO = {
    "informativa": ("\U0001F4CC", "Direto ao ponto:"),
    "contra-intuitiva": ("\U0001F914", "Você sabia?"),
    "tecnica": ("\U0001F527", "Detalhe técnico que faz diferença:"),
    "efeito-uau": ("\U0001F92F", "Isso pode te surpreender:"),
    "educativa": ("\U0001F4DA", "Você sabe por quê?"),
}

VARIANTES_VALIDAS = ("kit-consultor", "kit-distribuidor")


def montar_texto_whatsapp(tom, headline, subcopy, cta, assinatura):
    """Mensagem curta pronta para WhatsApp: gancho por tom (causa curiosidade) +
    headline em negrito + subcopy como bullet point + CTA comercial em destaque +
    assinatura em italico. Montagem deterministica (sem 2a chamada de LLM) a partir
    da copy compartilhada + brand/kits-conexao.json -- ver SPEC_KITS.md."""
    emoji, gancho = TOM_GANCHO.get(tom, ("\U0001F4AC", ""))
    partes = []
    if gancho:
        partes.append(f"{emoji} _{gancho}_")
    partes.append(f"*{headline}*")
    partes.append(f"▪️ {subcopy}")
    partes.append(f"\U0001F449 *{cta}*")
    partes.append(f"_{assinatura}_")
    return "\n\n".join(partes) + "\n"


def compilar_kit(slug, kit_variante, pasta=None):
    """`pasta` e a pasta real de destino em output/<slug>/ -- normalmente igual a
    `kit_variante`, mas pode ser uma versao regenerada (ex.: "kit-consultor-v2")
    por /gerar-kit-consultor -- ver REGRA 11 do AGENTS.md. `kit_variante`
    continua sendo a variante BASE (define CTA/assinatura fixos)."""
    if kit_variante not in VARIANTES_VALIDAS:
        print(f"[ERRO] variante de kit desconhecida: {kit_variante!r}")
        return 1
    pasta = pasta or kit_variante

    slug_dir = DIR_OUTPUT / slug
    copies_path = slug_dir / "kits" / "copies.json"
    config_kits_path = DIR_PROJETO / "brand" / "kits-conexao.json"
    template_path = DIR_PROJETO / "templates" / f"arte-{LARGURA}x{ALTURA}.html"

    if not copies_path.exists():
        print(f"[ERRO] {copies_path} nao encontrado -- redator-kit-copy deve gerar as "
              f"10 copies compartilhadas ANTES de compilar qualquer variante de kit")
        return 1
    if not config_kits_path.exists():
        print(f"[ERRO] {config_kits_path} nao encontrado (config fixa de CTA/assinatura por kit)")
        return 1
    if not template_path.exists():
        print(f"[ERRO] template nao encontrado: {template_path}")
        return 1

    dados_copies = carregar_json(copies_path)
    if not isinstance(dados_copies, dict):
        print(f"[ERRO] {copies_path} nao contem um objeto JSON valido")
        return 1
    copies = dados_copies.get("copies", [])
    if len(copies) != 10:
        print(f"[ERRO] {copies_path} deve conter exatamente 10 copies, encontrado {len(copies)}")
        return 1

    config_kits = carregar_json(config_kits_path)
    variante_cfg = (config_kits or {}).get("variantes", {}).get(kit_variante)
    if not variante_cfg:
        print(f"[ERRO] variante '{kit_variante}' nao encontrada em {config_kits_path}")
        return 1
    cta = variante_cfg.get("cta_padrao", "Fale com a Conexão")
    assinatura = variante_cfg.get("assinatura", "Conexão")

    kit_dir = slug_dir / pasta
    template_content = template_path.read_text(encoding="utf-8")

    # Elementos decorativos de fundo sao opt-out via config_projeto.elementos_decorativos
    # (Passo 5 do /esbocar) -- default True se o campo nao existir (REGRA 3).
    config_projeto = carregar_json(slug_dir / "config_projeto.json")
    decorativos_ativos = (config_projeto or {}).get("elementos_decorativos", True)

    por_tom = {}
    for copy in copies:
        if not isinstance(copy, dict):
            continue
        por_tom.setdefault(copy.get("tom"), []).append(copy)

    erros = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()

        for tom in TONS_ORDENADOS:
            itens = por_tom.get(tom, [])
            if len(itens) != 2:
                print(f"[ERRO] tom '{tom}' tem {len(itens)} copies em {copies_path}, "
                      f"esperado exatamente 2")
                erros += 1
                continue

            pasta_tom = kit_dir / TOM_PASTA[tom]

            forma_html = ""
            if decorativos_ativos:
                # 1 tipo de forma/wave decorativa por bloco -- aqui o bloco e o TOM
                # dentro desta variante de kit (as 2 artes de "efeito-uau" do
                # kit-consultor compartilham a mesma forma/posicao; outro tom tende
                # a sortear forma E posicionamento diferentes).
                forma_nome, instancias = escolher_decoracao_fundo(f"{slug}:kit:{kit_variante}:{tom}")
                forma_html = gerar_forma_decorativa_html(forma_nome, instancias)

            for indice, copy in enumerate(itens, start=1):
                sufixo = f"{indice:02d}"
                dest_dir = pasta_tom / f"arte-{sufixo}"
                dest_dir.mkdir(parents=True, exist_ok=True)

                img_produto_filename = preparar_assets(dest_dir, slug_dir)
                badge_tag = resolver_badge(slug_dir)

                headline = copy.get("headline", "")
                subcopy = copy.get("subcopy", "")
                rotulo = f"{kit_variante}/{TOM_PASTA[tom]}/arte-{sufixo}"

                dest_html = dest_dir / "index.html"
                dest_png = dest_dir / f"arte_{slug}_{kit_variante}_{tom}_{sufixo}.png"

                html_final = preencher_template(
                    template_content,
                    titulo=f"Kit {kit_variante} {tom} {sufixo} - Conexão",
                    headline=headline,
                    subcopy=subcopy,
                    cta=cta,
                    img_produto_filename=img_produto_filename,
                    badge_tag=badge_tag,
                    forma_decorativa_html=forma_html,
                )
                dest_html.write_text(html_final, encoding="utf-8")

                conteudo_final = {
                    "id": copy.get("id"),
                    "tom": tom,
                    "angulo": copy.get("angulo", ""),
                    "headline": headline,
                    "subcopy": subcopy,
                    "cta": cta,
                    "assinatura": assinatura,
                }
                (dest_dir / "conteudo.json").write_text(
                    json.dumps(conteudo_final, ensure_ascii=False, indent=2), encoding="utf-8")

                (dest_dir / "texto_whatsapp.txt").write_text(
                    montar_texto_whatsapp(tom, headline, subcopy, cta, assinatura), encoding="utf-8")

                print(f"Renderizando {rotulo} em PNG ({LARGURA}x{ALTURA}px)...")
                if not renderizar_pagina(browser, dest_html, dest_png, LARGURA, ALTURA, rotulo=rotulo):
                    erros += 1

        browser.close()

    return 1 if erros else 0


def main():
    ap = argparse.ArgumentParser(description="Compila as copies compartilhadas do kit em PNGs + textos de WhatsApp")
    ap.add_argument("slug")
    ap.add_argument("--kit", choices=[*VARIANTES_VALIDAS, "ambos"], default="ambos")
    ap.add_argument("--pasta", default=None,
                     help="pasta de destino em output/<slug>/ (default: o proprio "
                          "--kit; use '<kit>-v2', '-v3'... para regeneracoes que nao "
                          "devem sobrescrever a versao anterior - ver REGRA 11 do "
                          "AGENTS.md). So valido com --kit != 'ambos'.")
    args = ap.parse_args()

    if args.pasta and args.kit == "ambos":
        print("[ERRO] --pasta so pode ser usado com um unico --kit (nunca com 'ambos')")
        return 1

    variantes = list(VARIANTES_VALIDAS) if args.kit == "ambos" else [args.kit]

    erros = 0
    for variante in variantes:
        ret = compilar_kit(args.slug, variante, args.pasta)
        if ret != 0:
            erros += 1

    return 1 if erros > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
