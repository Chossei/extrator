import streamlit as st

@st.dialog('Adicione até 5 variáveis para a busca', width='large')
def adicionar_variavel():
    """
    Formulário dentro de um diálogo para o usuário adicionar até 5 variáveis,
    especificando nome, descrição e tipo para cada uma.
    A submissão só é permitida se pelo menos uma variável for nomeada.
    """
    OPCOES_TIPO = ["Texto", "Número sem casas decimais", "Número com casas decimais"]

    with st.form(key='form_variaveis'):
        st.info("É obrigatório preencher pelo menos a primeira variável (Nome, Descrição e Formato).")
        st.divider()

        # Loop para criar 5 linhas de inputs para as variáveis
        for i in range(5):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.text_input(
                    label='Nome da variável',
                    key=f'nome_{i}',
                    placeholder=f'Variável {i+1}'
                )
                st.selectbox(
                    label='Formato da variável',
                    options=OPCOES_TIPO,
                    key=f'tipo_{i}'
                )
            with col2:
                st.text_area(
                    label='Descrição da variável',
                    key=f'descricao_{i}',
                    placeholder='O que esta variável representa?',
                    height=150
                )
            st.divider()
        
        # Para você ver o session_state em ação!
        # Expanda para ver como os valores são armazenados em tempo real.
        with st.expander("Clique aqui para ver como os dados são armazenados (Depuração)"):
            st.write(st.session_state)
        
        botao_adiciona, botao_conclui = st.columns(2)
        with botao_adiciona:
            submitted = st.form_submit_button('Adicionar Variáveis')
        with botao_conclui:
            concluir = st.button('Concluir')
    
    if submitted:
        variaveis_coletadas = []
        pelo_menos_uma_preenchida = False

        # --- NOVA LÓGICA DE VALIDAÇÃO ---
        # Primeiro, verificamos se algum nome de variável foi preenchido.
        for i in range(5):
            if st.session_state[f'nome_{i}']: # Se o texto não for vazio...
                pelo_menos_uma_preenchida = True
                break # Encontramos um, não precisa checar o resto.

        # Se, após o loop, a flag continuar False, mostramos um erro.
        if not pelo_menos_uma_preenchida:
            st.error("Erro: Você deve preencher o nome de pelo menos uma variável para continuar.")
        else:
            # Se a validação passou, executamos a lógica original.
            for i in range(5):
                nome_variavel = st.session_state[f'nome_{i}']
                if nome_variavel: # Coleta só os que têm nome
                    variavel = {
                        'nome': nome_variavel,
                        'descricao': st.session_state[f'descricao_{i}'],
                        'tipo': st.session_state[f'tipo_{i}']
                    }
                    variaveis_coletadas.append(variavel)
            
            # Use o st.session_state para passar os dados para a aplicação principal
            if 'lista_de_variaveis' not in st.session_state:
                st.session_state.lista_de_variaveis = []
            
            st.session_state.lista_de_variaveis.extend(variaveis_coletadas)
            st.success(f"{len(variaveis_coletadas)} variável(is) adicionada(s) com sucesso!")
    
    if concluir:
        st.rerun()
          
