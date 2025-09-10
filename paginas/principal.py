import streamlit as st
from paginas.funcoes import adicionar_variavel

st.title('Extrator de Dados')
st.markdown('Selecione as variáveis de interesse e extraia os respectivos dados do seu arquivo PDF!')
st.divider() 

if 'lista_de_variaveis' not in st.session_state:
    st.session_state.lista_de_variaveis = []

st.header('Variáveis Atualmente Configuradas para Busca')
if st.session_state.lista_de_variaveis:
    st.table(st.session_state.lista_de_variaveis)
else:
    st.info('Nenhuma variável foi adicionada ainda.')

if st.button('Adicionar variáveis'):
    adicionar_variavel()
