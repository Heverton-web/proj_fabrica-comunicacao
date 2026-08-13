let workspaceAtivo = localStorage.getItem("workspaceAtivo") || null;

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
    const btn = document.createElement("button");
    btn.className = "secundario";
    btn.textContent = "usar";
    btn.onclick = () => marcarWorkspaceAtivo(ws.path);
    li.appendChild(btn);
    ul.appendChild(li);
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
  document.getElementById("cred-lista").textContent =
    harnesses_com_credencial.length ? harnesses_com_credencial.join(", ") : "(nenhuma)";
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

async function carregarArquivosDoJob(job, feedEl) {
  try {
    const arquivos = await chamar(
      "GET",
      `/api/projects/files?workspace_path=${encodeURIComponent(job.workspace_path)}&slug=${encodeURIComponent(job.slug)}`
    );
    if (!arquivos.length) {
      feedEl.textContent = "nenhum arquivo ainda.";
      return;
    }
    feedEl.innerHTML = arquivos
      .map((a) => `<div class="linha">${a.path}<span class="tam">${a.size}B</span></div>`)
      .join("");
    feedEl.scrollTop = feedEl.scrollHeight;
  } catch (erro) {
    feedEl.textContent = `(erro ao listar arquivos: ${erro.message})`;
  }
}

async function atualizarJobs() {
  if (!workspaceAtivo) return;
  const jobs = await chamar("GET", `/api/jobs?workspace_path=${encodeURIComponent(workspaceAtivo)}`);
  const ul = document.getElementById("jobs-lista");
  ul.innerHTML = "";

  for (const job of jobs) {
    const li = document.createElement("li");
    li.className = `job-card ${job.status}`;

    const top = document.createElement("div");
    top.className = "job-top";
    const permTag = job.permission_mode ? ` · permissão: ${job.permission_mode}` : "";
    top.innerHTML =
      `<span>#${job.id} <b>${job.slug}</b> via ${job.harness}${job.model ? ` (${job.model})` : ""}${permTag}</span>` +
      `<span class="badge ${job.status}">${job.status}${job.exit_code !== null ? ` · exit ${job.exit_code}` : ""}</span>`;
    li.appendChild(top);

    const track = document.createElement("div");
    track.className = "progress-track";
    track.innerHTML = `<div class="progress-fill"></div>`;
    li.appendChild(track);

    const feed = document.createElement("div");
    feed.className = "file-feed";
    feed.textContent = "carregando arquivos…";
    li.appendChild(feed);

    ul.appendChild(li);
    carregarArquivosDoJob(job, feed);
  }
}

(async function iniciar() {
  popularComandos();
  await carregarHarnesses();
  await carregarWorkspaces();
  await carregarCredenciais();
  if (workspaceAtivo) {
    document.getElementById("ws-ativo").textContent = workspaceAtivo;
    carregarProjetos();
    atualizarJobs();
  }
  setInterval(atualizarJobs, 2000);
})();
