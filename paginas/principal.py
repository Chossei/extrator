import streamlit as st
from paginas.funcoes import adicionar_variavel

st.title('Extrator de Dados')
st.markdown('Selecione as variáveis de interesse e extraia os respectivos dados do seu arquivo PDF!')
 

if 'lista_de_variaveis' not in st.session_state:
        st.session_state.lista_de_variaveis = []
        st.subheader("Variáveis configuradas:")
        st.table(st.session_state.lista_de_variaveis)
else:
        st.info("Nenhuma variável foi adicionada ainda.")

if st.button('Clique aqui'):
    adicionar_variavel()