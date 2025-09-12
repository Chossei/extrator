import streamlit as st
import time
import pandas as pd
import numpy as np
import PyPDF2
import google.generativeai as genai
import io
import json
from pydantic import create_model
from pdf2image import convert_from_bytes

@st.dialog('📝 Adicionar Novas Variáveis', width='large')
def adicionar_variavel():
    """
    Formulário dentro de um diálogo para o usuário adicionar até 5 variáveis,
    especificando nome, descrição e tipo para cada uma.
    A submissão só é permitida se pelo menos uma variável for nomeada.
    """
        # --- O Formulário ---
    with st.form(key="variaveis_form"):
        st.write("Preencha os campos para as variáveis que deseja extrair. Deixe o nome em branco para ignorar a linha.")
        st.divider()

        OPCOES_TIPO = ["Texto", "Número sem casas decimais", "Número com casas decimais"]

        # Loop para criar 5 linhas de inputs para as variáveis
        for i in range(5):
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
        for i in range(5):
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
                st.success(f"{len(variaveis_coletadas)} variável(is) adicionada(s)! Os campos foram mantidos caso queira editá-los ou pode preencher os campos vazios para adicionar mais.")
                # O script continua e o formulário permanece na tela

            elif acao_selecionada == "Concluir e voltar para a tela inicial":
                # Para fechar o "diálogo" e atualizar a tela principal, usamos o rerun
                # (Em um st.dialog(), isso fecharia o popup)
                st.success("Ação concluída!")
                with st.spinner("Voltando para a tela inicial..."):
                    time.sleep(1)
                st.rerun()

def estruturador(texto, variaveis):
  """
  Extrai informações estruturadas de um texto potencialmente contendo **múltiplos indivíduos**,
  pedindo ao modelo generativo que retorne um *array* JSON onde cada item representa um indivíduo
  com os campos definidos pelo schema dinâmico gerado via pydantic


  comportamento principal
  - monta dinamicamente um schema Pydantic (`DynamicSchema`) a partir de `variaveis`
  - constrói um prompt mínimo que instrui o modelo a retornar **uma lista** (array) de objetos
  obedecendo ao schema, cada objeto representando um indivíduo
  - configura o `generation_config` para esperar `application/json` e `response_schema=list[DynamicSchema]`
  - retorna `response.text` (string JSON) com o array de indivíduos, cabe ao chamador fazer o parse


  parâmetros
  - texto (str): texto bruto proveniente de documentos, pode conter zero, um ou vários indivíduos
  - variaveis (list[dict]): lista de dicionários com pelo menos as chaves:
  - 'nome' (str): nome do campo que aparecerá no schema e na saída JSON
  - 'descricao' (str): (opcional) descrição do campo — nesta versão ela não é enviada ao prompt
  - 'tipo' (str): tipo esperado: 'string', 'integer', 'float' ou 'boolean' (default 'string')


  requisitos/assunções
  - existe um cliente `genai` configurado globalmente e uma variável `api_key` disponível
  - `create_model` do pydantic está disponível (importado no topo deste arquivo)
  - o modelo generativo suporta `response_schema` e aceita `list[DynamicSchema]` como saída estruturada


  retorno
  - str: conteúdo bruto retornado pelo modelo (geralmente um JSON array). Ex.:
  '[{"nome": "João", "cpf": "..."}, {"nome": "Maria", "cpf": "..."}]'
  recomenda-se chamar `json.loads(response.text)` no chamador para obter a lista de objetos


  notas importantes / boas práticas
  - o prompt é propositalmente enxuto, não reenvie a descrição das variáveis no corpo do prompt,
  pois o schema já descreve os campos e descrições longas aumentam o custo de tokens
  - para permitir rastreabilidade, instruímos o modelo a incluir `nomes_alternativos` e `source_snippet`
  em cada objeto, caso queira trocar `source_snippet` por offsets (start/end) basta ajustar o texto do prompt
  - se o texto for muito grande, implemente pré-processamento local (chunking / seleção por parágrafos)
  para reduzir tokens antes da chamada, ou envie apenas blocos candidatos
  - depende da qualidade do modelo: para evitar duplicatas/erros peça no prompt que o modelo
  una menções repetidas num único objeto e liste variações em `nomes_alternativos`


  exemplo de uso (resumo, sem código de rede):
  1) defina `variaveis = [{'nome':'nome','tipo':'string'},{'nome':'cpf','tipo':'string'}]
  2) chame `resp = modelo_google(texto, variaveis)`
  3) em seguida: `data = json.loads(resp)` -> `data` será uma lista de dicionários


  limitações
  - o LLM pode alucinar valores ausentes, portanto sempre valide os campos críticos (ex.: cpf)
  comparando com o `source_snippet` retornado
  - se o texto contém muitos indivíduos, controle o tamanho da saída e o custo limitando
  o número máximo pedido ao modelo via instruções adicionais no prompt


  changelog / versão
  - v1.0: documentado, resposta em array de objetos (múltiplos indivíduos)


  """


  instrucoes_prompt = f"""
  Você é um especialista em extração de dados que recebe um texto e o converte em um array JSON de indivíduos.

  **REGRAS DE INTERPRETAÇÃO DO TEXTO DE ENTRADA:**
  O texto fornecido pode ser texto corrido, uma tabela em formato Markdown, ou uma combinação de ambos.
  1.  **Se o texto for uma tabela Markdown:** Considere que cada linha (após o cabeçalho) representa um indivíduo distinto. Os cabeçalhos da tabela podem ajudar a identificar os campos.
  2.  **Se o texto for corrido (parágrafos):** Procure por menções a indivíduos dentro da prosa.

  **REGRAS PARA A SAÍDA JSON:**
  Após interpretar o texto, gere um único array JSON seguindo estas regras estritas:
  - O array deve conter exatamente **um objeto por indivíduo distinto** identificado.
  - **Unicidade:** Não repita indivíduos. Se a mesma pessoa (identificada por CPF, número de processo ou nome normalizado) aparecer várias vezes, una todas as informações em um único objeto JSON.
  - **Campos:** Para cada objeto, inclua todos os campos solicitados pelo schema JSON.
  - **Valores Ausentes:** Para campos cujas informações não foram encontradas no texto, preencha o valor com a string "Não encontrado".
  - **Formato:** Strings devem sempre iniciar com letra maiúscula.
  - **Limite:** Retorne no máximo 200 objetos.
  - **Entidades:** Os indivíduos a serem extraídos são sempre seres humanos.
  - **Limpeza:** A saída final não deve incluir símbolos de formatação Markdown como `|` ou `---`.

  --- TEXTO PARA ANÁLISE ---
  {texto}
  """


  # 1. Mapeia os tipos de string para tipos reais do Python
  type_mapping = {
  'string': str,
  'integer': int,
  'float': float,
  'boolean': bool
  }


  # 2. Prepara as definições dos campos para o Pydantic
  field_definitions = {}
  for var in variaveis:
    nome = var['nome']
    tipo_py = type_mapping.get(var.get('tipo', 'string').lower(), str)
    # A tupla (tipo, ...) significa que o campo e obrigatorio.
    field_definitions[nome] = (tipo_py, ...)


  # 3. Usa create_model do Pydantic para criar a classe do schema
  DynamicSchema = create_model('DynamicSchema', **field_definitions)


  # configuracao e chamada ao modelo
  genai.configure(api_key=st.secrets['GEMINI_API_KEY'])
  model = genai.GenerativeModel('gemini-2.5-flash')


  generation_config = genai.GenerationConfig(
  response_mime_type='application/json',
  response_schema=list[DynamicSchema], # agora esperamos um array de objetos (varios individuos)
  temperature=0.0
  )


  response = model.generate_content(
  instrucoes_prompt,
  generation_config=generation_config
  )


  return pd.DataFrame(json.loads(response.text))          

def extrator_texto(caminho_arquivo, imagem : str):

  # caso 1: tentativa de extracao direta de texto
  if imagem == 'texto':
    pagina_texto = ''
    try:
        leitor = PyPDF2.PdfReader(pdf)
        for pagina in leitor.pages:
            texto = pagina.extract_text() or ''
            pagina_texto += texto
      # caso contrário, caimos para o fluxo de imagens (scanned)
        return pagina_texto
    except Exception as e:
    # se falhar qualquer coisa, prosseguimos para o fluxo de imagens
        print(f"Erro na extração via PyPDF2: {e}")


  else:
    # caso 2: tratar cada página como imagem e enviar para a Gemini (API genai)
    # renderiza as paginas como imagens (necessita pdf2image/poppler)
    file_bytes = caminho_arquivo.getvalue()
    images = convert_from_bytes(file_bytes, dpi=300)


    # inicializa o cliente
    genai.configure(api_key=st.secrets['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-2.5-flash')

    # string final
    resultado = ''

    for idx, img in enumerate(images):
        # converte PIL image para bytes jpeg
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=95)
        img_bytes = buf.getvalue()
        prompt_para_pagina = f"""
    Você é um analista de layout de documentos e um especialista em OCR. Sua tarefa é interpretar a estrutura de uma página e, em seguida, transcrevê-la com precisão absoluta. O documento está em português do Brasil (pt-BR).

    Siga este processo de dois passos:

    **Passo 1: Análise Estrutural (Rascunho Mental)**
    Primeiro, identifique todos os blocos de conteúdo distintos na página e sua ordem de leitura lógica. Os blocos podem ser: Títulos, Parágrafos, Listas, Tabelas, Imagens com Legendas, Cabeçalhos, Rodapés, etc.

    **Passo 2: Transcrição Fiel**
    Segundo, transcreva cada bloco que você identificou, na ordem correta, aplicando as regras de formatação abaixo.

    **REGRAS DE TRANSCRIÇÃO:**

    1.  **Fidelidade ao Original:** Não corrija erros, não complete frases e não adivinhe palavras. Se um trecho for ilegível, use o marcador `[ILEGÍVEL]`.
    2.  **Texto Comum (Títulos, Parágrafos, Listas):** Transcreva como texto simples, usando quebras de linha para separar os parágrafos.
    3.  **Tabelas:** Para blocos identificados como tabelas, use o formato **Markdown**:
        a. Preserve rigorosamente a estrutura de linhas e colunas. Uma linha na imagem é uma linha no Markdown.
        b. Mantenha as células vazias.
        c. Mantenha a ordem exata das colunas.

    **FORMATO FINAL:**
    Sua saída final deve conter apenas a transcrição do Passo 2. Não inclua sua análise do Passo 1 nem qualquer outro comentário.
    """

        # cada página é uma lista de partes (imagem + instrução textual)
        conteudo_api = [
                  {
                      "mime_type": "image/jpeg",
                      "data": buf.getvalue()
                  },
                  {
                      "text": prompt_para_pagina
                  }
              ]

        response = model.generate_content(conteudo_api)
        if response.candidates:
          resultado += response.candidates[0].content.parts[0].text


    # retornamos o objeto response bruto para que o chamador processe conforme preferir
    return resultado
