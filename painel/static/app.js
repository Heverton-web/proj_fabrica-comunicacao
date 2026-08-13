let workspaceAtivo = localStorage.getItem("workspaceAtivo") || null;
// Workspace raiz deste repo -- nunca pode ser removido, nem so da lista (o
// backend ja recusa isso em painel/workspace.py; aqui e so uma segunda
// camada pra nem mostrar o botao de remover pra esse caminho especifico).
let workspaceRaizProtegido = null;

const ICONE_LIXEIRA =
  '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" ' +
  'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="M3 6h18"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>' +
  '<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>' +
  '<line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>';

const COMANDOS = [
  "esbocar",
  "produzir-comunicacao-completa",
  "gerar-pdf",
  "gerar-landing",
  "gerar-apresentacao",
  "gerar-arte",
  "gerar-arte-1080x1080",
  "gerar-arte-1080x1350",
  "gerar-arte-1080x1920",
  "gerar-textos",
  "gerar-kit-consultor",
  "gerar-kit-distribuidor",
  "kit-completo-cliente",
  "kit-completo-consultor",
  "kit-completo-distribuidor",
];

async function chamar(metodo, url, corpo) {
  const resp = await fetch(url, {
    method: metodo,
    headers: corpo ? { "Content-Type": "application/json" } : undefined,
    body: corpo ? JSON.stringify(corpo) : undefined,
  });
  const dados = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(dados.detail || `Falha em ${metodo} ${url} (HTTP ${resp.status})`);
  }
  return dados;
}

function popularComandos() {
  const select = document.getElementById("job-comando");
  select.innerHTML =
    COMANDOS.map((c) => `<option value="${c}">/${c}</option>`).join("") +
    `<option value="customizado">customizado…</option>`;
}

function alternarComandoCustomizado() {
  const custom = document.getElementById("job-comando").value === "customizado";
  document.getElementById("job-prompt-wrap").classList.toggle("oculto", !custom);
}

function marcarWorkspaceAtivo(path) {
  workspaceAtivo = path;
  localStorage.setItem("workspaceAtivo", path);
  document.getElementById("ws-ativo").textContent = path;
  carregarProjetos();
  atualizarJobs();
}

async function carregarWorkspaces() {
  const lista = await chamar("GET", "/api/workspaces");
  const ul = document.getElementById("ws-lista");
  ul.innerHTML = "";
  for (const ws of lista) {
    const li = document.createElement("li");
    li.className = "ws-item";
    li.innerHTML = `<span><code>${ws.path}</code> <span class="muted">— ${ws.created_at}</span></span>`;

    const acoes = document.createElement("span");
    acoes.className = "item-acoes";

    const btnUsar = document.createElement("button");
    btnUsar.className = "secundario";
    btnUsar.textContent = "usar";
    btnUsar.onclick = () => marcarWorkspaceAtivo(ws.path);
    acoes.appendChild(btnUsar);

    if (ws.path !== workspaceRaizProtegido) {
      const btnRemover = document.createElement("button");
      btnRemover.className = "btn-icone perigo";
      btnRemover.innerHTML = ICONE_LIXEIRA;
      btnRemover.title = "Remover da lista (só o registro — a pasta não é apagada)";
      btnRemover.setAttribute("aria-label", "Remover da lista");
      btnRemover.onclick = () => removerWorkspace(ws.path);
      acoes.appendChild(btnRemover);
    }

    li.appendChild(acoes);
    ul.appendChild(li);
  }
}

async function removerWorkspace(path) {
  if (!confirm(`Remover "${path}" da lista? Isso só tira o registro do painel — a pasta e os arquivos dentro dela NÃO são apagados.`)) {
    return;
  }
  try {
    await chamar("DELETE", `/api/workspaces?path=${encodeURIComponent(path)}`);
    if (workspaceAtivo === path) {
      workspaceAtivo = null;
      localStorage.removeItem("workspaceAtivo");
      document.getElementById("ws-ativo").textContent = "(nenhum)";
      pararPolling();
      document.getElementById("jobs-lista").innerHTML = "";
      document.getElementById("projetos-lista").innerHTML = "";
    }
    await carregarWorkspaces();
  } catch (erro) {
    alert(erro.message);
  }
}

async function registrarWorkspace() {
  const path = document.getElementById("ws-path").value;
  try {
    const ws = await chamar("POST", "/api/workspaces", { path });
    await carregarWorkspaces();
    marcarWorkspaceAtivo(ws.path);
  } catch (erro) {
    alert(erro.message);
  }
}

async function usarWorkspaceDoRepo() {
  try {
    const { path } = await chamar("GET", "/api/repo-workspace");
    document.getElementById("ws-path").value = path;
    await registrarWorkspace();
  } catch (erro) {
    alert(erro.message);
  }
}

async function carregarHarnesses() {
  const { harnesses } = await chamar("GET", "/api/harnesses");
  for (const id of ["cred-harness", "job-harness"]) {
    const select = document.getElementById(id);
    select.innerHTML = harnesses.map((h) => `<option value="${h}">${h}</option>`).join("");
  }
}

async function carregarCredenciais() {
  const { harnesses_com_credencial } = await chamar("GET", "/api/credentials");
  const ul = document.getElementById("cred-lista");
  ul.innerHTML = "";

  if (!harnesses_com_credencial.length) {
    ul.innerHTML = `<li class="muted">(nenhuma)</li>`;
    return;
  }

  for (const harness of harnesses_com_credencial) {
    const li = document.createElement("li");
    li.className = "ws-item";
    li.innerHTML = `<span><code>${harness}</code></span>`;

    const btnRemover = document.createElement("button");
    btnRemover.className = "btn-icone perigo";
    btnRemover.innerHTML = ICONE_LIXEIRA;
    btnRemover.title = "Remover credencial";
    btnRemover.setAttribute("aria-label", "Remover credencial");
    btnRemover.onclick = () => removerCredencial(harness);
    li.appendChild(btnRemover);

    ul.appendChild(li);
  }
}

async function removerCredencial(harness) {
  if (!confirm(`Remover a credencial salva de "${harness}"?`)) return;
  try {
    await chamar("DELETE", `/api/credentials/${encodeURIComponent(harness)}`);
    await carregarCredenciais();
  } catch (erro) {
    alert(erro.message);
  }
}

async function salvarCredencial() {
  const harness = document.getElementById("cred-harness").value;
  const env_var = document.getElementById("cred-envvar").value;
  const api_key = document.getElementById("cred-key").value;
  try {
    await chamar("POST", "/api/credentials", { harness, env_var, api_key });
    document.getElementById("cred-key").value = "";
    await carregarCredenciais();
  } catch (erro) {
    alert(erro.message);
  }
}

async function criarProjeto() {
  if (!workspaceAtivo) return alert("Registre e selecione um workspace primeiro.");
  const materiais = Array.from(
    document.querySelectorAll("#proj-materiais input[type=checkbox]:checked")
  ).map((el) => el.value);

  try {
    await chamar("POST", "/api/projects", {
      workspace_path: workspaceAtivo,
      slug: document.getElementById("proj-slug").value,
      texto_base: document.getElementById("proj-texto").value,
      publico_alvo: document.getElementById("proj-publico").value,
      objetivo_tom: document.getElementById("proj-tom").value,
      materiais_selecionados: materiais,
    });
    alert("Projeto criado dentro do workspace.");
  } catch (erro) {
    alert(erro.message);
  }
}

async function carregarProjetos() {
  if (!workspaceAtivo) return;
  const ul = document.getElementById("projetos-lista");
  const datalist = document.getElementById("job-slug-lista");
  let projetos;
  try {
    projetos = await chamar("GET", `/api/projects?workspace_path=${encodeURIComponent(workspaceAtivo)}`);
  } catch (erro) {
    ul.innerHTML = `<li class="muted">${erro.message}</li>`;
    return;
  }

  ul.innerHTML = "";
  datalist.innerHTML = "";
  if (!projetos.length) {
    ul.innerHTML = `<li class="muted">nenhum projeto esboçado neste workspace ainda.</li>`;
    return;
  }

  for (const p of projetos) {
    datalist.innerHTML += `<option value="${p.slug}"></option>`;

    const materiaisProntos = (p.manifesto ? p.manifesto.materiais : [])
      .map((m) => m.tipo)
      .join(", ");
    const statusBrief = p.tem_brief
      ? "brief pronto — pode disparar /gerar-*"
      : "sem brief_criativo.json — precisa rodar /esbocar antes de /gerar-*";

    const li = document.createElement("li");
    li.className = "ws-item";
    li.innerHTML =
      `<span><b>${p.slug}</b> — <span class="muted">${statusBrief}</span>` +
      (materiaisProntos ? `<br><span class="muted">materiais já gerados: ${materiaisProntos}</span>` : "") +
      `</span>`;
    const btn = document.createElement("button");
    btn.className = "secundario";
    btn.textContent = "usar no passo 5";
    btn.onclick = () => {
      document.getElementById("job-slug").value = p.slug;
    };
    li.appendChild(btn);
    ul.appendChild(li);
  }
}

async function dispararJob() {
  if (!workspaceAtivo) return alert("Registre e selecione um workspace primeiro.");
  const slug = document.getElementById("job-slug").value;
  const comando = document.getElementById("job-comando").value;
  const prompt =
    comando === "customizado"
      ? document.getElementById("job-prompt").value
      : `/${comando} ${slug}`.trim();

  const permissionMode = document.getElementById("job-permissao").value || null;
  if (permissionMode === "bypass" && !confirm(
    "Bypass total desliga toda verificação de permissão do harness neste job. Confirmar?"
  )) {
    return;
  }

  try {
    await chamar("POST", "/api/jobs", {
      workspace_path: workspaceAtivo,
      slug,
      harness: document.getElementById("job-harness").value,
      model: document.getElementById("job-model").value || null,
      permission_mode: permissionMode,
      command: comando === "customizado" ? null : comando,
      prompt,
    });
    atualizarJobs();
  } catch (erro) {
    alert(erro.message);
  }
}

// Job terminado (done/error) nao tem mais arquivo novo para aparecer -- cachear
// o feed evita reconsultar disco pra sempre a cada tick de poll.
const arquivosCacheDoJob = {};
let pollTimer = null;

function pararPolling() {
  if (pollTimer) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }
}

// Poll auto-agendado (setTimeout, nao setInterval): so continua enquanto
// existir job pending/running. Sem isso o poll rodava pra sempre, e a cada
// tick refazia a listagem de arquivos de TODOS os jobs (inclusive os ja
// terminados ha muito tempo) -- N+1 chamadas HTTP a cada 2s sem parar nunca,
// mesmo sem nenhum job ativo (achado real reportado pelo usuario).
function agendarProximaAtualizacao(haJobAtivo) {
  pararPolling();
  if (haJobAtivo) {
    pollTimer = setTimeout(atualizarJobs, 2000);
  }
}

async function carregarArquivosDoJob(job, feedEl) {
  try {
    const arquivos = await chamar(
      "GET",
      `/api/projects/files?workspace_path=${encodeURIComponent(job.workspace_path)}&slug=${encodeURIComponent(job.slug)}`
    );
    const html = arquivos.length
      ? arquivos.map((a) => `<div class="linha">${a.path}<span class="tam">${a.size}B</span></div>`).join("")
      : "nenhum arquivo ainda.";
    feedEl.innerHTML = html;
    feedEl.scrollTop = feedEl.scrollHeight;
    if (job.status === "done" || job.status === "error") {
      arquivosCacheDoJob[job.id] = html;
    }
  } catch (erro) {
    feedEl.textContent = `(erro ao listar arquivos: ${erro.message})`;
  }
}

// Elementos de card por job.id -- reaproveitados entre ticks de poll (nunca
// recriados do zero) pra barra de progresso poder de fato fazer uma
// transicao suave de largura. Recriar o <li> a cada tick (como era antes)
// interrompe qualquer transicao/animacao CSS no meio do caminho -- e isso,
// junto com um keyframe em loop, e o que parecia "piscar".
const elementosDoJobPorId = {};

function criarCardDeJob() {
  const li = document.createElement("li");

  const top = document.createElement("div");
  top.className = "job-top";
  li.appendChild(top);

  const feed = document.createElement("div");
  feed.className = "file-feed";
  feed.textContent = "carregando arquivos…";
  li.appendChild(feed);

  const track = document.createElement("div");
  track.className = "progress-track";
  const fill = document.createElement("div");
  fill.className = "progress-fill";
  track.appendChild(fill);
  li.appendChild(track);

  return { li, top, feed, fill };
}

// Nao ha progresso real reportado pelo harness (headless, sem callback) --
// em vez de um loop indeterminado, sobe rapido no comeco e desacelera com
// base no tempo real decorrido, sem nunca fechar 100% sozinha. So o status
// real (done/error) faz a barra chegar no fim.
function calcularLarguraProgresso(job) {
  if (job.status === "done" || job.status === "error") return 100;
  if (job.status !== "running") return 4;
  const decorridoSeg = (Date.now() - new Date(job.created_at).getTime()) / 1000;
  const pct = 92 * (1 - Math.exp(-decorridoSeg / 25));
  return Math.max(4, Math.min(92, pct));
}

async function atualizarJobs() {
  if (!workspaceAtivo) {
    agendarProximaAtualizacao(false);
    return;
  }
  const jobs = await chamar("GET", `/api/jobs?workspace_path=${encodeURIComponent(workspaceAtivo)}`);
  const ul = document.getElementById("jobs-lista");

  const idsAtuais = new Set(jobs.map((j) => j.id));
  for (const id of Object.keys(elementosDoJobPorId)) {
    if (!idsAtuais.has(Number(id))) delete elementosDoJobPorId[id];
  }

  let haJobAtivo = false;

  const itensEmOrdem = jobs.map((job) => {
    if (job.status === "pending" || job.status === "running") haJobAtivo = true;

    const els = elementosDoJobPorId[job.id] || (elementosDoJobPorId[job.id] = criarCardDeJob());
    els.li.className = `job-card ${job.status}`;

    const permTag = job.permission_mode ? ` · permissão: ${job.permission_mode}` : "";
    els.top.innerHTML =
      `<span>#${job.id} <b>${job.slug}</b> via ${job.harness}${job.model ? ` (${job.model})` : ""}${permTag}</span>` +
      `<span class="badge ${job.status}">${job.status}${job.exit_code !== null ? ` · exit ${job.exit_code}` : ""}</span>`;

    els.fill.style.width = `${calcularLarguraProgresso(job)}%`;

    const cacheado = arquivosCacheDoJob[job.id];
    if (cacheado !== undefined) {
      els.feed.innerHTML = cacheado;
    } else if (job.status !== "pending") {
      carregarArquivosDoJob(job, els.feed);
    }

    return els.li;
  });

  // replaceChildren move os <li> ja existentes (preservando estado/transicao
  // CSS) em vez de destruir e recriar -- so cria de fato os que sao novos.
  ul.replaceChildren(...itensEmOrdem);
  agendarProximaAtualizacao(haJobAtivo);
}

(async function iniciar() {
  popularComandos();
  try {
    workspaceRaizProtegido = (await chamar("GET", "/api/repo-workspace")).path;
  } catch (erro) {
    // painel ainda funciona sem isso -- so nao esconde o botao de remover
    // do workspace raiz na lista (o backend recusa a remocao de qualquer jeito).
  }
  await carregarHarnesses();
  await carregarWorkspaces();
  await carregarCredenciais();
  if (workspaceAtivo) {
    document.getElementById("ws-ativo").textContent = workspaceAtivo;
    carregarProjetos();
    atualizarJobs();
  }
})();
