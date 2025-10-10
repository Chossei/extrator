import streamlit as st
import time
import pandas as pd
import numpy as np
import google.generativeai as genai
import io
import json
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

# def estruturador(texto, variaveis):
#   """
#   Extrai informações estruturadas de um texto potencialmente contendo **múltiplos indivíduos**,
#   pedindo ao modelo generativo que retorne um *array* JSON onde cada item representa um indivíduo
#   com os campos definidos pelo schema dinâmico gerado via pydantic


#   comportamento principal
#   - monta dinamicamente um schema Pydantic (`DynamicSchema`) a partir de `variaveis`
#   - constrói um prompt mínimo que instrui o modelo a retornar **uma lista** (array) de objetos
#   obedecendo ao schema, cada objeto representando um indivíduo
#   - configura o `generation_config` para esperar `application/json` e `response_schema=list[DynamicSchema]`
#   - retorna `response.text` (string JSON) com o array de indivíduos, cabe ao chamador fazer o parse


#   parâmetros
#   - texto (str): texto bruto proveniente de documentos, pode conter zero, um ou vários indivíduos
#   - variaveis (list[dict]): lista de dicionários com pelo menos as chaves:
#   - 'nome' (str): nome do campo que aparecerá no schema e na saída JSON
#   - 'descricao' (str): (opcional) descrição do campo — nesta versão ela não é enviada ao prompt
#   - 'tipo' (str): tipo esperado: 'string', 'integer', 'float' ou 'boolean' (default 'string')


#   requisitos/assunções
#   - existe um cliente `genai` configurado globalmente e uma variável `api_key` disponível
#   - `create_model` do pydantic está disponível (importado no topo deste arquivo)
#   - o modelo generativo suporta `response_schema` e aceita `list[DynamicSchema]` como saída estruturada


#   retorno
#   - str: conteúdo bruto retornado pelo modelo (geralmente um JSON array). Ex.:
#   '[{"nome": "João", "cpf": "..."}, {"nome": "Maria", "cpf": "..."}]'
#   recomenda-se chamar `json.loads(response.text)` no chamador para obter a lista de objetos


#   notas importantes / boas práticas
#   - o prompt é propositalmente enxuto, não reenvie a descrição das variáveis no corpo do prompt,
#   pois o schema já descreve os campos e descrições longas aumentam o custo de tokens
#   - para permitir rastreabilidade, instruímos o modelo a incluir `nomes_alternativos` e `source_snippet`
#   em cada objeto, caso queira trocar `source_snippet` por offsets (start/end) basta ajustar o texto do prompt
#   - se o texto for muito grande, implemente pré-processamento local (chunking / seleção por parágrafos)
#   para reduzir tokens antes da chamada, ou envie apenas blocos candidatos
#   - depende da qualidade do modelo: para evitar duplicatas/erros peça no prompt que o modelo
#   una menções repetidas num único objeto e liste variações em `nomes_alternativos`


#   exemplo de uso (resumo, sem código de rede):
#   1) defina `variaveis = [{'nome':'nome','tipo':'string'},{'nome':'cpf','tipo':'string'}]
#   2) chame `resp = modelo_google(texto, variaveis)`
#   3) em seguida: `data = json.loads(resp)` -> `data` será uma lista de dicionários


#   limitações
#   - o LLM pode alucinar valores ausentes, portanto sempre valide os campos críticos (ex.: cpf)
#   comparando com o `source_snippet` retornado
#   - se o texto contém muitos indivíduos, controle o tamanho da saída e o custo limitando
#   o número máximo pedido ao modelo via instruções adicionais no prompt


#   changelog / versão
#   - v1.0: documentado, resposta em array de objetos (múltiplos indivíduos)


#   """


#   instrucoes_prompt = f"""
#   Você é um especialista em extração de dados que recebe um texto e o converte em um array JSON de indivíduos.

#   **REGRAS DE INTERPRETAÇÃO DO TEXTO DE ENTRADA:**
#   O texto fornecido pode ser texto corrido, em formato Markdown, ou uma combinação de ambos.
#   1.  **Se o texto for uma tabela Markdown:** Considere que cada linha (após o cabeçalho) representa um indivíduo distinto. Os cabeçalhos da tabela podem ajudar a identificar os campos.
#   2.  **Se o texto for corrido (parágrafos):** Procure por menções a indivíduos dentro da prosa.
#   3. Se o texto tiver uma seção referências, com estruturas do tipo ABNT ou outras, ignore.

#   **REGRAS PARA A SAÍDA JSON:**
#   Após interpretar o texto, gere um único array JSON seguindo estas regras estritas:
#   - O array deve conter exatamente **um objeto por indivíduo distinto** identificado.
#   - **Unicidade:** Não repita indivíduos. Se a mesma pessoa (identificada por CPF, número de processo ou nome normalizado) aparecer várias vezes, una todas as informações em um único objeto JSON.
#   - **Campos:** Para cada objeto, inclua todos os campos solicitados pelo schema JSON.
#   - **Valores Ausentes:** Para campos cujas informações não foram encontradas no texto, preencha o valor com a string "Não encontrado".
#   - **Formato:** Strings devem sempre iniciar com letra maiúscula.
#   - **Limite:** Retorne no máximo 200 objetos.
#   - **Entidades:** Os indivíduos a serem extraídos são sempre seres humanos.
#   - **Limpeza:** A saída final não deve incluir símbolos de formatação Markdown como `|` ou `---`.

#   --- TEXTO PARA ANÁLISE ---
#   {texto}
#   """


#   # 1. Mapeia os tipos de string para tipos reais do Python
#   type_mapping = {
#   'Texto': str,
#   'Número sem casas decimais': int,
#   'Números com casas decimais': float,
#   }


#   # 2. Prepara as definições dos campos para o Pydantic
#   field_definitions = {}
#   for var in variaveis:
#     nome = var['nome']
#     descricao = var.get('descricao', f'Informação sobre {nome}')
#     tipo_py = type_mapping.get(var.get('tipo', 'string').lower(), str)
#     # A tupla (tipo, ...) significa que o campo e obrigatorio.
#     field_definitions[nome] = (tipo_py, Field(..., description=descricao))


#   # 3. Usa create_model do Pydantic para criar a classe do schema
#   DynamicSchema = create_model('DynamicSchema', **field_definitions)


#   print(f"Enviando {len(texto)} caracteres para a API para estruturação.")
#   # configuracao e chamada ao modelo
#   genai.configure(api_key=st.secrets['GEMINI_API_KEY_2'])
#   model = genai.GenerativeModel('gemini-2.5-flash')


#   generation_config = genai.GenerationConfig(
#   response_mime_type='application/json',
#   response_schema=list[DynamicSchema], # agora esperamos um array de objetos (varios individuos)
#   temperature=0.0
#   )


#   response = model.generate_content(
#   instrucoes_prompt,
#   generation_config=generation_config
#   )


#   return json.loads(response.text)          

# def extrator_texto(caminho_arquivo, imagem : str):

#   # caso 1: tentativa de extracao direta de texto
#   if imagem == 'texto':
#     pagina_texto = ''
#     try:
#         leitor = PyPDF2.PdfReader(caminho_arquivo)
#         for pagina in leitor.pages:
#             texto = pagina.extract_text() or ''
#             pagina_texto += texto
#       # caso contrário, caimos para o fluxo de imagens (scanned)
#         return pagina_texto
#     except Exception as e:
#     # se falhar qualquer coisa, prosseguimos para o fluxo de imagens
#         print(f"Erro na extração via PyPDF2: {e}")

#   elif imagem == 'texto/imagens':
#     numero_da_pagina_com_imagem = []
#     limiar_texto = 280

#     try:
#         leitor = PyPDF2.PdfReader(caminho_arquivo)
#         total_paginas = len(leitor.pages)
#         pagina_apenas_texto = ['-'] * total_paginas

#         caminho_arquivo.seek(0)
#         doc_fitz = fitz.open(stream=caminho_arquivo.read(),filetype='pdf')
#         numero_da_pagina = 0
        
#         with st.status(label = 'Processando o PDF...', expanded = False):
#             for pagina in leitor.pages:
#                 texto = pagina.extract_text()
#                 if len(texto.strip()) > limiar_texto:
#                     pagina_apenas_texto[numero_da_pagina] = (f'Página {numero_da_pagina+1}: {texto}')
#                     st.write(f'(PyPDF2) Texto da Página {numero_da_pagina+1} extraída com sucesso.')
#                 else:
#                             # Usar fitz aqui para verificar se contém imagem. Se conter imagem, marca o número da página. Se não, deixa o conteúdo de texto extraído mesmo.
#                     pagina_fitz = doc_fitz.load_page(numero_da_pagina)
#                     if pagina_fitz.get_images(full=True):
#                         st.write(f'(Fitz) Página {numero_da_pagina+1} tem pouco texto E contém imagem. Marcando para OCR.')
#                         numero_da_pagina_com_imagem.append(numero_da_pagina)
#                     else:
#                         # Se não contém imagens, é apenas uma página com pouco texto (ex: folha de rosto, etc).
#                         # Nesse caso, mantemos o pouco texto que foi extraído.
#                         st.write(f'(Fitz) Página {numero_da_pagina+1} tem pouco texto mas NÃO contém imagem. Mantendo texto original.')
#                         pagina_apenas_texto[numero_da_pagina] = (f'Página {numero_da_pagina+1}: {texto}')

#                 numero_da_pagina += 1
#             print(f"PyPDF2 encontrou {numero_da_pagina} páginas no total.")
#             print(f"Páginas marcadas para OCR: {numero_da_pagina_com_imagem}")
#     except Exception as e:
#         print(f"Erro na leitura via PyPDF2: {e}")
#         return 'Não foi possível ler o arquivo.'

#     if numero_da_pagina_com_imagem: 
#         genai.configure(api_key = st.secrets['GEMINI_API_KEY'])
#         model = genai.GenerativeModel('gemini-2.5-flash')

#         for indice in numero_da_pagina_com_imagem:
#             pagina_fitz_imagem = doc_fitz.load_page(indice)
#             pix = pagina_fitz_imagem.get_pixmap(dpi=300)
#             img_bytes=pix.tobytes(output='jpeg')
#             buf = io.BytesIO(img_bytes)
#         #     prompt_para_pagina = f"""
#         # Você é um analista de layout de documentos e um especialista em OCR. Sua tarefa é interpretar a estrutura de uma página e, em seguida, transcrevê-la com precisão absoluta. O documento está em português do Brasil (pt-BR).

#         # Siga este processo de dois passos:

#         # **Passo 1: Análise Estrutural (Rascunho Mental)**
#         # Primeiro, identifique todos os blocos de conteúdo distintos na página e sua ordem de leitura lógica. Os blocos podem ser: Títulos, Parágrafos, Listas, Tabelas, Imagens com Legendas, Cabeçalhos, Rodapés, etc.

#         # **Passo 2: Transcrição Fiel**
#         # Segundo, transcreva cada bloco que você identificou, na ordem correta, aplicando as regras de formatação abaixo.

#         # **REGRAS DE TRANSCRIÇÃO:**

#         # 1.  **Fidelidade ao Original:** Não corrija erros, não complete frases e não adivinhe palavras. Se um trecho for ilegível, use o marcador `[ILEGÍVEL]`.
#         # 2.  **Texto Comum (Títulos, Parágrafos, Listas):** Transcreva como texto simples, usando quebras de linha para separar os parágrafos.
#         # 3.  **Tabelas:** Para blocos identificados como tabelas, use o formato **Markdown**:
#         #     a. Preserve rigorosamente a estrutura de linhas e colunas. Uma linha na imagem é uma linha no Markdown.
#         #     b. Mantenha as células vazias.
#         #     c. Mantenha a ordem exata das colunas.
#         # 4. Se identificar uma seção "referências", não transcreva essa seção.

#         # **FORMATO FINAL:**
#         # Sua saída final deve conter apenas a transcrição do Passo 2. Não inclua sua análise do Passo 1 nem qualquer outro comentário.
#         # """
#             prompt_para_pagina= f'''você é um analista de layout de documentos e especialista em ocr, o documento está em português do brasil (pt-br)
# Você não deve interpretar, resumir ou gerar conteúdo. Sua tarefa é transcrever o texto da imagem fornecida com precisão absoluta. Sua única função é agir como um serviço de OCR.
# objetivo
# - identificar os blocos de conteúdo da página e transcrever a página **em formato markdown**, fiel ao original, sem comentários extras

# regras gerais
# 1) responda **apenas** com a transcrição em markdown, não inclua a análise do passo 1 nem qualquer meta-comentário  
# 2) mantenha fidelidade total ao texto, não corrija nada, não complete frases, se um trecho estiver ilegível escreva exatamente: [ILEGÍVEL]  
# 3) preserve quebras de linha e ordem dos blocos tal qual a leitura da página  
# 4) não transcreva seções marcadas como "referências"  
# 5) para imagens insira um marcador no ponto correspondente: `![IMAGE]` opcionalmente com legenda entre parênteses, ex: `![IMAGE] (legenda da imagem)`  
# 6) tabelas devem ser convertidas para **markdown table** com pipes, preservando células vazias e a ordem de colunas  
# 7) listas devem usar `-` para itens não ordenados e `1.` `2.` para ordenadas, preservando a hierarquia  

# formato de saída (obrigatório)
# - use cabeçalhos `#`, `##` quando identificar títulos/subtítulos  
# - parágrafos como blocos de texto separados por linha em branco  
# - tabelas em markdown com linha de separador `| --- | --- |` mesmo que não haja cabeçalho claro, preserve células vazias  
# - imagens como `![IMAGE] (legenda opcional)` no local onde aparecem  
# - marque textos ilegíveis com `[ILEGÍVEL]` inline  

# exemplo mínimo de saída esperada
# # Título da Página
# Parágrafo inicial da página que pode ocupar mais de uma linha

# ## Subtítulo
# - item de lista 1
# - item de lista 2

# | coluna 1 | coluna 2 | coluna 3 |
# | --- | --- | --- |
# | valor A | valor B |  |
# |  | valor D | valor E |

# ![IMAGE] (Legenda, se houver)

# fim, responda somente com a transcrição em markdown, nada além'''
#             # cada página é uma lista de partes (imagem + instrução textual)
#             conteudo_api = [
#                     {
#                         "mime_type": "image/jpeg",
#                         "data": buf.getvalue()
#                     },
#                     {
#                         "text": prompt_para_pagina
#                     }
#                 ]
#             try:
#                 response = model.generate_content(contents=conteudo_api,
#                 safety_settings={
#                         'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
#                         'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
#                         'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
#                         'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
#                     }
#                 )
#                 if response.candidates:
#                     pagina_apenas_texto[indice] = f'Página {indice + 1}: {response.text}'
#                     print(f'Texto da Página com imagem (n°{indice + 1}) extraído com sucesso.')
#                 print('Aguardando 13 segundos para próxima chamada...')
#                 time.sleep(13)
#             except Exception as e:
#                 print(f'Erro na chamada do modelo para extrair texto da página {indice + 1}: {e}')
#                 continue

#         doc_fitz.close()
#     resultado_final = '\n\n'.join(pagina_apenas_texto)
#     return resultado_final


#   else:
#     # caso 2: tratar cada página como imagem e enviar para a Gemini (API genai)
#     # renderiza as paginas como imagens (necessita pdf2image/poppler)
#     file_bytes = caminho_arquivo.getvalue()
#     images = convert_from_bytes(file_bytes, dpi=300)


#     # inicializa o cliente
#     genai.configure(api_key=st.secrets['GEMINI_API_KEY'])
#     model = genai.GenerativeModel('gemini-2.5-flash')

#     # string final
#     resultado = ''

#     for idx, img in enumerate(images):
#         # converte PIL image para bytes jpeg
#         buf = io.BytesIO()
#         img.save(buf, format='JPEG', quality=95)
#         img_bytes = buf.getvalue()
#         prompt_para_pagina = f"""
#     Você é um analista de layout de documentos e um especialista em OCR. Sua tarefa é interpretar a estrutura de uma página e, em seguida, transcrevê-la com precisão absoluta. O documento está em português do Brasil (pt-BR).

#     Siga este processo de dois passos:

#     **Passo 1: Análise Estrutural (Rascunho Mental)**
#     Primeiro, identifique todos os blocos de conteúdo distintos na página e sua ordem de leitura lógica. Os blocos podem ser: Títulos, Parágrafos, Listas, Tabelas, Imagens com Legendas, Cabeçalhos, Rodapés, etc.

#     **Passo 2: Transcrição Fiel**
#     Segundo, transcreva cada bloco que você identificou, na ordem correta, aplicando as regras de formatação abaixo.

#     **REGRAS DE TRANSCRIÇÃO:**

#     1.  **Fidelidade ao Original:** Não corrija erros, não complete frases e não adivinhe palavras. Se um trecho for ilegível, use o marcador `[ILEGÍVEL]`.
#     2.  **Texto Comum (Títulos, Parágrafos, Listas):** Transcreva como texto simples, usando quebras de linha para separar os parágrafos.
#     3.  **Tabelas:** Para blocos identificados como tabelas, use o formato **Markdown**:
#         a. Preserve rigorosamente a estrutura de linhas e colunas. Uma linha na imagem é uma linha no Markdown.
#         b. Mantenha as células vazias.
#         c. Mantenha a ordem exata das colunas.
#     4. Se identificar uma seção "referências", não transcreva essa seção.

#     **FORMATO FINAL:**
#     Sua saída final deve conter apenas a transcrição do Passo 2. Não inclua sua análise do Passo 1 nem qualquer outro comentário.
#     """

#         # cada página é uma lista de partes (imagem + instrução textual)
#         conteudo_api = [
#                   {
#                       "mime_type": "image/jpeg",
#                       "data": buf.getvalue()
#                   },
#                   {
#                       "text": prompt_para_pagina
#                   }
#               ]

#         response = model.generate_content(conteudo_api)
#         if response.candidates:
#           resultado += response.candidates[0].content.parts[0].text


#     # retornamos o objeto response bruto para que o chamador processe conforme preferir
#     return resultado

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

    client = genai.Client(api_key = 'AIzaSyDon5TniEuUX-rYbjZncnhg2mQMfj1k_TQ')

    prompt = """Você é um assistente de IA especialista em extração de dados de documentos. Sua tarefa é analisar o documento fornecido para extrair informações sobre um único indivíduíduo, formatando a saída como um único objeto JSON que segue estritamente o schema fornecido.
    REGRAS DE INTERPRETAÇÃO DO DOCUMENTO:
    -Foco Principal: O objetivo é encontrar todas as informações sobre o indivíduo principal do documento. Reúna dados de todas as partes relevantes para construir um perfil completo.
    -Fontes de Dados: Analise tanto as tabelas quanto os parágrafos para coletar os dados. As informações podem estar espalhadas por todo o documento.
    -Associação de Dados: Utilize os cabeçalhos das tabelas e o contexto do texto para associar corretamente as informações aos campos do schema.
    -Exclusão: Ignore informações genéricas de cabeçalhos, rodapés e seções de referências bibliográficas do documento.

    REGRAS DE GERAÇÃO DO OBJETO JSON:
    -Estrutura da Saída: A saída deve ser um único objeto JSON, não um array.
    -Valores Ausentes: Se uma informação para um campo do schema não for encontrada no documento, o valor para esse campo deve ser a string "Não encontrado".
    -Formatação de Strings: Todas as strings no JSON final devem iniciar com letra maiúscula.
    -Limpeza do Conteúdo: O conteúdo extraído deve ser limpo, sem conter caracteres de formatação (como Markdown |, ---, *, etc.).
        """

    response = client.models.generate_content(
        model = 'gemini-2.5-flash',
        contents = [
            types.Part.from_bytes(
                data = pdf,
                mime_type = 'application/pdf'
            ),
            prompt
        ],
        config = {
            'response_mime_type': 'application/json',
            'response_schema': esquema
        }
    )


    return json.loads(response.text) 