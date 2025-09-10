import streamlit as st
from paginas.funcoes import adicionar_variavel

st.title('Extrator de Dados')
st.markdown('Selecione as variáveis de interesse e extraia os respectivos dados do seu arquivo PDF!')
 

if st.button('Clique aqui'):
    adicionar_variavel()