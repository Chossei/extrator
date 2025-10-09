import streamlit as st
import pandas as pd
from paginas.funcoes_firebase import (
    verificar_existencia_modelos,
    buscar_nomes_dos_modelos,
    buscar_variaveis_de_modelo,
    criar_base
)

# --- CONFIGURAÇÃO DA PÁGINA E TÍTULO ---
st.set_page_config(layout="wide")
st.title("📊 Histórico de Extrações")
st.caption("Visualize e baixe as bases de dados consolidadas para cada um dos seus modelos.")

# --- LÓGICA PRINCIPAL ---
if not verificar_existencia_modelos():
    st.info("Você ainda não criou nenhum modelo. Vá para a página principal para começar.")
    st.stop()

# --- CONTAINER DE SELEÇÃO ---
with st.container(border=True):
    modelos = buscar_nomes_dos_modelos()
    
    selecionado = st.selectbox(
        "Selecione um modelo para visualizar seu histórico de extrações:",
        options=modelos,
        index=None,
        placeholder="Selecione um modelo..."
    )

# --- CONTAINER DE RESULTADOS (só aparece após a seleção) ---
if selecionado:
    # UX: Adiciona um spinner para dar feedback de carregamento
    with st.spinner(f"Buscando todos os dados do modelo '{selecionado}'..."):
        dataframe = criar_base(nome_modelo_usado=selecionado)

    # Verifica se a busca retornou um DataFrame válido
    if dataframe is not None:
        # UX: Trata o caso de um modelo sem extrações
        if dataframe.empty:
            st.info(f"Nenhuma extração foi encontrada para o modelo '{selecionado}' ainda.")
        else:
            # UI: Organiza a exibição em um container
            with st.container(border=True):
                st.header(f"Resultados para: {selecionado}")

                # UI: Usa métricas para dar um resumo rápido
                col1, col2 = st.columns(2)
                col1.metric("Total de registros encontrados", len(dataframe))
                col2.metric("N° de variáveis do modelo", len(variaveis_do_modelo))
                st.divider()

                # UI: Usa tabs para separar a visualização dos dados e das variáveis
                tab_dados, tab_variaveis = st.tabs(["Visualização da Base de Dados", "Variáveis do Modelo"])

                with tab_dados:
                    st.dataframe(dataframe, use_container_width=True, hide_index=True)
                
                with tab_variaveis:
                    st.subheader("Variáveis usadas nesta extração:")
                    variaveis = pd.DataFrame(buscar_variaveis_de_modelo(nome_do_modelo=selecionado))
                    # UI: Usa st.dataframe para consistência visual
                    st.dataframe(variaveis, use_container_width=True, hide_index=True)
                
                # Prepara os dados para download (fazemos isso uma vez aqui)
                dados_csv = dataframe.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label = "📥 Baixar Base Completa (.csv)",
                    data=dados_csv,
                    file_name=f'base_{selecionado}.csv',
                    use_container_width=True
                )
    else:       
        st.error("Ocorreu um erro ao buscar os dados. Tente novamente.")
