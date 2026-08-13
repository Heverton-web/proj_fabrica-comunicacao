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

## Credenciais

`POST /api/credentials` recebe `{harness, env_var, api_key}` e grava
criptografado (Fernet) em `vault.enc`, fora do workspace. Ao disparar um job,
o backend injeta `{env_var: api_key}` no ambiente do subprocess do harness
escolhido — nunca grava a credencial em disco em texto claro, nunca dentro do
workspace do usuário.

## O que foi validado de verdade nesta entrega

- **37 testes automatizados** (`pytest`), incluindo:
  - subprocess real do adaptador `echo` criando arquivo em disco;
  - job runner real (thread + subprocess) atualizando status no índice;
  - API HTTP real via `TestClient` (workspace, credenciais, projetos,
    disparo de job) — nenhum teste usa apenas mocks para o fluxo principal.
- **Smoke test manual end-to-end**: servidor `uvicorn` real, requisições HTTP
  reais via `curl` (não `TestClient`), confirmando:
  - `config_projeto.json` e `smoke_marker.txt` gravados dentro da pasta de
    workspace escolhida (nunca em banco);
  - `painel.db` (bookkeeping) e os logs ficando fora do workspace, em
    `~/.fabrica-painel`.

## Limitações conhecidas (leia antes de usar com um harness real)

1. **Descoberta de skills quando o workspace é externo ao repo.** Os
   adaptadores `claude-code`/`opencode` rodam com `cwd` = pasta do projeto
   dentro do workspace escolhido. Se esse workspace estiver fora deste
   repositório, o harness não vai encontrar `.claude/skills/`,
   `SPEC_COMANDOS.md`, `AGENTS.md` etc. — que é de onde vem todo o
   conhecimento da Fábrica. **Isso não foi resolvido nesta entrega.** Três
   saídas possíveis, a decidir antes de usar em produção:
   - manter o workspace como uma subpasta dentro deste repo (ex.:
     `<repo>/output`), igual ao pipeline atual;
   - instalar as skills em nível de usuário/global no harness escolhido, se
     ele suportar (verificar por harness);
   - estender o adaptador para passar um "project root" explícito, se o
     harness tiver essa opção de CLI.
2. **Adaptadores de harness real não foram exercitados com subprocess de
   verdade.** `claude-code` e `opencode` são validados só por construção de
   comando (testes mockados) — de propósito, para não gerar custo de LLM nem
   risco de recursão de agente rodando de dentro desta própria sessão. Rodar
   de verdade requer o binário instalado e credencial real do usuário.
3. **Fluxo one-shot substitui a entrevista conversacional do `/esbocar`.**
   Como a invocação é headless, o formulário precisa entregar tudo de uma vez
   — perde-se a adaptação dinâmica de perguntas de acompanhamento que uma
   conversa real permite (REGRA 3 do `AGENTS.md`).
4. **Cofre de credenciais é single-user, não enterprise.** Chave simétrica
   local (Fernet), sem rotação, sem HSM. Adequado para uso pessoal.
5. **Sem autenticação na API HTTP.** Pensado para rodar só em `localhost`;
   não expor a rede sem adicionar autenticação.
6. **Job runner é uma thread por job, sem fila real.** Suficiente para uso
   pessoal sequencial; múltiplos jobs pesados simultâneos precisariam de uma
   fila de verdade (ex.: limite de concorrência, prioridade).
7. **Frontend é intencionalmente mínimo.** Wizard funcional sem framework e
   sem polimento visual — prova o fluxo, não é a versão final de produto.
