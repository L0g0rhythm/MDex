# MDex Singularity Bootstrap - Windows (PowerShell)
# L0g0rhythm Authority Core - Kernel v3.5

Write-Host "🚀 Inicializando MDex Singularity v4.0..." -ForegroundColor Cyan

# 1. Verificar/Criar Venv
if (!(Test-Path "venv")) {
    Write-Host "📦 Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# 2. Ativar Venv
Write-Host "🔌 Ativando ambiente..." -ForegroundColor Yellow
$VenvActivate = ".\venv\Scripts\Activate.ps1"
& $VenvActivate

# 3. Atualizar Dependências
Write-Host "📥 Verificando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# 4. Executar
Write-Host "✨ Iniciando MDex..." -ForegroundColor Green
python main.py

Write-Host "🏁 Sessão finalizada." -ForegroundColor Cyan
