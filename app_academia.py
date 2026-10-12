"""Ponto de entrada do Sistema de Gestão da Academia.

Para rodar o programa:
    streamlit run app_academia.py -- clicar tab depois

Para parar o streamlit:
    1 - deixar a página do navegador aberta
    2 - clicar Ctrl+C

Para apagar o que tem no terminal:
    Ctrl+L

st.set_page_config() define o título da aba do navegador, o ícone e o
layout da página; st.title() desenha o título grande no topo da página
em si (diferente do page_title, que só aparece na aba do navegador).
"""

import streamlit as st
from aba_alunos import aba_alunos
from aba_funcionarios import aba_funcionarios
from aba_turmas import aba_turmas

st.set_page_config(page_title="Academia", page_icon="🏋️", layout="centered")

st.title("Sistema de Gestão da Academia")

aba1, aba2, aba3 = st.tabs(["Alunos", "Funcionários", "Turmas"])

with aba1:
    aba_alunos()
with aba2:
    aba_funcionarios()
with aba3:
    aba_turmas()
