# Organizador de Termos de Responsabilidade de TI 📂

Script em Python para organizar automaticamente documentos de inventário e termos de responsabilidade (entrega, devolução e termos assinados) em pastas estruturadas por colaborador e número de controle da nota/termo.

---

## 🚀 Funcionalidades

- **Identificação Inteligente por Regex**: Extrai automaticamente o número da nota e o nome do colaborador a partir do padrão de nomenclatura do arquivo.
- **Normalização de Nomes**: Remove acentos e caracteres especiais para evitar duplicidades em nomes e pastas.
- **Fase de Simulação (Dry-Run)**: Antes de realizar qualquer cópia, o script lista todos os arquivos identificados, pendências e a estrutura de pastas prevista.
- **Operação Segura**: Os arquivos originais **nunca são alterados ou excluídos**; o script utiliza cópia com preservação de metadados (`shutil.copy2`).
- **Verificação de Duplicatas**: Não sobrescreve documentos já existentes no destino.
- **Configuração Flexível**: O diretório base pode ser informado via linha de comando (`--base`), variável de ambiente (`TERMOS_BASE_DIR`) ou diretamente pelo terminal interativo.

---

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Nenhuma dependência externa necessária (utiliza apenas a biblioteca padrão do Python: `pathlib`, `re`, `shutil`, `unicodedata`, `argparse`).

---

## 📁 Estrutura de Pastas Esperada

O diretório base de trabalho deve conter as pastas de origem:

```text
NOTEBOOKS/
├── Entrega de ativos/
│   └── TR-NOT-0085-COLABORADOR-NOT-0085-TI-Entrega-Ativo.pdf
├── Devolução de ativos/
│   └── TR-NOT-0090-OUTRO-COLABORADOR-Devolucao.pdf
└── Assinados/
    └── NOT-0065-COLABORADOR-ASSINADO.pdf
```

### Estrutura Gerada

O script criará o diretório `Organizados por colaborador/` com subpastas categorizadas:

```text
NOTEBOOKS/
└── Organizados por colaborador/
    ├── 65-COLABORADOR/
    │   └── Assinados/
    │       └── NOT-0065-COLABORADOR-ASSINADO.pdf
    └── 85-COLABORADOR/
        └── Entrega de ativos/
            └── TR-NOT-0085-COLABORADOR-NOT-0085-TI-Entrega-Ativo.pdf
```

---

## 🛠️ Como Utilizar

### 1. Execução Interativa

Execute o script diretamente. Se o caminho base não for informado, você poderá digitá-lo no terminal:

```bash
python organizar_termos.py
```

### 2. Passando o Diretório por Linha de Comando

```bash
python organizar_termos.py --base "C:\Caminho\Para\NOTEBOOKS"
```

### 3. Modo Direto (Sem confirmação manual)

Útil para agendamento via cron ou automações:

```bash
python organizar_termos.py --base "C:\Caminho\Para\NOTEBOOKS" --yes
```

---

## 🏷️ Padrões de Nomes Suportados

O script reconhece nomenclaturas no formato:
- `NOT-0065-Nome-Sobrenome-NOTE-96.pdf`
- `TR-NOT-0085-NOME-SOBRENOME-NOT-0085-TI-Entrega-Ativo.pdf`
- `TR-NOT-0120-NOME-SOBRENOME-ASSINADO.pdf`

Sufixos como `NOTE`, `TI`, `TR`, `ENTREGA`, `DEVOLUÇÃO` e `ASSINADO` são automaticamente filtrados do nome do colaborador.

---

## 🛡️ Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais informações.
