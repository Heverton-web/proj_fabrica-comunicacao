#!/usr/bin/env python3
"""
Helper compartilhado por orquestrar-pool-materiais.py, auditar-projeto.py e
empacotar-projeto.py: separa "tipo" (qual validador/dimensao/CTA se aplica) de
"pasta" (nome real do diretorio em output/<slug>/, que pode ser uma versao
regenerada por /gerar-<material> — ver REGRA 11 do AGENTS.md).

Tambem e a FONTE UNICA da regra deterministica dos presets
/kit-completo-<publico> (SPEC_COMANDOS.md): consumida por parametros_projeto.py
(--validar) e auditar-projeto.py (gate --estrito). Nunca duplicar PRESETS_KIT_COMPLETO
ou erros_preset_kit_completo em outro script — lição do bug historico de TIPOS_VALIDOS
duplicado.

Convencao de versionamento (mesma do slug de projeto inteiro no /esbocar):
1a geracao = pasta sem sufixo (ex.: "pdf"); regeneracoes seguintes = "pdf-v2",
"pdf-v3"... Nunca sobrescreve uma pasta ja entregue.

Modulo de Resiliencia de Rede (Retry com Backoff):
Fornece retry automatico com backoff exponencial + jitter para operacoes que podem
falhar temporariamente (HTTP, timeouts do browser, etc).
Reaproveita stdlib: time, random, urllib, itertools.
"""

import re
import time
import random
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from itertools import count

RE_VERSAO = re.compile(r"^(.+)-v(\d+)$")

# Presets /kit-completo-<publico> (SPEC_COMANDOS.md, secao /kit-completo-consultor):
# publico_alvo fixo + materiais fixos por preset.
PRESETS_KIT_COMPLETO = {
    "consultores": {
        "publico_alvo": "consultores",
        "materiais": ["pdf", "kit-consultor", "landing-page", "apresentacao"],
    },
    "distribuidores": {
        "publico_alvo": "distribuidores",
        "materiais": ["pdf", "kit-distribuidor", "landing-page", "apresentacao"],
    },
    "clientes": {
        "publico_alvo": "clientes",
        "materiais": ["pdf", "landing-page", "apresentacao"],
    },
}

KITS = {"kit-consultor", "kit-distribuidor"}


def tipo_base(pasta):
    """'pdf-v2' -> 'pdf'; 'pdf' -> 'pdf'."""
    m = RE_VERSAO.match(pasta)
    return m.group(1) if m else pasta


def numero_versao(pasta):
    """'pdf-v2' -> 2; 'pdf' -> 1 (1a geracao, implicita)."""
    m = RE_VERSAO.match(pasta)
    return int(m.group(2)) if m else 1


def proxima_pasta_livre(dir_slug, tipo_base_str):
    """Proximo nome de pasta livre para uma NOVA versao de tipo_base_str dentro
    de dir_slug: o proprio tipo_base_str se a pasta ainda nao existe (1a
    geracao), senao tipo_base_str-v2, -v3... (primeiro numero livre)."""
    if not (dir_slug / tipo_base_str).exists():
        return tipo_base_str
    n = 2
    while (dir_slug / f"{tipo_base_str}-v{n}").exists():
        n += 1
    return f"{tipo_base_str}-v{n}"


def erros_preset_kit_completo(config):
    """Regra deterministica dos presets /kit-completo-<publico>: retorna lista de
    erros (vazia se conforme ou se o config nao usa preset). Chamado por
    parametros_projeto.py --validar e auditar-projeto.py --estrito."""
    preset = config.get("preset_kit_completo")
    if not preset:
        return []
    if preset not in PRESETS_KIT_COMPLETO:
        return [
            f"preset_kit_completo invalido: {preset!r} - esperado um de "
            f"{sorted(PRESETS_KIT_COMPLETO)}"
        ]

    erros = []
    esperado = PRESETS_KIT_COMPLETO[preset]
    publico = config.get("publico_alvo")
    if publico != esperado["publico_alvo"]:
        erros.append(
            f"preset {preset!r} exige publico_alvo {esperado['publico_alvo']!r}, "
            f"mas config.publico_alvo = {publico!r}"
        )

    materiais = set(config.get("materiais_selecionados", []))
    for m in esperado["materiais"]:
        if m not in materiais:
            erros.append(
                f"preset {preset!r} exige o material {m!r} em materiais_selecionados"
            )
    for kit in sorted(KITS):
        if kit not in esperado["materiais"] and kit in materiais:
            erros.append(
                f"preset {preset!r} nao inclui kits - material {kit!r} nao pode "
                f"estar em materiais_selecionados"
            )
    return erros


# === RESILIENCIA DE REDE ===

def http_get_with_retry(url, max_retries=3, timeout=10, verbose=False):
    """Fetch HTTP com retry exponencial + jitter para falhas transitórias.

    Retorna: bytes do response body
    Levanta: URLError/HTTPError se todos os retries falharem

    Padrões retentáveis:
    - HTTPError 429 (Too Many Requests), 502 (Bad Gateway), 503 (Service Unavailable)
    - URLError de timeout

    Padrões NÃO retentáveis (levantam imediatamente):
    - HTTPError 404, 403, 401, 400
    - Qualquer outro erro não-transitório
    """
    for attempt in range(max_retries):
        try:
            if verbose:
                print(f"[HTTP GET] {url} (tentativa {attempt + 1}/{max_retries})")
            response = urlopen(url, timeout=timeout)
            return response.read()
        except HTTPError as e:
            if e.code in (429, 502, 503):
                if attempt == max_retries - 1:
                    raise
                wait = 0.5 * (2 ** attempt) + random.uniform(0, 0.3)
                if verbose:
                    print(f"  → Erro {e.code} (transitório), aguardando {wait:.2f}s...")
                time.sleep(wait)
            else:
                if verbose:
                    print(f"  → Erro {e.code} (não-retentável), falhando imediatamente")
                raise
        except (URLError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise
            wait = 0.5 * (2 ** attempt) + random.uniform(0, 0.3)
            if verbose:
                print(f"  → Timeout/URLError, aguardando {wait:.2f}s...")
            time.sleep(wait)

    raise URLError(f"Máximo de retries ({max_retries}) atingido para {url}")


def playwright_goto_with_retry(page, url, max_retries=3, timeout=30000, verbose=False):
    """Wrapper de page.goto() com retry exponencial + jitter.

    Útil para contornar timeouts transitórios ao carregar URLs em Playwright.

    Args:
        page: Objeto Playwright page
        url: URL a carregar
        max_retries: Número máximo de tentativas
        timeout: Timeout em ms (padrão Playwright é 30000)
        verbose: Log de retries

    Retorna: response object do page.goto()
    Levanta: TimeoutError ou exceção original se todos retries falharem
    """
    for attempt in range(max_retries):
        try:
            if verbose:
                print(f"[PLAYWRIGHT GOTO] {url} (tentativa {attempt + 1}/{max_retries})")
            return page.goto(url, wait_until="networkidle", timeout=timeout)
        except (TimeoutError, Exception) as e:
            if "timeout" not in str(e).lower() and "connection" not in str(e).lower():
                if verbose:
                    print(f"  → Erro não-transitório: {type(e).__name__}")
                raise
            if attempt == max_retries - 1:
                raise
            wait = 0.5 * (2 ** attempt) + random.uniform(0, 0.3)
            if verbose:
                print(f"  → Timeout/conexão, aguardando {wait:.2f}s...")
            time.sleep(wait)

    raise TimeoutError(f"Máximo de retries ({max_retries}) atingido para {url}")
