import streamlit as st
from paginas.funcoes import adicionar_variavel

st.title('Extrator de Dados')
st.markdown('Selecione as variáveis de interesse e extraia os respectivos dados do seu arquivo PDF!')
 

if st.button('Clique aqui'):
    if 'lista_de_variaveis' not in st.session_state:
        st.session_state.lista_de_variaveis = []
    adicionar_variavel()