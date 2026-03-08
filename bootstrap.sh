#!/bin/bash
# MDex Singularity Bootstrap - Linux/macOS
# L0g0rhythm Authority Core - Kernel v3.5

echo -e "\033[0;36m🚀 Inicializando MDex Singularity v4.0...\033[0m"

# 1. Verificar/Criar Venv
if [ ! -d "venv" ]; then
    echo -e "\033[0;33m📦 Criando ambiente virtual...\033[0m"
    python3 -m venv venv
fi

# 2. Ativar Venv
echo -e "\033[0;33m🔌 Ativando ambiente...\033[0m"
source venv/bin/activate

# 3. Atualizar Dependências
echo -e "\033[0;33m📥 Verificando dependências...\033[0m"
pip install -r requirements.txt --quiet

# 4. Executar
echo -e "\033[0;32m✨ Iniciando MDex...\033[0m"
python3 main.py

echo -e "\033[0;36m🏁 Sessão finalizada.\033[0m"
