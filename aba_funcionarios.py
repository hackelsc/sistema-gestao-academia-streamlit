"""Aba "Funcionários" do Sistema de Gestão da Academia.

Contém as funções auxiliares de código e exibição de tabela, além da
função aba_funcionarios(), que monta toda a interface (cadastrar, ver,
buscar, editar e remover funcionários) usada em app_academia.py.

Usa o banco TinyDB próprio dos funcionários (funcionarios.json).
"""

import streamlit as st
from tinydb import TinyDB, Query
from datetime import date

q = Query()
db = TinyDB("funcionarios.json", encoding="utf-8", ensure_ascii=False)
todas_atribuicoes = ["Professor", "Auxiliar serviços gerais", "Recepção"]


def contador_codigo():
    """Calcula o próximo código disponível.

    Pega o maior código já cadastrado no banco e soma 1; se não houver
    nenhum funcionário cadastrado, retorna 1.
    """
    todos = db.all()
    if todos:
        maior = max(item["codigo"] for item in todos)
        codigo = maior + 1
        return codigo
    else:
        return 1


def exibir_tabela(resultados):
    """Exibe uma lista de funcionários (do banco) como tabela formatada.

    Retorna True se algo foi mostrado, ou False se a lista veio vazia.
    Usa st.dataframe() em vez de st.table() porque ele aceita ajuste de
    tamanho de colunas.
    """
    if resultados:
        tabela = [
            {"codigo": item["codigo"], "nome": item["nome"], "rua": item["rua"], "numero": item["numero"],
             "complemento": item["complemento"], "nascimento": item["nascimento"], "telefone": item["telefone"],
             "atribuicao": item["atribuicao"],
             "data_admissao": item["data_admissao"], "status": "Ativo" if item["status"] else "Inativo"}
            for item in resultados
        ]
        st.dataframe(
            tabela,
            column_config={
                "codigo": st.column_config.Column(width="small"),
                "nome": st.column_config.Column(width="large"),
                "rua": st.column_config.Column(width="large"),
                "numero": st.column_config.Column(width="small"),
                "complemento": st.column_config.Column(),
                "nascimento": st.column_config.Column(),
                "telefone": st.column_config.Column(width="medium"),
                "atribuicao": st.column_config.Column(),
                "data_admissao": st.column_config.Column(),
                "status": st.column_config.Column(width="small")
            },
            hide_index=True
        )
        return True
    else:
        return False


def aba_funcionarios():
    """Monta a interface completa da aba "Funcionários" para uso em app_academia.py.

    Menu principal com as opções: cadastrar, ver cadastrados, buscar,
    editar e remover funcionários. Ao trocar de opção no menu, os dados
    que estavam em edição/remoção são descartados do session_state. O
    formulário de cadastro limpa os campos após o envio
    (clear_on_submit=True); o de edição mantém os dados visíveis, já
    preenchidos com os valores atuais do cadastro.
    """
    escolha = st.selectbox("O que você deseja fazer?",
                           ["escolha uma opção", "cadastrar funcionário", "ver funcionários cadastrados", "buscar funcionário",
                            "editar cadastro", "remover cadastro"],
                           key="menu_principal_func")

    if escolha != "editar cadastro":
        st.session_state.pop("funcionario_editando", None)
        st.session_state.pop("opcoes_edicao", None)
    if escolha != "remover cadastro":
        st.session_state.pop("funcionario_remover", None)
        st.session_state.pop("opcoes_remocao", None)

    if escolha == "cadastrar funcionário":
        with st.form("form_cadastro", clear_on_submit = True):
            nome = st.text_input("Nome completo:")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                rua = st.text_input("Rua:")
            with col2:
                numero = st.text_input("Número:")
            with col3:
                complemento = st.text_input("Complemento:")
            col4, col5 = st.columns(2)
            with col4:
                nascimento = st.date_input("Data de nascimento:", value=date(2000, 1, 1),
                                           min_value=date(1900, 1, 1), max_value=date.today(),
                                           format="DD/MM/YYYY")
            with col5:
                telefone = st.text_input("Telefone:")
            col6, col7 = st.columns(2)
            with col6:
                atribuicao = st.selectbox("Atribuição:", todas_atribuicoes)
            with col7:
                status = st.selectbox("Status:", ["ativo", "inativo"])
            data_admissao = date.today()
            enviado = st.form_submit_button("Cadastrar")
            if enviado:
                if not nome:
                    st.error("O campo nome é obrigatório.")
                else:
                    db.insert({"codigo": contador_codigo(), "nome": nome, "rua": rua, "numero": numero,
                               "complemento": complemento, "nascimento": nascimento.isoformat(), "telefone": telefone,
                               "atribuicao": atribuicao,
                               "data_admissao": data_admissao.isoformat(), "status": True if status == "ativo" else False})
                    st.toast("Cadastro realizado com sucesso!")

    elif escolha == "ver funcionários cadastrados":
        ver = db.all()
        if ver:
            exibir_tabela(ver)
        else:
            st.warning("Nenhum funcionário cadastrado.")

    elif escolha == "buscar funcionário":
        escolha_buscar = st.selectbox("Escolha um critério de busca:",
                                      ["código do funcionário", "nome", "atribuição"])

        if escolha_buscar == "código do funcionário":
            registration_number = st.number_input("Digite o código do funcionário:", min_value=0, step=1)
            if st.button("Buscar"):
                resultado = db.search(q.codigo == registration_number)
                if resultado:
                    exibir_tabela(resultado)
                else:
                    st.warning("Código não encontrado.")

        if escolha_buscar == "nome":
            name = st.text_input("Digite o nome:")
            if st.button("Buscar"):
                resultado = db.search(q.nome.test(lambda x: name.lower() in x.lower()))
                if resultado:
                    exibir_tabela(resultado)
                else:
                    st.warning("Nome não encontrado.")

        if escolha_buscar == "atribuição":
            assignment = st.selectbox("Escolha a atribuição:", todas_atribuicoes)
            if st.button("Buscar"):
                resultado = db.search(q.atribuicao == assignment)
                if resultado:
                    exibir_tabela(resultado)
                else:
                    st.warning("Não existem cadastros para essa atribuição.")

    elif escolha == "editar cadastro":
        escolha_editar = st.selectbox("Buscar por:", ["código do funcionário", "nome"], key="buscar_por_editar_func")
        if escolha_editar == "código do funcionário":
            codigo_editar = st.number_input("Insira o número do código do funcionário que deseja editar:", min_value=0, step=1)
            if st.button("Buscar cadastro"):
                resultado = db.get(q.codigo == codigo_editar)
                if resultado:
                    st.session_state["funcionario_editando"] = resultado
                else:
                    st.warning("Código não encontrado.")

        elif escolha_editar == "nome":
            nome_editar = st.text_input("Digite o nome:", key="nome_editar_func")
            if nome_editar:  # busca ao vivo, direto do que foi digitado (sem botão)
                resultados = db.search(q.nome.test(lambda x: nome_editar.lower() in x.lower()))
                if resultados:
                    rotulos = []
                    for funcionario in resultados:
                        rotulos.append(f"{funcionario['codigo']} — {funcionario['nome']}")
                    rotulo_escolhido = st.selectbox("Selecione o funcionário:", rotulos, key="select_editar_func")
                    for funcionario in resultados:
                        if f"{funcionario['codigo']} — {funcionario['nome']}" == rotulo_escolhido:
                            funcionario_escolhido = funcionario
                    st.session_state["funcionario_editando"] = funcionario_escolhido
                else:
                    st.warning("Nome não encontrado.")

        if "funcionario_editando" in st.session_state:
            resultado = st.session_state["funcionario_editando"]
            with st.form("form_editar"):
                novo_nome = st.text_input("Nome completo:", value=resultado["nome"], key=f"nome_{resultado['codigo']}")
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    novo_rua = st.text_input("Rua:", value=resultado["rua"], key=f"rua_{resultado['codigo']}")
                with col2:
                    novo_numero = st.text_input("Número:", value=resultado["numero"], key=f"numero_{resultado['codigo']}")
                with col3:
                    novo_complemento = st.text_input("Complemento:", value=resultado["complemento"], key=f"complemento_{resultado['codigo']}")
                col4, col5 = st.columns(2)
                with col4:
                    nova_data_nascimento = st.date_input("Data de nascimento:",
                                                         value=date.fromisoformat(resultado["nascimento"]), key=f"nascimento_{resultado['codigo']}")
                with col5:
                    novo_telefone = st.text_input("Telefone:", value=resultado["telefone"], key=f"telefone_{resultado['codigo']}")
                col6, col7 = st.columns(2)
                with col6:
                    # selectbox não aceita "value"/"default", só "index" — por isso usa .index() pra descobrir em
                    # que posição de todas_atribuicoes está o valor atual do funcionário.
                    nova_atribuicao = st.selectbox("Atribuição:", todas_atribuicoes, index=todas_atribuicoes.index(resultado["atribuicao"]), key=f"atribuicao_{resultado['codigo']}")
                with col7:
                    novo_status = st.selectbox("Status:", ["ativo", "inativo"], index=0 if resultado["status"] else 1, key=f"status_{resultado['codigo']}")
                enviado = st.form_submit_button("Salvar alterações")
                if enviado:
                    db.update({"nome": novo_nome, "rua": novo_rua, "numero": novo_numero,
                               "complemento": novo_complemento,
                               "telefone": novo_telefone,
                               "nascimento": nova_data_nascimento.isoformat(),
                               "atribuicao": nova_atribuicao,
                               "status": novo_status == "ativo"},
                              q.codigo == resultado["codigo"])
                    st.toast("Cadastro alterado com sucesso!")

    elif escolha == "remover cadastro":
        escolha_remover = st.selectbox("Buscar por:", ["código do funcionário", "nome"], key="buscar_por_remover_func")

        if escolha_remover == "código do funcionário":
            codigo_deletar = st.number_input("Insira o número do código do funcionário que deseja remover:",
                                                min_value=0, step=1)
            if st.button("Buscar cadastro"):
                resultado = db.get(q.codigo == codigo_deletar)
                if resultado:
                    exibir_tabela([resultado])
                    st.session_state["funcionario_remover"] = resultado
                else:
                    st.warning("Código não encontrado.")

        elif escolha_remover == "nome":
            nome_remover = st.text_input("Digite o nome:", key="nome_remover_func")
            if nome_remover:  # busca ao vivo, direto do que foi digitado (sem botão)
                resultados = db.search(q.nome.test(lambda x: nome_remover.lower() in x.lower()))
                if resultados:
                    rotulos = []
                    for funcionario in resultados:
                        rotulos.append(f"{funcionario['codigo']} — {funcionario['nome']}")
                    rotulo_escolhido = st.selectbox("Selecione o funcionário:", rotulos, key="select_remover_func")
                    for funcionario in resultados:
                        if f"{funcionario['codigo']} — {funcionario['nome']}" == rotulo_escolhido:
                            funcionario_escolhido = funcionario
                    st.session_state["funcionario_remover"] = funcionario_escolhido
                    exibir_tabela([funcionario_escolhido])
                else:
                    st.warning("Nome não encontrado.")

        if "funcionario_remover" in st.session_state:
            resultado = st.session_state["funcionario_remover"]
            if st.button("Deletar cadastro"):
                if resultado:
                    db.remove(q.codigo == resultado["codigo"])
                    st.toast("Cadastro removido com sucesso!")
