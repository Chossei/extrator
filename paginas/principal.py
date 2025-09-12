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


st.subheader('Upload do arquivo PDF para extração dos dados')
pdf = st.file_uploader(label = "", accept_multiple_files=False, type = 'pdf')

if pdf is not None:
    texto = extrator_texto(pdf, imagem = True)
    dados = estruturador(texto, variaveis = st.session_state.lista_de_variaveis)
    numero = np.random.randint(0, 1000)
    st.download_button(label='Base de dados', data = dados, use_container_width=True,
    file_name = f'base_{numero}')