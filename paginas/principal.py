import streamlit as st
import numpy as np
from paginas.funcoes import (
    adicionar_variavel,
    extrator_texto,
    estruturador
)

st.title('Extrator de Dados')
st.markdown('Selecione as variáveis de interesse e extraia os respectivos dados do seu arquivo PDF!')
st.divider() 

if 'lista_de_variaveis' not in st.session_state:
    st.session_state.lista_de_variaveis = []

st.subheader('Variáveis Atualmente Configuradas para Busca')
if st.session_state.lista_de_variaveis:
    estado = True
    st.table(st.session_state.lista_de_variaveis)
else:
    estado = False
    st.info('Nenhuma variável foi adicionada ainda.')

if st.button('Adicionar variáveis', use_container_width=True):
    adicionar_variavel()

argumento_extrator = st.radio('O arquivo PDF contém...', key='opa', options = ['texto', 'imagens', 'texto/imagens'],
horizontal = True)
pdf = st.file_uploader(label = "", accept_multiple_files=False, type = 'pdf')


if pdf and st.session_state.lista_de_variaveis:
    if st.button(label = 'Gerar base de dados', key = 'submeter', use_container_width=True):
        with st.spinner(text = 'Extraindo texto do pdf...', width='stretch'):
            texto = extrator_texto(pdf, imagem = argumento_extrator)
            st.success('Pronto! A extração foi realizada com sucesso.')
        with st.spinner('Estruturando as variáveis configuradas...', width='stretch', show_time = True):    
            dados = estruturador(texto, variaveis = st.session_state.lista_de_variaveis)
            st.write(dados)
            st.success('Ótimo! As variáveis configuradas foram encontradas!')
        dados_csv = dados.to_csv(index=False).encode('utf-8')
        numero = np.random.randint(0, 1000)
        st.download_button(label='Baixar a base de dados', data = dados_csv, use_container_width=True,
        file_name = f'base_{numero}.csv')