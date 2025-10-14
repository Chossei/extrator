import streamlit as st
import numpy as np
import pandas as pd
from paginas.funcoes import (
    adicionar_variavel,
    estruturador_atualizado
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

# CÓDIGO CORRIGIDO -----------------

# --- SELEÇÃO E CRIAÇÃO DE MODELOS ---
# Verificando se existem modelos de variáveis já prontos
opcoes = ['Nenhum (Criar novo)']
if verificar_existencia_modelos():
    modelos = buscar_nomes_dos_modelos()
    opcoes.extend(modelos)

nome_do_modelo_selecionado = st.selectbox(
    'Selecione um modelo de variáveis para continuar ou crie um novo.',
    options=opcoes
)

# CORREÇÃO 1: Usar uma única variável para o modelo ativo
modelo_ativo = ""

st.subheader('Variáveis atualmente configuradas para busca')

if nome_do_modelo_selecionado != 'Nenhum (Criar novo)':
    # --- LÓGICA PARA MODELO EXISTENTE ---
    modelo_ativo = nome_do_modelo_selecionado
    
    # Busca as variáveis do modelo selecionado e as armazena na sessão
    if 'modelo_carregado' not in st.session_state or st.session_state.modelo_carregado != modelo_ativo:
        variaveis_db = buscar_variaveis_de_modelo(modelo_ativo)
        st.session_state.lista_de_variaveis = variaveis_db
        st.session_state.modelo_carregado = modelo_ativo

    with st.expander(label = 'Clique aqui para visualizá-las',expanded=False, icon = '🔎'):
        variaveis_df = pd.DataFrame(st.session_state.get('lista_de_variaveis', [])) 
        st.dataframe(variaveis_df, hide_index = True, width = 'stretch')
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Adicionar variáveis', use_container_width=True):
            adicionar_variavel() # O ideal é que esta tela permita editar também
    with col2:
        if st.button('Salvar alterações no modelo', use_container_width=True):
            # A função de atualizar ainda não existe, mas a chamada seria aqui
            atualizar_variaveis_do_modelo(modelo_ativo, st.session_state.lista_de_variaveis)
            st.success("Modelo atualizado!") # Placeholder

else:
    # --- LÓGICA PARA NOVO MODELO ---
    # CORREÇÃO 2: Simplificação radical do gerenciamento de estado
    if 'lista_de_variaveis' not in st.session_state or nome_do_modelo_selecionado == 'Nenhum (Criar novo)' and st.session_state.get('modelo_carregado') != 'Nenhum':
        st.session_state.lista_de_variaveis = []
        st.session_state.modelo_carregado = 'Nenhum'
    
    if not st.session_state.lista_de_variaveis:
        st.info('Nenhuma variável foi adicionada ainda.')
    else:
        with st.expander(label = 'Clique aqui para visualizá-las',expanded=False, icon = '🔎'):
            variaveis_df = pd.DataFrame(st.session_state.lista_de_variaveis)
            st.dataframe(variaveis_df, hide_index = True, width = 'stretch')

    titulo_novo_modelo = st.text_input('Insira o nome do novo modelo *', key='titulo_novo')
    if titulo_novo_modelo:
        modelo_ativo = titulo_novo_modelo

    col1, col2 = st.columns(2)
    with col1:
        if st.button('Adicionar variáveis', use_container_width=True):
            adicionar_variavel()
    with col2:
        # Simplificando a lógica do botão 'disabled'
        if st.button('Salvar novo modelo', use_container_width=True, disabled=not (titulo_novo_modelo and st.session_state.lista_de_variaveis)):
            salvar_variaveis(variaveis=st.session_state.lista_de_variaveis, titulo=titulo_novo_modelo)

# --- UPLOAD E EXTRAÇÃO ---
st.divider()
pdf = st.file_uploader(label="Faça o upload do seu arquivo PDF", type='pdf')

# CORREÇÃO 1 (continuação): A condição agora usa a variável 'modelo_ativo'
if pdf and st.session_state.get('lista_de_variaveis') and modelo_ativo:
    if st.button('Salvar informações no banco de dados', use_container_width=True):
        
        with st.spinner('Extraindo as informações no documento...', show_time = True):
            dados_extraidos = estruturador_atualizado(pdf = pdf, variaveis = st.session_state.lista_de_variaveis)
            # CORREÇÃO 1 e 3: Usar 'modelo_ativo' e salvar a extração
            salvar_extracao(nome_modelo_usado=modelo_ativo, nome_arquivo=pdf.name, dados_extraidos=dados_extraidos)
            st.success('Ótimo! As variáveis configuradas foram encontradas e armazenadas!')
            # CORREÇÃO 3: Criar o DataFrame diretamente dos dados extraídos, sem nova consulta
            if dados_extraidos:     
                dataframe = criar_base(modelo_ativo)
                st.write(dataframe)
                
                # Oferece o download
                dados_csv = dataframe.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label='Baixar a base de dados',
                    data=dados_csv,
                    file_name=f'base_{modelo_ativo}.csv',
                    use_container_width=True
                )
            else:
                st.warning("Nenhuma das variáveis configuradas foi encontrada no texto.")
else:
    st.warning("É necessário selecionar um modelo (ou criar um novo com nome e variáveis) e fazer o upload de um PDF para continuar.")