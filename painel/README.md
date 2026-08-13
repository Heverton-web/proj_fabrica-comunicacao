# Painel de Controle Universal Multi-Harness

Backend local (FastAPI) + frontend mínimo que dá "cara" à Fábrica de Materiais
de Comunicação sem depender de uma sessão interativa de agente, sem travar em
um único provedor de LLM, e sem banco de dados de conteúdo — os artefatos
ficam sempre dentro da pasta (workspace) que o usuário escolhe.

Plano completo: [`melhorias/plano-painel-controle-multi-harness.md`](../melhorias/plano-painel-controle-multi-harness.md).

## Como rodar

```bash
pip install -r painel/requirements.txt
python -m uvicorn painel.main:app --reload --port 8787
```

Abra `http://127.0.0.1:8787/` no navegador. É um serviço **local**, não
cloud — precisa acesso a filesystem arbitrário e capacidade de spawnar
processo, algo que um browser puro não tem.

## Como rodar os testes

```bash
python -m pytest painel/tests -v -o testpaths=
```

(o `-o testpaths=` é necessário porque o `pytest.ini` da raiz do repo aponta
`testpaths = tests`, exclusivo dos testes da Fábrica.)

## Onde cada coisa vive

| O quê | Onde |
|---|---|
| Artefatos gerados (config, PDFs, PNGs, etc.) | dentro da pasta de workspace que o usuário escolhe — **nunca em banco** |
| Índice de execuções (job id, status, log, exit code) | `~/.fabrica-painel/painel.db` (SQLite, fora do workspace) |
| Credenciais de harness/provedor | `~/.fabrica-painel/vault.enc` (criptografado, fora do workspace) |
| Logs de cada job | `~/.fabrica-painel/logs/job-<id>.log` |

`FABRICA_PAINEL_HOME` sobrescreve `~/.fabrica-painel` (usado pelos testes para
nunca tocar no home real).

## Escolher provedor de LLM = escolher harness

"Provedor/LLM" é resolvido pela **CLI do harness já configurada pelo
usuário**, não por chamada crua a uma API de LLM — ver seção 3 do plano para o
racional completo. Harnesses hoje registrados em
`painel/harness_adapters/__init__.py`:

- `echo` — dry-run, não chama LLM nenhuma. Existe só para provar a
  canalização inteira (subprocess real → arquivo no workspace → status/log).
- `claude-code` — monta `claude -p "<prompt>" [--model <modelo>]`.
- `opencode` — monta `opencode run "<prompt>" [--model <modelo>]`.

### Adicionar um novo harness

1. Criar `painel/harness_adapters/novo_harness.py` com uma classe que
   implementa `HarnessAdapter.build_invocation(cwd, prompt, credential, model)`.
2. Registrar em `_REGISTRY` em `painel/harness_adapters/__init__.py`.
3. Escrever testes de construção de comando (mockados) em
   `painel/tests/test_adapters.py`, seguindo o padrão dos adaptadores
   existentes.

## Pré-requisito de insumos (brief_criativo.json)

Comandos `/gerar-*` e `/produzir-comunicacao-completa` regeneram material a
partir de um projeto **já esboçado** — eles falham rápido sem
`brief_criativo.json` (ver `.claude/commands/*.md`). O backend valida isso
antes de disparar o job (`POST /api/jobs` rejeita com HTTP 400 se o slug não
tiver `brief_criativo.json` e o `command` enviado exigir um). `/esbocar` e
`/kit-completo-*` ficam de fora da checagem — são eles que criam o brief.

A seção "Projetos existentes no workspace" da UI lista os projetos já
esboçados no workspace ativo (com o status do brief e quais materiais já
foram gerados) para reaproveitar um slug existente e disparar só um
`/gerar-*` novo, sem repetir o `/esbocar`.

## Credenciais

`POST /api/credentials` recebe `{harness, env_var, api_key}` e grava
criptografado (Fernet) em `vault.enc`, fora do workspace. Ao disparar um job,
o backend injeta `{env_var: api_key}` no ambiente do subprocess do harness
escolhido — nunca grava a credencial em disco em texto claro, nunca dentro do
workspace do usuário.

## O que foi validado de verdade nesta entrega

- **47 testes automatizados** (`pytest`), incluindo:
  - subprocess real do adaptador `echo` criando arquivo em disco;
  - job runner real (thread + subprocess) atualizando status no índice;
  - API HTTP real via `TestClient` (workspace, credenciais, projetos,
    disparo de job, listagem de arquivos) — nenhum teste usa apenas mocks
    para o fluxo principal;
  - regressão do bug de normalização de `workspace_path` (barra `/` vs `\`)
    e do bug de resolução de executável via `PATH` (shim `.cmd` do npm no
    Windows).
- **Smoke test manual end-to-end**: servidor `uvicorn` real, requisições HTTP
  reais via `curl` e validação visual real via Playwright (screenshot),
  confirmando:
  - `config_projeto.json` e artefatos do job gravados dentro da pasta de
    workspace escolhida (nunca em banco);
  - `painel.db` (bookkeeping) e os logs ficando fora do workspace, em
    `~/.fabrica-painel`;
  - lista de jobs e feed de arquivos renderizando corretamente na UI.
- **Chamada real a LLM via os adaptadores `claude-code` e `opencode`**
  (prompt pequeno e seguro, fora de qualquer slash-command): os dois
  responderam corretamente (`exit_code 0`), confirmando que a construção de
  comando, injeção de credencial/modelo e resolução de executável funcionam
  de ponta a ponta com harness real, não só com o adaptador `echo`. O que
  **não** foi testado é um slash-command real (`/produzir-comunicacao-completa`
  etc.) — isso depende da limitação nº 1 abaixo (descoberta de skills).

## Limitações conhecidas (leia antes de usar com um harness real)

0. ~~Job ficava preso em "running" para sempre mesmo com o trabalho já
   concluído~~ — **RESOLVIDO.** `subprocess.run(..., capture_output=True)`
   só retorna quando o pipe de stdout/stderr fecha, e isso só acontece
   quando **todo** processo que herdou aquele handle termina — inclusive um
   neto que o harness spawna (MCP server, `node.exe` por trás do shim
   `.cmd` do npm no Windows) e que não morre junto com o processo principal.
   `painel/jobs.py` agora redireciona stdout/stderr direto para o arquivo de
   log (nunca `PIPE`), então o runner só espera o PID do processo filho
   direto — regressão coberta por
   `test_run_job_does_not_hang_waiting_for_orphaned_grandchild`.
1. ~~Descoberta de skills quando o workspace é externo ao repo~~ — **RESOLVIDO
   para `claude-code` quando o workspace é `<repo>/output`** (o atalho "usar
   output/ deste repo" da seção 1 do painel). O job runner detecta
   automaticamente que o projeto está dentro deste repo e adiciona
   `--add-dir <repo root>` — sem isso, `claude -p` recusa ler `AGENTS.md`/
   `SPEC_COMANDOS.md` por ficarem acima do cwd (achado real, não hipotético).
   Se o workspace continuar **fora** do repo, a limitação original persiste;
   `opencode` não tem um flag equivalente conhecido a `--add-dir`.
2. **Rodar um slash-command real precisa de `permission_mode` explícito.**
   Mesmo com `--add-dir` resolvendo a leitura dos arquivos, o `claude -p`
   headless para pedindo aprovação antes de rodar `Bash`/scripts (sem
   terminal pra aprovar) e desiste sozinho, sem travar. É preciso escolher,
   por job, um de:
   - **`scoped`** (recomendado): `--allowedTools "Bash Read Write Edit Glob
     Grep Task"` — libera só as ferramentas que o pipeline usa, sem desligar
     nenhuma verificação de segurança do harness. **Validado de ponta a
     ponta**: `/produzir-comunicacao-completa` com `materiais_selecionados:
     ["textos"]` gerou de verdade `dossie_insumos.md`, `brief_criativo.json`
     e os 3 textos (WhatsApp/Instagram/LinkedIn), com conteúdo real e
     coerente, e `_pool_estado.json` marcou `"estado": "concluido_autonomo"`.
   - **`bypass`**: `--allow-dangerously-skip-permissions` (claude-code) /
     `--auto` (opencode) — desliga toda verificação de permissão do harness.
     Maior raio de risco; disponível porque às vezes é a única forma de
     rodar 100% autônomo, mas quem dispara o job decide isso conscientemente
     (a UI pede confirmação extra antes de disparar em modo `bypass`).
   - Sem escolher nenhum dos dois (padrão), o comportamento é o mais seguro,
     mas pode parar pedindo aprovação e desistir — não serve pra produção
     autônoma de verdade.
3. **Empacotamento final ainda não foi observado completo num teste real.**
   No teste de validação (timeout de 300s), o material "textos" terminou e
   foi validado (`concluido_autonomo`) dentro da janela, mas o processo
   ainda estava rodando (provavelmente `revisor-marca`/empacotamento) quando
   o timeout do teste matou o subprocess — isso é uma limitação do *teste*
   (janela curta), não uma falha observada do pipeline. Rodar sem timeout
   apertado (ou aumentar o timeout do job) é necessário pra ver o fluxo
   completo até `manifesto_materiais.json`/pacote final.
4. **Fluxo one-shot substitui a entrevista conversacional do `/esbocar`.**
   Como a invocação é headless, o formulário precisa entregar tudo de uma vez
   — perde-se a adaptação dinâmica de perguntas de acompanhamento que uma
   conversa real permite (REGRA 3 do `AGENTS.md`).
5. **Cofre de credenciais é single-user, não enterprise.** Chave simétrica
   local (Fernet), sem rotação, sem HSM. Adequado para uso pessoal.
6. **Sem autenticação na API HTTP.** Pensado para rodar só em `localhost`;
   não expor a rede sem adicionar autenticação.
7. **Job runner é uma thread por job, sem fila real.** Suficiente para uso
   pessoal sequencial; múltiplos jobs pesados simultâneos precisariam de uma
   fila de verdade (ex.: limite de concorrência, prioridade).
8. **Frontend é funcional, não polido.** Wizard funcional sem framework e
   sem polimento visual — prova o fluxo, não é a versão final de produto.
