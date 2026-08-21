# Setup de Git Hooks para proj_fabrica-comunicacao
# Ativa o pre-commit hook de blindagem de segredos
# Uso: powershell -ExecutionPolicy Bypass -File scripts/setup-hooks.ps1

$ErrorActionPreference = "Stop"

# Detectar raiz do repo
$gitRoot = git rev-parse --show-toplevel 2>$null
if (-not $gitRoot) {
    Write-Host "[ERRO] Nao esta em repositorio Git." -ForegroundColor Red
    exit 1
}

$hooksSourceDir = Join-Path (Join-Path $gitRoot "scripts") "hooks"
$hooksTargetDir = Join-Path (Join-Path $gitRoot ".git") "hooks"

Write-Host "[INFO] Configurando git hooks..." -ForegroundColor Cyan
Write-Host ("  Raiz do repo: " + $gitRoot) -ForegroundColor Gray
Write-Host ("  Hooks source: " + $hooksSourceDir) -ForegroundColor Gray
Write-Host ("  Hooks target: " + $hooksTargetDir) -ForegroundColor Gray
Write-Host ""

# Passo 1: Configurar core.hooksPath
Write-Host "[PASSO 1] Configurando core.hooksPath..." -ForegroundColor Yellow
$relativeHooksPath = "scripts/hooks"
git config --local core.hooksPath $relativeHooksPath
if ($LASTEXITCODE -eq 0) {
    Write-Host ("  Configurado para: " + $relativeHooksPath) -ForegroundColor Green
} else {
    Write-Host "  Erro ao configurar core.hooksPath" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Passo 2: Copiar hook pre-commit para .git/hooks
Write-Host "[PASSO 2] Copiando pre-commit hook..." -ForegroundColor Yellow

if (-not (Test-Path $hooksTargetDir)) {
    New-Item -ItemType Directory -Force -Path $hooksTargetDir | Out-Null
    Write-Host "  Diretorio .git/hooks criado" -ForegroundColor Green
}

$preCommitSource = Join-Path $hooksSourceDir "pre-commit"
$preCommitTarget = Join-Path $hooksTargetDir "pre-commit"

if (-not (Test-Path $preCommitSource)) {
    Write-Host ("  Erro: arquivo nao encontrado: " + $preCommitSource) -ForegroundColor Red
    exit 1
}

Copy-Item -Path $preCommitSource -Destination $preCommitTarget -Force
Write-Host ("  pre-commit copiado para: " + $preCommitTarget) -ForegroundColor Green

# Passo 3: Tornar executavel
Write-Host "[PASSO 3] Configurando permissoes..." -ForegroundColor Yellow

# git update-index pode falhar se o arquivo estiver em .git/hooks (nao rastreado)
# isso e normal, o arquivo ja e executavel no sistema de arquivos
attrib -R "$preCommitTarget" 2>$null
Write-Host "  Permissoes atualizadas" -ForegroundColor Green
Write-Host ""

Write-Host "[SUCESSO] Git hooks configurados!" -ForegroundColor Green
Write-Host ""
Write-Host "Configured hooksPath:" -ForegroundColor Gray
git config --local core.hooksPath
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "  1. Testar o hook com um commit contendo padrao de chave (sk-, AKIA, ghp_, etc.)" -ForegroundColor Gray
Write-Host "  2. Confirmar que o commit e bloqueado" -ForegroundColor Gray
Write-Host ""
