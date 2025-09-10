import streamlit as st
import time

@st.dialog('📝 Adicionar Novas Variáveis', width='large')
def adicionar_variavel():
    """
    Formulário dentro de um diálogo para o usuário adicionar até 5 variáveis,
    especificando nome, descrição e tipo para cada uma.
    A submissão só é permitida se pelo menos uma variável for nomeada.
    """
        # --- O Formulário ---
    with st.form(key="variaveis_form"):
        st.write("Preencha os campos para as variáveis que deseja extrair. Deixe o nome em branco para ignorar a linha.")
        st.divider()

        OPCOES_TIPO = ["Texto", "Número sem casas decimais", "Número com casas decimais"]

        # Loop para criar 5 linhas de inputs para as variáveis
        for i in range(5):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.text_input(label=f'Nome da Variável {i+1}', key=f'nome_{i}')
                st.selectbox(label='Formato', options=OPCOES_TIPO, key=f'tipo_{i}')
            with col2:
                st.text_area(label='Descrição', key=f'descricao_{i}', height=150)
            st.divider()

        # --- O SELETOR DE AÇÃO ---
        acao = st.radio(
            "Após adicionar, o que você deseja fazer?",
            ("Adicionar e continuar preenchendo", "Concluir e voltar para a tela inicial"),
            key="acao_escolhida",
            horizontal=True, width='stretch'
        )

        # --- BOTÃO ÚNICO DE SUBMISSÃO ---
        submitted = st.form_submit_button("Prosseguir", use_container_width=True)

    # --- LÓGICA APÓS A SUBMISSÃO ---
    if submitted:
        variaveis_coletadas = []
        pelo_menos_uma_preenchida = False
        
        # Coleta os dados de todas as linhas preenchidas
        for i in range(5):
            nome_variavel = st.session_state[f'nome_{i}']
            if nome_variavel:
                pelo_menos_uma_preenchida = True
                variavel = {
                    'nome': nome_variavel,
                    'descricao': st.session_state[f'descricao_{i}'],
                    'tipo': st.session_state[f'tipo_{i}']
                }
                variaveis_coletadas.append(variavel)

        # Validação: verifica se pelo menos uma foi preenchida
        if not pelo_menos_uma_preenchida:
            st.error("Erro: Você deve preencher o nome de pelo menos uma variável.")
        else:
            # Adiciona as variáveis coletadas à lista principal na sessão
            st.session_state.lista_de_variaveis.extend(variaveis_coletadas)
            
            acao_selecionada = st.session_state.acao_escolhida

            if acao_selecionada == "Adicionar e continuar preenchendo":
                st.success(f"{len(variaveis_coletadas)} variável(is) adicionada(s)! Os campos foram mantidos caso queira editá-los ou pode preencher os campos vazios para adicionar mais.")
                # O script continua e o formulário permanece na tela

            elif acao_selecionada == "Concluir e voltar para a tela inicial":
                # Para fechar o "diálogo" e atualizar a tela principal, usamos o rerun
                # (Em um st.dialog(), isso fecharia o popup)
                st.success("Ação concluída!")
                with st.spinner("Voltando para a tela inicial..."):
                    time.sleep(1)
                st.rerun()

          
