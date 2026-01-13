import streamlit as st
import time
import pandas as pd
import numpy as np
import io
import json
import tempfile
import os
from google import genai
from google.genai import types

@st.dialog('📝 Adicionar Novas Variáveis', width='large')
def adicionar_variavel():
    """
    Formulário dentro de um diálogo para o usuário adicionar até 4 variáveis,
    especificando nome, descrição e tipo para cada uma.
    A submissão só é permitida se pelo menos uma variável for nomeada.
    """
        # --- O Formulário ---
    with st.form(key="variaveis_form"):
        st.write("Preencha os campos para as variáveis que deseja extrair. Deixe o nome em branco para ignorar a linha.")
        st.divider()

        OPCOES_TIPO = ["Texto", "Número sem casas decimais", "Número com casas decimais"]

        # Loop para criar 5 linhas de inputs para as variáveis
        for i in range(4):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.text_input(label=f'Nome da Variável {i+1}', key=f'nome_{i}')
                st.selectbox(label='Formato', options=OPCOES_TIPO, key=f'tipo_{i}')
            with col2:
                st.text_area(label='Descrição', key=f'descricao_{i}', height=150)
            st.divider()

        # --- O SELETOR DE AÇÃO ---
        acao = st.radio(
            "Após adicionar, o que você deseja fazer?",
            ("Adicionar e continuar preenchendo", "Concluir e voltar para a tela inicial"),
            key="acao_escolhida",
            horizontal=True, width='stretch'
        )

        # --- BOTÃO ÚNICO DE SUBMISSÃO ---
        submitted = st.form_submit_button("Prosseguir", use_container_width=True)

    # --- LÓGICA APÓS A SUBMISSÃO ---
    if submitted:
        variaveis_coletadas = []
        pelo_menos_uma_preenchida = False
        
        # Coleta os dados de todas as linhas preenchidas
        for i in range(4):
            nome_variavel = st.session_state[f'nome_{i}']
            if nome_variavel:
                pelo_menos_uma_preenchida = True
                variavel = {
                    'nome': nome_variavel,
                    'descricao': st.session_state[f'descricao_{i}'],
                    'tipo': st.session_state[f'tipo_{i}']
                }
                variaveis_coletadas.append(variavel)

        # Validação: verifica se pelo menos uma foi preenchida
        if not pelo_menos_uma_preenchida:
            st.error("Erro: Você deve preencher o nome de pelo menos uma variável.")
        else:
            # Adiciona as variáveis coletadas à lista principal na sessão
            st.session_state.lista_de_variaveis.extend(variaveis_coletadas)
            
            acao_selecionada = st.session_state.acao_escolhida

            if acao_selecionada == "Adicionar e continuar preenchendo":
                st.success(f"{len(variaveis_coletadas)} variável(is) adicionada(s)! Preencha os campos novamente para adicionar mais variáveis.")
                # O script continua e o formulário permanece na tela

            elif acao_selecionada == "Concluir e voltar para a tela inicial":
                st.success("Ação concluída!")
                with st.spinner("Voltando para a tela inicial..."):
                    time.sleep(1)
                st.rerun()

def estruturador_atualizado(pdf, variaveis):
    esquema = {
    "type": "ARRAY",
    "items": {
      "type": "OBJECT",
      "properties": {
        # Este dicionário começará vazio
      },
      "required": [
        # Esta lista começará vazia
      ]
    }
    }

    for var in variaveis:
      nome = var['nome']
      tipo = 'STRING' if var['tipo'] == 'Texto' else 'NUMBER'
      descricao = var['descricao']
      esquema['items']['properties'][nome] = {
          'type': tipo,
          'description': descricao
      }
      
      esquema['items']['required'].append(nome)


    # Modelo ---------------

    client = genai.Client(api_key = st.secrets['GEMINI_API_KEY'])

    prompt = """Você é um assistente de IA especialista em extração de dados de documentos. Sua tarefa é analisar o documento fornecido para extrair informações, formatando a saída como um único objeto JSON que segue estritamente o schema fornecido.
    REGRAS DE INTERPRETAÇÃO DO DOCUMENTO:
    -Foco Principal: O objetivo é encontrar todas as informações sobre o indivíduo principal do documento. Reúna dados de todas as partes relevantes para construir um perfil completo.
    -Fontes de Dados: Analise tanto as tabelas quanto os parágrafos para coletar os dados. As informações podem estar espalhadas por todo o documento.
    -Associação de Dados: Utilize os cabeçalhos das tabelas e o contexto do texto para associar corretamente as informações aos campos do schema.
    -Exclusão: Ignore informações genéricas de cabeçalhos, rodapés e seções de referências bibliográficas do documento.

    REGRAS DE GERAÇÃO DO OBJETO JSON:
    -Valores Ausentes: Se uma informação para um campo do schema não for encontrada no documento, o valor para esse campo deve ser a string "Não encontrado".
    -Formatação de Strings: Todas as strings no JSON final devem iniciar com letra maiúscula.
    -Limpeza do Conteúdo: O conteúdo extraído deve ser limpo, sem conter caracteres de formatação (como Markdown |, ---, *, etc.).
        """
    
    # Lógica para a API File
    # Se maior de 10MB, utiliza API para grandes arquivos
    tamanho_arquivo = pdf.size
    limiar = 5 * 1048576

    if tamanho_arquivo < limiar:
        response = client.models.generate_content(
            model = 'gemini-3-flash-preview',
            contents = [
                types.Part.from_bytes(
                    data = pdf.getvalue(),
                    mime_type = 'application/pdf'
                ),
                prompt
            ],
            config = {
                'response_mime_type': 'application/json',
                'response_schema': esquema
            }
        )
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf.getvalue())
            caminho_arquivo = tmp_file.name

        try:
            conteudo_pdf = client.files.upload(
                file = caminho_arquivo
            )

            response = client.models.generate_content(
                model = 'gemini-3-flash-preview',
                contents = [conteudo_pdf, prompt],
                config = {
                    'response_mime_type' : 'application/json',
                    'response_schema' : esquema
                }
            )
        finally:
            os.remove(caminho_arquivo)

    return json.loads(response.text) 
