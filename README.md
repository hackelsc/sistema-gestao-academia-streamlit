# Sistema de Gestão da Academia (Streamlit)

Aplicação web para gerenciar uma academia: cadastro de alunos, funcionários e turmas, com busca, edição e remoção de registros. Projeto final do curso de Python, feito com [Streamlit](https://streamlit.io/) e [TinyDB](https://tinydb.readthedocs.io/).

## Funcionalidades

**Alunos**
- Cadastrar, listar, buscar (por matrícula, nome ou modalidade), editar e remover alunos
- Resumo na listagem: quantidade de alunos ativos e receita mensal esperada com as mensalidades

**Funcionários**
- Cadastrar, listar, buscar (por código, nome ou atribuição), editar e remover funcionários

**Turmas**
- Cadastrar turmas com modalidade, dias da semana, horários, professor e alunos
- Listar turmas e buscar as turmas de um aluno pelo nome
- Ver a lista de chamada da turma (em ordem alfabética), editar e remover a turma

## Tecnologias

- Python 3
- Streamlit (interface web)
- TinyDB (banco de dados em arquivos JSON)

## Como executar

1. Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/hackelsc/sistema-gestao-academia-streamlit.git
cd sistema-gestao-academia-streamlit
```

2. (Opcional, recomendado) Crie e ative um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS
```

3. Instale as dependências:

```bash
pip install streamlit tinydb
```

4. Rode a aplicação **de dentro da pasta do projeto** (os bancos são lidos pelo caminho relativo):

```bash
streamlit run app_academia.py
```

O navegador abre automaticamente. Para parar, use `Ctrl+C` no terminal.

## Estrutura do projeto

```
├── app_academia.py        # ponto de entrada: monta o título e as três abas
├── aba_alunos.py          # aba "Alunos"
├── aba_funcionarios.py    # aba "Funcionários"
├── aba_turmas.py          # aba "Turmas"
├── alunos.json            # banco de dados dos alunos
├── funcionarios.json      # banco de dados dos funcionários
└── turmas.json            # banco de dados das turmas
```

## Dados

Cada entidade tem seu próprio banco (`alunos.json`, `funcionarios.json` e `turmas.json`), todos em UTF-8. Os arquivos incluídos no repositório contêm cadastros de exemplo, usados para testar o sistema.

As turmas guardam apenas o código do professor e as matrículas dos alunos; os nomes são buscados nos bancos de funcionários e alunos na hora de exibir.

## Autora

Raquel — [github.com/hackelsc](https://github.com/hackelsc)
