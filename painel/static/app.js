let workspaceAtivo = localStorage.getItem("workspaceAtivo") || null;

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

function marcarWorkspaceAtivo(path) {
  workspaceAtivo = path;
  localStorage.setItem("workspaceAtivo", path);
  document.getElementById("ws-ativo").textContent = path;
  atualizarJobs();
}

async function carregarWorkspaces() {
  const lista = await chamar("GET", "/api/workspaces");
  const ul = document.getElementById("ws-lista");
  ul.innerHTML = "";
  for (const ws of lista) {
    const li = document.createElement("li");
    li.innerHTML = `<code>${ws.path}</code> — registrado em ${ws.created_at}`;
    const btn = document.createElement("button");
    btn.textContent = "usar";
    btn.onclick = () => marcarWorkspaceAtivo(ws.path);
    li.appendChild(document.createTextNode(" "));
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
  const materiais = document.getElementById("proj-materiais").value
    .split(",").map((s) => s.trim()).filter(Boolean);

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

async function dispararJob() {
  if (!workspaceAtivo) return alert("Registre e selecione um workspace primeiro.");
  try {
    await chamar("POST", "/api/jobs", {
      workspace_path: workspaceAtivo,
      slug: document.getElementById("job-slug").value,
      harness: document.getElementById("job-harness").value,
      model: document.getElementById("job-model").value || null,
      prompt: document.getElementById("job-prompt").value,
    });
    atualizarJobs();
  } catch (erro) {
    alert(erro.message);
  }
}

async function atualizarJobs() {
  if (!workspaceAtivo) return;
  const jobs = await chamar("GET", `/api/jobs?workspace_path=${encodeURIComponent(workspaceAtivo)}`);
  const ul = document.getElementById("jobs-lista");
  ul.innerHTML = "";
  for (const job of jobs) {
    const li = document.createElement("li");
    li.className = "item";
    li.innerHTML =
      `#${job.id} <b>${job.slug}</b> via ${job.harness}` +
      (job.model ? ` (${job.model})` : "") +
      ` — <span class="status-${job.status}">${job.status}</span>` +
      (job.exit_code !== null ? ` (exit ${job.exit_code})` : "");
    ul.appendChild(li);
  }
}

(async function iniciar() {
  await carregarHarnesses();
  await carregarWorkspaces();
  await carregarCredenciais();
  if (workspaceAtivo) {
    document.getElementById("ws-ativo").textContent = workspaceAtivo;
    atualizarJobs();
  }
  setInterval(atualizarJobs, 3000);
})();
