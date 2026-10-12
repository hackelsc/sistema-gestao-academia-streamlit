"""Aba "Alunos" do Sistema de Gestão da Academia.

Contém as funções auxiliares de matrícula e exibição de tabela, além da
função aba_alunos(), que monta toda a interface (cadastrar, ver, buscar,
editar e remover alunos) usada em app_academia.py.

Usa o banco TinyDB próprio dos alunos (alunos.json).
"""

import streamlit as st
from tinydb import TinyDB, Query
from datetime import date

q = Query()
db = TinyDB("alunos.json", encoding="utf-8", ensure_ascii=False)
todas_modalidades = ["Natação", "Hidroginástica", "Musculação"]


def contador_matricula():
    """Calcula a próxima matrícula disponível.

    Pega a maior matrícula já cadastrada no banco e soma 1; se não houver
    nenhum aluno cadastrado, retorna 1.
    """
    todos = db.all()
    if todos:
        maior = max(item["matricula"] for item in todos)
        matricula = maior + 1
        return matricula
    else:
        return 1


def exibir_tabela(resultados):
    """Exibe uma lista de alunos (do banco) como tabela formatada.

    Retorna True se algo foi mostrado, ou False se a lista veio vazia.
    Usa st.dataframe() em vez de st.table() porque ele aceita ajuste de
    tamanho de colunas.
    """
    if resultados:
        tabela = [
            {"matricula": item["matricula"], "nome": item["nome"], "rua": item["rua"], "numero": item["numero"],
             "complemento": item["complemento"], "nascimento": item["nascimento"], "telefone": item["telefone"],
             **{opcao: 1 if opcao in item["modalidade"] else 0 for opcao in todas_modalidades},
             "mensalidade": f"{item['mensalidade']:.2f}",
             "data_matricula": item["data_matricula"], "status": "Ativo" if item["status"] else "Inativo"}
            for item in resultados
        ]
        st.dataframe(
            tabela,
            column_config={
                "matricula": st.column_config.Column(width="small"),
                "nome": st.column_config.Column(width="large"),
                "rua": st.column_config.Column(width="large"),
                "numero": st.column_config.Column(width="small"),
                "complemento": st.column_config.Column(),
                "nascimento": st.column_config.Column(),
                "telefone": st.column_config.Column(width="medium"),
                "Natação": st.column_config.Column(width="small"),
                "Hidroginástica": st.column_config.Column(),
                "Musculação": st.column_config.Column(),
                "mensalidade": st.column_config.Column(),
                "data_matricula": st.column_config.Column(),
                "status": st.column_config.Column(width="small")
            },
            hide_index=True
        )
        return True
    else:
        return False


def aba_alunos():
    """Monta a interface completa da aba "Alunos" para uso em app_academia.py.

    Menu principal com as opções: cadastrar, ver cadastrados, buscar,
    editar e remover alunos. Ao trocar de opção no menu, os dados que
    estavam em edição/remoção são descartados do session_state. Os
    formulários de cadastro limpam os campos após o envio
    (clear_on_submit=True); os de edição mantêm os dados visíveis, já
    preenchidos com os valores atuais do cadastro.
    """
    escolha = st.selectbox("O que você deseja fazer?",
                           ["escolha uma opção", "cadastrar aluno", "ver alunos cadastrados", "buscar aluno",
                            "editar cadastro", "remover cadastro"],
                            key="menu_principal")

    if escolha != "editar cadastro":
        st.session_state.pop("aluno_editando", None)
        st.session_state.pop("opcoes_edicao", None)
    if escolha != "remover cadastro":
        st.session_state.pop("aluno_remover", None)
        st.session_state.pop("opcoes_remocao", None)


    if escolha == "cadastrar aluno":
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
            col6, col7, col8 = st.columns(3)
            with col6:
                modalidade = st.multiselect("Modalidades:", todas_modalidades)
            with col7:
                mensalidade = st.number_input("Mensalidade:", min_value=0.00, value=0.00, step=0.01, format="%.2f")
            with col8:
                status = st.selectbox("Status:", ["ativo", "inativo"])
            data_matricula = date.today()
            enviado = st.form_submit_button("Cadastrar")
            if enviado:
                if not nome:
                    st.error("O campo nome é obrigatório.")
                else:
                    db.insert({"matricula": contador_matricula(), "nome": nome, "rua": rua, "numero": numero,
                               "complemento": complemento, "nascimento": nascimento.isoformat(), "telefone": telefone,
                               "modalidade": modalidade, "mensalidade": mensalidade,
                               "data_matricula": data_matricula.isoformat(), "status": True if status == "ativo" else False})
                    st.toast("Cadastro realizado com sucesso!")
                    st.balloons()

    elif escolha == "ver alunos cadastrados":
        ver = db.all()
        if ver:
            exibir_tabela(ver)
            quantidade_ativos = 0
            total_mensalidades = 0
            for aluno in ver:
                if aluno["status"]:
                    quantidade_ativos = quantidade_ativos + 1
                    total_mensalidades = total_mensalidades + aluno["mensalidade"]

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Alunos ativos", quantidade_ativos)
            with col2:
                st.metric("Receita mensal esperada (mensalidades)", f"R$ {total_mensalidades:.2f}")
        else:
            st.warning("Nenhum aluno cadastrado.")

    elif escolha == "buscar aluno":
        escolha_buscar = st.selectbox("Escolha um critério de busca:",
                                      ["matrícula", "nome", "modalidade"])

        if escolha_buscar == "matrícula":
            registration_number = st.number_input("Digite a matrícula:", min_value=0, step=1)
            if st.button("Buscar"):
                resultado = db.search(q.matricula == registration_number)
                if resultado:
                    exibir_tabela(resultado)
                else:
                    st.warning("Matrícula não encontrada.")

        elif escolha_buscar == "nome":
            name = st.text_input("Digite o nome:")
            if st.button("Buscar"):
                resultado = db.search(q.nome.test(lambda x: name.lower() in x.lower()))
                if resultado:
                    exibir_tabela(resultado)
                else:
                    st.warning("Nome não encontrado.")

        elif escolha_buscar == "modalidade":
            modality = st.selectbox("Escolha a modalidade:", todas_modalidades)
            if st.button("Buscar"):
                # não dá pra usar search(q.modalidade == modality) porque "modalidade" no banco é uma lista de
                # valores, e "modality" é uma única string — por isso usa .test() com lambda, que verifica se
                # "modality" está contido na lista.
                resultado = db.search(q.modalidade.test(lambda x: modality in x))
                if resultado:
                    exibir_tabela(resultado)
                else:
                    st.warning("Não existem cadastros para essa modalidade.")

    elif escolha == "editar cadastro":
        escolha_editar = st.selectbox("Buscar por:", ["matrícula", "nome"], key="buscar_por_editar")

        if escolha_editar == "matrícula":
            matricula_editar = st.number_input("Insira o número da matrícula do cadastro que deseja editar:", min_value=0, step=1)
            if st.button("Buscar cadastro"):
                resultado = db.get(q.matricula == matricula_editar)
                if resultado:
                    st.session_state["aluno_editando"] = resultado
                else:
                    st.warning("Matrícula não encontrada.")

        elif escolha_editar == "nome":
            nome_editar = st.text_input("Digite o nome:", key="nome_editar")
            if nome_editar:  # busca ao vivo, direto do que foi digitado (sem botão)
                resultados = db.search(q.nome.test(lambda x: nome_editar.lower() in x.lower()))
                if resultados:
                    rotulos = []
                    for aluno in resultados:
                        rotulos.append(f"{aluno['matricula']} — {aluno['nome']}")
                    rotulo_escolhido = st.selectbox("Selecione o aluno:", rotulos, key="select_editar")
                    for aluno in resultados:
                        if f"{aluno['matricula']} — {aluno['nome']}" == rotulo_escolhido:
                            aluno_escolhido = aluno
                    st.session_state["aluno_editando"] = aluno_escolhido
                else:
                    st.warning("Nome não encontrado.")

        if "aluno_editando" in st.session_state:
            resultado = st.session_state["aluno_editando"]
            with st.form("form_editar"):
                novo_nome = st.text_input("Nome completo:", value=resultado["nome"], key=f"nome_{resultado['matricula']}")
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    novo_rua = st.text_input("Rua:", value=resultado["rua"], key=f"rua_{resultado['matricula']}")
                with col2:
                    novo_numero = st.text_input("Número:", value=resultado["numero"], key=f"numero_{resultado['matricula']}")
                with col3:
                    novo_complemento = st.text_input("Complemento:", value=resultado["complemento"], key=f"complemento_{resultado['matricula']}")
                col4, col5 = st.columns(2)
                with col4:
                    nova_data_nascimento = st.date_input("Data de nascimento:", value=date.fromisoformat(resultado["nascimento"]), key=f"nascimento_{resultado['matricula']}")
                with col5:
                    novo_telefone = st.text_input("Telefone:", value=resultado["telefone"], key=f"telefone_{resultado['matricula']}")
                col6, col7, col8 = st.columns(3)
                with col6:
                    novas_modalidades = st.multiselect("Modalidades:", todas_modalidades, default=resultado["modalidade"], key=f"modalidade_{resultado['matricula']}")
                with col7:
                    nova_mensalidade = st.number_input("Mensalidade:", value=resultado["mensalidade"], key=f"mensalidade_{resultado['matricula']}")
                with col8:
                    novo_status = st.selectbox("Status:", ["ativo", "inativo"], index=0 if resultado["status"] else 1, key=f"status_{resultado['matricula']}")
                enviado = st.form_submit_button("Salvar alterações")
                if enviado:
                    db.update({"nome": novo_nome, "rua": novo_rua, "numero": novo_numero,
                        "complemento": novo_complemento,
                        "telefone": novo_telefone,
                        "nascimento": nova_data_nascimento.isoformat(),
                        "modalidade": novas_modalidades,
                        "mensalidade": nova_mensalidade,
                        "status": novo_status == "ativo"},
                        q.matricula == resultado["matricula"])
                    st.toast("Cadastro alterado com sucesso!")



    elif escolha == "remover cadastro":
        escolha_remover = st.selectbox("Buscar por:", ["matrícula", "nome"], key="buscar_por_remover")

        if escolha_remover == "matrícula":
            matricula_deletar = st.number_input("Insira o número da matrícula do cadastro que deseja remover:", min_value=0, step=1)
            if st.button("Buscar cadastro"):
                resultado = db.get(q.matricula == matricula_deletar)
                if resultado:
                    exibir_tabela([resultado])
                    st.session_state["aluno_remover"] = resultado
                else:
                    st.warning("Matrícula não encontrada.")

        elif escolha_remover == "nome":
            nome_remover = st.text_input("Digite o nome:", key="nome_remover")
            if nome_remover:  # busca ao vivo, direto do que foi digitado (sem botão)
                resultados = db.search(q.nome.test(lambda x: nome_remover.lower() in x.lower()))
                if resultados:
                    rotulos = []
                    for aluno in resultados:
                        rotulos.append(f"{aluno['matricula']} — {aluno['nome']}")
                    rotulo_escolhido = st.selectbox("Selecione o aluno:", rotulos, key="select_remover")
                    for aluno in resultados:
                        if f"{aluno['matricula']} — {aluno['nome']}" == rotulo_escolhido:
                            aluno_escolhido = aluno
                    st.session_state["aluno_remover"] = aluno_escolhido
                    exibir_tabela([aluno_escolhido])
                else:
                    st.warning("Nome não encontrado.")

        if "aluno_remover" in st.session_state:
            resultado = st.session_state["aluno_remover"]
            if st.button("Deletar cadastro"):
                if resultado:
                    db.remove(q.matricula == resultado["matricula"])
                    st.toast("Cadastro removido com sucesso!")
