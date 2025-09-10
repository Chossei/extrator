import streamlit as st

@st.dialog('Adicione até 5 variáveis para a busca', width='large')
def adicionar_variavel():
    """
    Formulário dentro de um diálogo para o usuário adicionar até 5 variáveis,
    especificando nome, descrição e tipo para cada uma.
    """
    variaveis_coletadas = []
    OPCOES_TIPO = ["Texto", "Número sem casas decimais", "Número com casas decimais"]
    # Usamos st.form para agrupar os inputs. O envio só ocorre ao clicar no botão.
    with st.form(key='form_variaveis'):
        st.write("Preencha os campos para as variáveis que deseja extrair. Deixe o nome em branco para ignorar a linha.")
        st.divider()

        # Loop para criar 5 linhas de inputs para as variáveis
        for i in range(5):
            col1, col2 = st.columns([1, 3])
            with col1:
                # Usamos uma chave única e descritiva para cada input
                st.text_input(
                    label='Nome da variável',
                    key=f'nome_{i}',  # Chave única: 'nome_0', 'nome_1', etc.
                    placeholder=f'Variável {i+1}'
                )
                
                # Trocamos text_input por selectbox para o usuário escolher uma opção
                st.selectbox(
                    label='Formato da variável',
                    options=OPCOES_TIPO,
                    key=f'tipo_{i}' # Chave única
                )
            with col2:
                st.text_area(
                    label='Descrição da variável',
                    key=f'descricao_{i}', # Chave única e obrigatória
                    placeholder='O que esta variável representa?'
                )
        
        # O botão que, quando clicado, envia todos os dados do formulário de uma vez
        submitted = st.form_submit_button('Concluir e Adicionar Variáveis')

    # Após o envio do formulário, processamos os dados
    if submitted:
        # Loop para ler os dados de cada uma das 5 linhas de inputs
        for i in range(5):
            # Acessamos os valores usando as chaves que definimos, através do st.session_state
            nome_variavel = st.session_state[f'nome_{i}']

            # Só adicionamos a variável à lista se o usuário tiver preenchido o nome
            if nome_variavel:
                variavel = {
                    'nome': nome_variavel,
                    'descricao': st.session_state[f'descricao_{i}'],
                    'tipo': st.session_state[f'tipo_{i}']
                }
                variaveis_coletadas.append(variavel)
        
        # A função retorna a lista de dicionários com as variáveis preenchidas
        st.rerun() # O rerun() é importante para fechar o diálogo e atualizar a tela principal

    return variaveis_coletadas
            
