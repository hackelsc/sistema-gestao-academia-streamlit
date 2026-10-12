"""Aba "Turmas" do Sistema de Gestão da Academia.

Contém as funções auxiliares de código e chamada, além da função
aba_turmas(), que monta toda a interface (cadastrar, ver e buscar turmas,
com edição e remoção) usada em app_academia.py.

Usa três bancos TinyDB próprios: turmas.json, funcionarios.json (para
achar os professores) e alunos.json (para achar os alunos ativos).
mapa_professores e mapa_alunos traduzem entre o código/matrícula salvo
no banco e o rótulo "código — nome" / "matrícula — nome" mostrado nos
formulários.
"""

import streamlit as st
from tinydb import TinyDB, Query
from datetime import date

q = Query()
db = TinyDB("turmas.json", encoding="utf-8", ensure_ascii=False)
db_funcionarios = TinyDB("funcionarios.json", encoding="utf-8", ensure_ascii=False)
db_alunos = TinyDB("alunos.json", encoding="utf-8", ensure_ascii=False)

todas_modalidades = ["Natação", "Hidroginástica", "Musculação"]
dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"]
horarios = ["7:00", "7:30", "8:00", "8:30", "9:00", "9:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00"]
professores = db_funcionarios.search(q.atribuicao == "Professor")
mapa_professores = {f"{p['codigo']} — {p['nome']}": p["codigo"] for p in professores}
alunos = db_alunos.search(q.status == True)
mapa_alunos = {f"{a['matricula']} — {a['nome']}": a["matricula"] for a in alunos}


def contador_codigo():
    """Calcula o próximo código disponível.

    Pega o maior código já cadastrado no banco e soma 1; se não houver
    nenhuma turma cadastrada, retorna 1.
    """
    todos = db.all()
    if todos:
        maior = max(item["codigo"] for item in todos)
        codigo = maior + 1
        return codigo
    else:
        return 1


def exibir_chamada(turma):
    """Exibe o cabeçalho e a lista de chamada de uma turma (do banco).

    Traduz o código do professor e as matrículas dos alunos para os
    respectivos nomes, e monta a chamada em ordem alfabética pelo nome,
    numerada a partir de 1. Retorna True se algo foi mostrado, ou False
    se a turma veio vazia.
    """
    if turma:
        if turma["professor"]:
            professor = db_funcionarios.get(q.codigo == turma["professor"])
            nome_professor = professor["nome"]
        else:
            nome_professor = "Sem professor definido"

        nomes_alunos = []
        for matricula in turma["matriculas"]:
            aluno = db_alunos.get(q.matricula == matricula)
            nomes_alunos.append(aluno["nome"])

        st.subheader(turma["modalidade"])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Professor:** {nome_professor}")
        with col2:
            st.write(f"**Dia:** {', '.join(turma['dia_semana'])}")
        with col3:
            st.write(f"**Horário:** {turma['horario_inicio']} às {turma['horario_fim']}")

        st.divider()

        alunos_turma = list(zip(turma["matriculas"], nomes_alunos))
        alunos_turma.sort(key=lambda item: item[1])

        chamada = []
        contador = 1
        for matricula, nome in alunos_turma:
            chamada.append({"#": contador, "matrícula": matricula, "nome": nome})
            contador += 1

        st.dataframe(chamada, hide_index=True)
        return True
    else:
        return False


def aba_turmas():
    """Monta a interface completa da aba "Turmas" para uso em app_academia.py.

    Menu principal com as opções: cadastrar, ver cadastradas e buscar
    turmas. As duas últimas preenchem "turma_selecionada" no
    session_state, que é usada mais abaixo (fora do menu) para exibir a
    chamada da turma escolhida e permitir editá-la ou removê-la; ao sair
    dessas telas, a seleção/edição é descartada. O formulário de
    cadastro limpa os campos após o envio (clear_on_submit=True).
    """
    escolha = st.selectbox("O que você deseja fazer?",
                           ["escolha uma opção", "cadastrar turma", "ver turmas cadastradas", "buscar turma"],
                           key="menu_principal_turma")
    if escolha not in ("ver turmas cadastradas", "buscar turma"):
        st.session_state.pop("turma_selecionada", None)
        st.session_state.pop("turma_editando", None)

    if escolha == "cadastrar turma":
        with st.form("form_cadastro", clear_on_submit=True):
            modalidade = st.selectbox("Modalidade:", todas_modalidades)
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                dia = st.multiselect("Dia da semana:", dias_semana)
            with col2:
                horario_inicio = st.selectbox("Início:", horarios)
            with col3:
                horario_fim = st.selectbox("Término:", horarios)
            col4, col5 = st.columns([2, 1])
            with col4:
                # o selectbox mostra as chaves (keys) do dicionário (os rótulos "código — nome")
                professor_escolhido = st.selectbox(label="Professor:", options=list(mapa_professores.keys()))
            with col5:
                status = st.selectbox("Status:", ["ativo", "inativo"])
            data_cadastro = date.today()
            alunos_selecionados = st.multiselect("Alunos:", list(mapa_alunos.keys()))
            enviado = st.form_submit_button("Cadastrar")
            if enviado:
                codigo_professor = mapa_professores[professor_escolhido]
                matriculas_selecionadas = [mapa_alunos[rotulo] for rotulo in alunos_selecionados]
                db.insert({"codigo": contador_codigo(), "modalidade": modalidade, "dia_semana": dia, "horario_inicio": horario_inicio,
                           "horario_fim": horario_fim, "professor": codigo_professor, "matriculas": matriculas_selecionadas,
                           "data_cadastro": data_cadastro.isoformat(), "status": True if status == "ativo" else False})
                st.toast("Cadastro realizado com sucesso!")

    elif escolha == "ver turmas cadastradas":
        todas = db.all()
        if todas:
            for t in todas:
                rotulo = f"{t['modalidade']} — {', '.join(t['dia_semana'])} — {t['horario_inicio']} às {t['horario_fim']}"
                if st.button(rotulo, key=f"turma_{t['codigo']}"):
                    st.session_state["turma_selecionada"] = t
        else:
            st.warning("Nenhuma turma cadastrada.")

    elif escolha == "buscar turma":
        nome_aluno_busca = st.text_input("Digite o nome do aluno:")
        if nome_aluno_busca:
            alunos_encontrados = db_alunos.search(q.nome.test(lambda x: nome_aluno_busca.lower() in x.lower()))
            if alunos_encontrados:
                matriculas_encontradas = []
                for a in alunos_encontrados:
                    matriculas_encontradas.append(a["matricula"])

                # busca turmas em que QUALQUER uma dessas matrículas apareça na lista "matriculas" da turma
                turmas_encontradas = db.search(q.matriculas.test(lambda lista: any(m in lista for m in matriculas_encontradas)))
                if turmas_encontradas:
                    for t in turmas_encontradas:
                        rotulo = f"{t['modalidade']} — {', '.join(t['dia_semana'])} — {t['horario_inicio']} às {t['horario_fim']}"
                        if st.button(rotulo, key=f"turma_{t['codigo']}"):
                            st.session_state["turma_selecionada"] = t
                else:
                    st.warning("Esse aluno não está matriculado em nenhuma turma.")
            else:
                st.warning("Nome não encontrado.")

    if "turma_selecionada" in st.session_state:
        turma = st.session_state["turma_selecionada"]
        exibir_chamada(turma)

        col_editar, col_remover = st.columns(2)
        with col_editar:
            if st.button("Editar turma"):
                st.session_state["turma_editando"] = turma
        with col_remover:
            confirmar_remocao = st.checkbox("Tenho certeza que quero remover essa turma",
                                             key=f"confirmar_remover_{turma['codigo']}")
            if st.button("Remover turma"):
                if confirmar_remocao:
                    db.remove(q.codigo == turma["codigo"])
                    st.session_state.pop("turma_selecionada", None)
                    st.toast("Turma removida com sucesso!")
                else:
                    st.warning("Marque a confirmação antes de remover.")

        if "turma_editando" in st.session_state:
            turma = st.session_state["turma_editando"]

            with st.form("form_editar_turma"):
                nova_modalidade = st.selectbox("Modalidade:", todas_modalidades,
                                               index=todas_modalidades.index(turma["modalidade"]))

                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    novo_dia = st.multiselect("Dia da semana:", dias_semana, default=turma["dia_semana"])
                with col2:
                    novo_horario_inicio = st.selectbox("Início:", horarios,
                                                       index=horarios.index(turma["horario_inicio"]))
                with col3:
                    novo_horario_fim = st.selectbox("Término:", horarios,
                                                    index=horarios.index(turma["horario_fim"]))

                col4, col5 = st.columns([2, 1])
                with col4:
                    # o valor salvo (turma["professor"]) é um código, mas as opções do selectbox são rótulos
                    # ("código — nome"); por isso primeiro acha o rótulo correspondente ao código salvo, e só
                    # então usa .index() pra descobrir a posição desse rótulo na lista de opções. Se a turma não
                    # tiver professor (código é None), o índice fica None e o selectbox abre sem seleção.
                    rotulo_professor_atual = None
                    for rotulo, codigo in mapa_professores.items():
                        if codigo == turma["professor"]:
                            rotulo_professor_atual = rotulo

                    indice_professor = list(mapa_professores.keys()).index(
                        rotulo_professor_atual) if rotulo_professor_atual else None

                    novo_professor_escolhido = st.selectbox("Professor:", options=list(mapa_professores.keys()),
                                                            index=indice_professor,
                                                            placeholder="Selecione um professor (opcional)")
                with col5:
                    novo_status = st.selectbox("Status:", ["ativo", "inativo"],
                                               index=0 if turma["status"] else 1)

                # mesmo problema do professor (matrícula salva x rótulo mostrado), mas como é multiselect,
                # resolve com default (lista de valores), sem precisar de índice
                rotulos_alunos_atuais = []
                for rotulo, matricula in mapa_alunos.items():
                    if matricula in turma["matriculas"]:
                        rotulos_alunos_atuais.append(rotulo)

                novos_alunos_selecionados = st.multiselect("Alunos:", list(mapa_alunos.keys()),
                                                           default=rotulos_alunos_atuais)

                enviado_edicao = st.form_submit_button("Salvar alterações")
                if enviado_edicao:
                    if novo_professor_escolhido:
                        novo_codigo_professor = mapa_professores[novo_professor_escolhido]
                    else:
                        novo_codigo_professor = None

                    novas_matriculas = [mapa_alunos[rotulo] for rotulo in novos_alunos_selecionados]

                    db.update({"modalidade": nova_modalidade, "dia_semana": novo_dia,
                               "horario_inicio": novo_horario_inicio, "horario_fim": novo_horario_fim,
                               "professor": novo_codigo_professor, "matriculas": novas_matriculas,
                               "status": novo_status == "ativo"},
                              q.codigo == turma["codigo"])

                    st.toast("Turma atualizada com sucesso!")
                    st.session_state.pop("turma_editando", None)
