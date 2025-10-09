import streamlit as st
import pandas as pd
from paginas.funcoes_firebase import(
    verificar_existencia_modelos,
    buscar_nomes_dos_modelos,
    buscar_variaveis_de_modelo,
    criar_base
)

st.title('Visualize as extrações feitas anteriormente')

if verificar_existencia_modelos():
    modelos = buscar_nomes_dos_modelos()
    selecionado = st.selectbox('Clique abaixo para selecionar o modelo a visualizar',
    options = modelos)

    if selecionado:
        variaveis = pd.DataFrame(buscar_variaveis_de_modelo(nome_do_modelo = selecionado))
        st.subheader(f'Variáveis configuradas até o momento para o modelo "{selecionado}" ')
        with st.expander('Clique aqui para expandir'):
            st.table(variaveis, border = False)
        if st.button(f'Visualizar base de dados associada ao modelo "{selecionado}"', use_container_width=True):
            dataframe = criar_base(nome_modelo_usado = selecionado)
            st.dataframe(dataframe)
                        
            # Oferece o download
            dados_csv = dataframe.to_csv(index=False).encode('utf-8')
            st.download_button(
                label='Baixar a base de dados',
                data=dados_csv,
                file_name=f'base_{selecionado}.csv',
                use_container_width=True
            )

else:
    st.info('Nenhum modelo de variáveis foi criado ainda. Retorne à página inicial e crie o seu primeiro modelo.')
