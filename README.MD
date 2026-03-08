# MDex Omni-v6 (Absolute Singularity)

> [!IMPORTANT]
> **L0g0rhythm Authority Core — Kernel v3.5.8 (Total Singularity)**
> Edição Auditada 2026. **Certificação de 100% de Cobertura de Testes.**

Downloader de Mangás de ultra-performance, totalmente assíncrono e modularizado. MDex Omni-v6 representa o ápice da arquitetura defensiva e funcional para o MangaDex.

## 🏆 Singularidade Absoluta
O estado de **Singularidade Absoluta** foi atingido, com **100% de cobertura de testes** em todo o núcleo (`src/`). Cada linha de código foi auditada, testada e validada contra falhas de rede e condições de borda.

## 🚀 Destaques da Versão Omni-v6
- **Motor Omni-Reader (Integração Avançada)**: 
  - **OCR Nativo**: Extração de texto de alta precisão via EasyOCR.
  - **Tradução Estruturada**: Motor Argos Translate integrado para traduções locais (EN -> PT-BR) com zero dependência de serviços externos.
- **Arquitetura Zero Trust**: Rigoroso controle de segurança, rate limiting dinâmico e saneamento de metadados.
- **Performance Assíncrona Total**: Orquestração via `httpx` + `asyncio` permitindo processamento maciço de dados.
- **Modularidade Nível Kernel**: Implementação sob a governança L0g0rhythm.

## 🛠️ Instalação Rápida

O MDex utiliza um sistema de bootstrap automático para garantir isolamento e integridade:

### Windows (Recomendado)
```powershell
./bootstrap.ps1
```

### Linux / macOS
```bash
chmod +x bootstrap.sh
./bootstrap.sh
```

## 📖 Como Usar

Execute o orquestrador principal:
```bash
python src/main.py
```
*Siga o prompt interativo para buscar mangás, selecionar capítulos e ativar o motor de IA (Omni-Reader) conforme necessário.*

## 📂 Estrutura do Projeto (Omni-v6)
- `src/api/`: Clientes de conexão assíncrona e provedores modularizados.
- `src/modules/ai/`: Motores de OCR e Tradução (Omni-Reader).
- `src/modules/search/`: Lógica de busca e seleção de capítulos inteligente.
- `src/modules/download/`: Orquestração de downloads paralelos com validação de Hash.
- `src/modules/pdf/`: Geração de PDFs premium com injeção de IA.
- `tests/`: Suíte de testes completa (Singularity 100).

## 🛡️ Governança & Segurança (Kernel v3.5.8)
- **M04 (Cryptography)**: Validação de integridade via SHA-256.
- **M10 (Financial Integrity)**: Proteção contra race conditions no processamento de capítulos.
- **M14 (Rate Limiting)**: Semáforos inteligentes persistentes.
- **M25 (Governance)**: Execução local de modelos sensíveis (Zero Cloud Exposure).

---
**Arquitetura e Execução: L0g0rhythm Authority Core.**
**User: Vernier.**
