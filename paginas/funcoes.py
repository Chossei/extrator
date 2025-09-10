import streamlit as st


@st.dialog('Adicione uma variável para a busca', width = 'large')
def adicionar_variavel():
    with st.form(key = 'xxx'):
        variaveis = [None] * 5
        nome = [None] * 5
        descricao = [None] * 5
        tipo = [None] * 5
        for indice in range(5):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                nome[indice] = st.text_input(key = f'xx{indice+1}', label = 'Nome da variável')
            with col2:
                descricao[indice] = st.text_area(label = 'Descrição breve da variável')
            with col3:
                tipo[indice] = st.text_input(key =f'xx{indice}', label = 'Formato da variável')
        
        
    if st.form_submit_button('Concluir'):
        for indice_2 in range(5):
            variaveis.append({
                'nome' : nome[indice_2],
                'descricao': descricao[indice_2],
                'tipo': tipo[indice_2]
            })
            
