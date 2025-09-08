import streamlit as st


paginas = {
    'Menu' : [st.Page('paginas/principal.py', title = 'Extração Dinâmica de Dados', default = True)]
}


pg = st.navigation(paginas)
pg.run()