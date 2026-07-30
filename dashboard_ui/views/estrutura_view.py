import streamlit as st
from dashboard_ui import api_client
from dashboard_ui.components.cascade_selectors import render_cascade_selectors


def render_estrutura_view():
    st.header("⚙️ Gestão de Estrutura & Equipamentos")
    st.caption("Adicione ou atualize os equipamentos, fornecedores, fábricas e linhas de produção.")

    tab_add_sis, tab_fornecedores, tab_fabrica_linha = st.tabs([
        "➕ Adicionar Sistema",
        "🤝 Gerir Fornecedores",
        "🏭 Adicionar Fábrica / Linha"
    ])

    with tab_add_sis:
        st.subheader("Cadastrar Novo Sistema / Equipamento")
        st.write("Selecione a localização na hierarquia fabril e preencha o nome do novo equipamento.")

        selected_fabrica_id, selected_linha_id, _ = render_cascade_selectors(
            key_prefix="add_sis",
            show_all_option=False
        )

        fornecedores = api_client.get_fornecedores()
        forn_options = {"Sem Fornecedor": None}
        for f in fornecedores:
            forn_options[f"{f['nome']} ({f.get('contacto', 'Sem contacto')})"] = f["id"]

        with st.form("form_add_sistema"):
            nome_sistema = st.text_input("Nome do Sistema", placeholder="Ex: Baumer Inspection D14")
            forn_label = st.selectbox("Fornecedor Responsável", options=list(forn_options.keys()))

            submeter = st.form_submit_button("Criar Sistema")

            if submeter:
                if not selected_linha_id:
                    st.error("Por favor, selecione uma linha válida.")
                elif not nome_sistema.strip():
                    st.warning("Por favor, introduza o nome do sistema.")
                else:
                    payload = {
                        "nome": nome_sistema.strip(),
                        "linha_id": selected_linha_id,
                        "fornecedor_id": forn_options[forn_label]
                    }
                    resp = api_client.criar_sistema(payload)
                    if resp.status_code in (200, 201):
                        st.success(f"✅ Sistema '{nome_sistema}' criado com sucesso!")
                    else:
                        st.error(f"Erro ao criar sistema: {resp.text}")

    with tab_fornecedores:
        st.subheader("Lista de Fornecedores Registados")
        fornecedores = api_client.get_fornecedores()
        if fornecedores:
            st.dataframe(fornecedores, use_container_width=True)

        col_f1, col_f2 = st.tabs(["➕ Criar Fornecedor", "✏️ Editar Fornecedor"])

        with col_f1:
            with st.form("form_add_fornecedor"):
                nome_f = st.text_input("Nome do Fornecedor")
                contacto_f = st.text_input("Contacto / Email")
                sub_f = st.form_submit_button("Registar Fornecedor")

                if sub_f:
                    if not nome_f.strip():
                        st.warning("Insira o nome do fornecedor.")
                    else:
                        resp = api_client.criar_fornecedor({"nome": nome_f.strip(), "contacto": contacto_f.strip()})
                        if resp.status_code in (200, 201):
                            st.success(f"✅ Fornecedor '{nome_f}' registado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro: {resp.text}")

        with col_f2:
            if fornecedores:
                forn_dict = {f"{f['nome']} (ID #{f['id']})": f for f in fornecedores}
                sel_f_label = st.selectbox("Selecione o Fornecedor a Editar", options=list(forn_dict.keys()))
                f_obj = forn_dict[sel_f_label]

                with st.form(f"form_edit_forn_{f_obj['id']}"):
                    edit_nome_f = st.text_input("Novo Nome", value=f_obj["nome"])
                    edit_contacto_f = st.text_input("Novo Contacto", value=f_obj.get("contacto", ""))
                    sub_edit_f = st.form_submit_button("Guardar Alterações")

                    if sub_edit_f:
                        resp = api_client.editar_fornecedor(f_obj["id"], {"nome": edit_nome_f.strip(), "contacto": edit_contacto_f.strip()})
                        if resp.status_code == 200:
                            st.success("✅ Fornecedor atualizado!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao editar: {resp.text}")

    with tab_fabrica_linha:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("Adicionar Fábrica")
            with st.form("form_add_fabrica"):
                nome_fabrica = st.text_input("Nome da Fábrica", placeholder="Ex: PIGMENT")
                loc_fabrica = st.text_input("Localização", placeholder="Ex: PFF / BOF")
                sub_fab = st.form_submit_button("Criar Fábrica")

                if sub_fab:
                    if not nome_fabrica.strip():
                        st.warning("Introduza o nome da fábrica.")
                    else:
                        # POST /api/fabricas
                        import requests
                        resp = requests.post(
                            f"{api_client.API_URL}/fabricas",
                            json={"nome": nome_fabrica.strip(), "localizacao": loc_fabrica.strip()},
                            headers=api_client.get_headers()
                        )
                        if resp.status_code in (200, 201):
                            st.success("✅ Fábrica criada com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro: {resp.text}")

        with col_c2:
            st.subheader("Adicionar Linha")
            fabricas = api_client.get_fabricas()
            fab_dict = {f["nome"]: f["id"] for f in fabricas}

            with st.form("form_add_linha"):
                nome_linha = st.text_input("Nome da Linha", placeholder="Ex: Linha 5")
                fab_label = st.selectbox("Fábrica Associada", options=list(fab_dict.keys()) if fab_dict else ["Sem fábricas"])
                sub_lin = st.form_submit_button("Criar Linha")

                if sub_lin:
                    if not nome_linha.strip() or not fab_dict:
                        st.warning("Preencha o nome da linha e selecione uma fábrica.")
                    else:
                        import requests
                        resp = requests.post(
                            f"{api_client.API_URL}/linhas",
                            json={"nome": nome_linha.strip(), "fabrica_id": fab_dict[fab_label]},
                            headers=api_client.get_headers()
                        )
                        if resp.status_code in (200, 201):
                            st.success("✅ Linha criada com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro: {resp.text}")
