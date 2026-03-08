# MDex Singularity (v4.0)

> [!IMPORTANT]
> **L0g0rhythm Authority Core — Kernel v3.5 (The Singularity)**
> 2026 Audited Edition.

Downloader de Mangás de alta performance, totalmente assíncrono e modularizado para o MangaDex.

## 🚀 Destaques da Versão 4.0
- **Arquitetura "1 Função = 1 Arquivo"**: Modularidade máxima para facilidade de manutenção.
- **Motor Assíncrono (`httpx` + `asyncio`)**: Downloads paralelos extremamente rápidos.
- **Rate Limiting Dinâmico**: Semáforos inteligentes para evitar bloqueio de IP.
- **Interface Premium**: UI moderna de terminal utilizando a biblioteca `Rich`.
- **Cross-Platform**: Suporte nativo para Windows (PowerShell), Linux e macOS.

## 🛠️ Instalação

1. Clone o repositório.
2. Crie um ambiente virtual:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Como Usar

Execute o ponto de entrada principal:
```bash
python main.py
```

Siga as instruções na tela para buscar o mangá, selecionar os capítulos e gerar os PDFs automaticamente.

## Como Executar (Recomendado)

O MDex Singularity v4.0 inclui scripts de auto-configuração (Bootstrap) que gerenciam o ambiente isolado automaticamente:

### Windows (PowerShell)
```powershell
./bootstrap.ps1
```

### Linux / macOS (Bash)
```bash
chmod +x bootstrap.sh
./bootstrap.sh
```

## Testes Automatizados
Para garantir a integridade do sistema em seu ambiente local:
```powershell
./venv/Scripts/python -m pytest tests/
```

## Arquitetura de Segurança (Kernel v3.5)
- **M06 (Data Integrity)**: Verificação de Hash SHA-256 no download.
- **M14 (Rate Limiting)**: Semáforos assíncronos para proteção contra banimento de IP.
- **M23 (Resource Safety)**: Limite de dimensões de imagem para evitar exaustão de RAM.
- **M25 (AI Privacy)**: Remoção automática de metadados EXIF.

## 📂 Estrutura do Projeto
- `src/api/`: Cliente de conexão assíncrona.
- `src/core/`: Configurações globais e rate limiting.
- `src/modules/`: Lógica de busca, download e PDF.
- `src/ui/`: Componentes visuais.
- `main.py`: Orquestrador do sistema.

---
**Desenvolvido sob as diretrizes de L0g0rhythm.**
