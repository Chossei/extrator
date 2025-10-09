import streamlit as st
import numpy as np
from paginas.funcoes import (
    adicionar_variavel,
    extrator_texto,
    estruturador
)

from paginas.funcoes_firebase import (
    inicializar_firebase,
    verificar_existencia_modelos,
    buscar_nomes_dos_modelos,
    buscar_variaveis_de_modelo,
    salvar_variaveis,
    salvar_extracao,
    criar_base
)

st.title('Extrator de Dados')
st.markdown('Selecione as variáveis de interesse e extraia os respectivos dados do seu arquivo PDF!')
st.divider() 


# Verificando se existem modelos de variáveis já prontos
opcoes = ['Nenhum']
existencia_modelo = verificar_existencia_modelos()
if existencia_modelo:
    modelos = buscar_nomes_dos_modelos()
    opcoes.extend(modelos)

nome_do_modelo = st.selectbox('Selecione um modelo de variáveis para continuar ou crie outro abaixo.',
    options = opcoes)

####
st.subheader('Variáveis atualmente configuradas para busca')
####

if nome_do_modelo != 'Nenhum':
    variaveis = buscar_variaveis_de_modelo(nome_do_modelo)
    st.session_state.lista_de_variaveis = variaveis
    st.table(st.session_state.lista_de_variaveis)
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Adicionar variáveis', use_container_width=True):
            adicionar_variavel()
    with col2:
        if st.button('Atualizar modelo', use_container_width=True):
            atualizar_variaveis_do_modelo(nome_do_modelo, novas_variaveis = st.session_state.lista_de_variaveis)
else:
    st.session_state.lista_de_variaveis = []
    st.session_state.button = False
    st.session_state.button2 = True
    if not st.session_state.button:
        st.info('Nenhuma variável foi adicionada ainda.')
    else:
        st.table(st.session_state.lista_de_variaveis)
        titulo_do_modelo = st.text_input(label = 'Insira o nome do modelo das variáveis adicionadas *', key = 'titulo')
        if len(titulo_do_modelo) > 0:
            st.session_state.button2 = True
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Adicionar variáveis', use_container_width=True):
            adicionar_variavel()
            st.session_state.button = False
    with col2:
        if st.button('Salvar novo modelo de variáveis', use_container_width=True,
        disabled = st.session_state.button2):
            salvar_variaveis(variaveis = st.session_state.lista_de_variaveis, titulo = titulo_do_modelo)
            
argumento_extrator = 'texto/imagens'
pdf = st.file_uploader(label = "Faça o upload do seu arquivo PDF", accept_multiple_files=False, type = 'pdf')

if pdf and st.session_state.lista_de_variaveis and len(titulo_do_modelo) > 0:
    if st.button(label = 'Gerar base de dados', key = 'submeter', use_container_width=True):
        with st.spinner(text = 'Extraindo texto do pdf...', width='stretch', show_time=True):
            texto = extrator_texto(pdf, imagem = argumento_extrator)
            st.success('Pronto! A extração foi realizada com sucesso.')
        with st.spinner('Estruturando as variáveis configuradas...', width='stretch', show_time = True):    
            dados = estruturador(texto, variaveis = st.session_state.lista_de_variaveis)
            salvar_extracao(nome_modelo_usado = titulo_do_modelo, nome_arquivo = pdf.name, dados_extraidos = dados)
            dataframe = criar_base(nome_modelo_usado = titulo_do_modelo)
            st.write(dataframe)
            st.success('Ótimo! As variáveis configuradas foram encontradas!')
        dados_csv = dataframe.to_csv(index=False).encode('utf-8')
        numero = np.random.randint(0, 1000)
        st.download_button(label='Baixar a base de dados', data = dados_csv, use_container_width=True,
        file_name = f'base_{numero}.csv')


# if 'lista_de_variaveis' not in st.session_state:
#     st.session_state.lista_de_variaveis = []

# st.subheader('Variáveis Atualmente Configuradas para Busca')
# if st.session_state.lista_de_variaveis:
#     estado = True
#     st.table(st.session_state.lista_de_variaveis)
# else:
#     estado = False
#     st.info('Nenhuma variável foi adicionada ainda.')

# if st.button('Adicionar variáveis', use_container_width=True):
#     adicionar_variavel()

# argumento_extrator = st.radio('O arquivo PDF contém...', key='opa', options = ['texto', 'imagens', 'texto/imagens'],
# horizontal = True)
# pdf = st.file_uploader(label = "Faça o upload do seu arquivo PDF", accept_multiple_files=False, type = 'pdf')


# if pdf and st.session_state.lista_de_variaveis:
#     if st.button(label = 'Gerar base de dados', key = 'submeter', use_container_width=True):
#         with st.spinner(text = 'Extraindo texto do pdf...', width='stretch', show_time=True):
#             texto = extrator_texto(pdf, imagem = argumento_extrator)
#             st.success('Pronto! A extração foi realizada com sucesso.')
#         with st.spinner('Estruturando as variáveis configuradas...', width='stretch', show_time = True):    
#             dados = estruturador(texto, variaveis = st.session_state.lista_de_variaveis)
#             st.write(dados)
#             st.success('Ótimo! As variáveis configuradas foram encontradas!')
#         dados_csv = dados.to_csv(index=False).encode('utf-8')
#         numero = np.random.randint(0, 1000)
#         st.download_button(label='Baixar a base de dados', data = dados_csv, use_container_width=True,
#         file_name = f'base_{numero}.csv')