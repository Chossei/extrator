import firebase_admin
import streamlit as st
import pandas as pd
from firebase_admin import firestore
from firebase_admin import credentials

@st.cache_resource
def inicializar_firebase():
    """
    Inicializa o Firebase Admin SDK se ainda não tiver sido inicializado
    e retorna uma instância do cliente do Firestore.
    """
    if not firebase_admin._apps:
        credenciais = credentials.Certificate(dict(st.secrets['firebase_credentials']))
        app = firebase_admin.initialize_app(credenciais)
    
    db = firestore.client()
    return db

def usuario_login():
    """
    Inicializa o Firebase Admin SDK se ainda não tiver sido inicializado
    e retorna uma instância do cliente do Firestore.
    """

    try:
        db = inicializar_firebase()
        email_usuario = st.user.email
        doc_ref = db.collection("usuarios").document(email_usuario)
        doc = doc_ref.get()

        if not doc.exists:
            doc_ref.set({
                'email': email_usuario,
                'cadastro em': firestore.SERVER_TIMESTAMP 
            })
        return doc_ref
    except Exception as e:
        print(f'Erro ao verificar/criar o perfil de usuário:{e}')
        return None

def verificar_existencia_modelos() -> bool:
    """
    Verifica se uma subcoleção específica existe para um usuário.

    A verificação é feita de forma eficiente, tentando buscar apenas um
    documento dentro da subcoleção.

    Returns:
        bool: True se a subcoleção contiver pelo menos um documento,
              False caso contrário.
    """
    try:
        db = inicializar_firebase()
        email_usuario = st.user.email
        subcolecao_ref = db.collection("usuarios").document(email_usuario).collection("modelos")
        documentos = subcolecao_ref.limit(1).stream()
        
        # Se list(documentos) não for vazio, o resultado é True. Se for vazio, é False.
        return bool(list(documentos))

    except Exception as e:
        print(f"Erro ao verificar a subcoleção '{nome_subcolecao}': {e}")
        return False

def buscar_nomes_dos_modelos() -> list[str]:
    """
    Busca e retorna uma lista com os nomes de todos os modelos de um usuário.

    A função consulta a subcoleção 'modelos' do usuário e extrai o ID
    de cada documento encontrado, que corresponde ao título do modelo.

    Args:
        email_usuario (str): O e-mail do usuário logado.

    Returns:
        list[str]: Uma lista contendo os nomes (títulos) de todos os
                   modelos salvos pelo usuário. Retorna uma lista vazia
                   se nenhum modelo for encontrado ou em caso de erro.
    """
    try:
        db = inicializar_firebase()
        # Aponta para a subcoleção 'modelos' do usuário.
        modelos_ref = db.collection("usuarios").document(st.user.email).collection("modelos")
        
        # .stream() busca todos os documentos na referência.
        docs = modelos_ref.stream()
        
        # Cria uma lista extraindo o .id de cada documento encontrado.
        # Esta é a forma mais rápida e "Pythonica" de fazer isso.
        lista_de_nomes = [doc.id for doc in docs]
        
        return lista_de_nomes

    except Exception as e:
        st.error(f"Erro ao buscar a lista de modelos: {e}")
        # Retorna uma lista vazia como um valor seguro em caso de falha.
        return []

def buscar_variaveis_de_modelo( nome_do_modelo: str) -> list | None:
    """
    Busca e retorna a lista de variáveis de um modelo específico de um usuário.

    A função acessa diretamente o documento do modelo na subcoleção 'modelos'
    e extrai o campo 'variaveis', que contém a lista de dicionários
    definida pelo usuário.

    Args:
        nome_do_modelo (str): O nome do modelo cujas variáveis serão buscadas.

    Returns:
        list | None: Uma lista de dicionários, onde cada dicionário representa
                    uma variável. Retorna None se o modelo não for encontrado
                    ou se ocorrer um erro.
    """
    try:
        db = inicializar_firebase()
        # Aponta diretamente para o documento do modelo específico.
        doc_ref = db.collection("usuarios").document(st.user.email).collection("modelos").document(nome_do_modelo)
        
        # .get() busca os dados de um único documento.
        doc = doc_ref.get()
        
        # Verifica se o documento realmente existe.
        if doc.exists:
            # Converte o documento para um dicionário Python.
            dados_do_modelo = doc.to_dict()
            # Retorna o valor da chave 'variaveis'. Usar .get() é uma
            # prática segura que retorna None se a chave não existir.
            return dados_do_modelo.get("variaveis")
        else:
            # Se o documento não for encontrado, informa o usuário.
            st.warning(f"O modelo '{nome_do_modelo}' não foi encontrado.")
            return None

    except Exception as e:
        st.error(f"Erro ao buscar as variáveis do modelo: {e}")
        return None

def atualizar_variaveis_do_modelo(nome_do_modelo: str, novas_variaveis: list) -> bool:
    """
    Atualiza a lista de variáveis de um modelo de extração existente.

    Esta função modifica apenas o campo 'variaveis' do documento do modelo
    especificado, substituindo a lista antiga pela nova. Outros campos,
    como 'criado_em', permanecem inalterados.

    Args:
        nome_do_modelo (str): O nome do modelo que será atualizado.
        novas_variaveis (list): A nova lista de dicionários de variáveis que
                                substituirá a lista existente.

    Returns:
        bool: True se a atualização for bem-sucedida, False caso contrário.
    """
    try:
        db = inicializar_firebase()
        # Aponta diretamente para o documento do modelo que queremos alterar.
        doc_ref = db.collection("usuarios").document(st.user.email).collection("modelos").document(nome_do_modelo)
        
        # Prepara um dicionário contendo APENAS os campos a serem atualizados.
        # A chave é o nome do campo no Firestore, e o valor é o novo conteúdo.
        dados_para_atualizar = {
            "variaveis": novas_variaveis
        }
        
        # Usa o método .update() para aplicar as alterações.
        # Se o documento não existir, .update() gerará um erro.
        doc_ref.update(dados_para_atualizar)
        
        print(f"Modelo '{nome_do_modelo}' atualizado com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao atualizar o modelo: {e}")
        return False

def salvar_variaveis(variaveis: list, titulo: str) -> str | None:
    """
    Salva um novo modelo de extração para o usuário no Firestore.

    Esta função cria ou sobrescreve um documento na subcoleção 'modelos' do
    usuário logado. O nome do documento é o próprio 'titulo' fornecido,
    garantindo que cada modelo tenha um identificador único e legível.

    Args:
        variaveis (list): A lista de dicionários contendo as variáveis
                          (nome, tipo, descrição) definidas pelo usuário.
        titulo (str): O nome que o usuário deu ao modelo, que será usado
                      como o ID do documento.

    Returns:
        str | None: O ID do documento criado (o próprio título) em caso de
                    sucesso. Retorna None se ocorrer qualquer erro durante
                    a operação.
    """
    try:
        # Inicializa a conexão com o banco de dados.
        db = inicializar_firebase()
        email_usuario = st.user.email

        # Aponta para o documento do modelo. O caminho é: usuarios/{email}/modelos/{titulo}.
        # Usar .document(titulo) nos permite definir um ID personalizado para o documento.
        doc_ref = db.collection("usuarios").document(email_usuario).collection("modelos").document(titulo)

        # Prepara um dicionário com todos os dados a serem salvos no documento do modelo.
        dados_para_salvar = {
            "titulo": titulo,  # Salvar o título dentro do doc é uma boa prática
            "variaveis": variaveis,
            "criado_em": firestore.SERVER_TIMESTAMP  # Adiciona a data de criação
        }

        # Usa o método .set() para criar o documento (ou sobrescrevê-lo se já existir).
        # Isso garante que o modelo esteja sempre atualizado com as últimas variáveis salvas.
        doc_ref.set(dados_para_salvar)
        
        print(f"Modelo '{titulo}' salvo com sucesso!")
        
        # Retorna o ID do documento, que é o próprio título.
        return doc_ref.id

    except Exception as e:
        # Em caso de qualquer falha, exibe um erro no terminal.
        print(f"Erro ao salvar o modelo de variáveis: {e}")
        # Retorna None para indicar que a operação falhou.
        return None

def salvar_extracao(nome_modelo_usado: str, nome_arquivo: str, dados_extraidos: list) -> str | None:
    """
    Salva o resultado de uma extração de PDF como um novo registro no histórico do usuário.

    Esta função cria um novo documento na subcoleção 'extracao' dentro do
    documento do usuário logado. Cada documento representa um único trabalho
    de extração, contendo o modelo utilizado, o nome do arquivo processado
    e os dados estruturados que foram extraídos.

    Args:
        nome_modelo_usado (str): O nome do modelo de variáveis que foi
                                 utilizado para esta extração.
        nome_arquivo (str): O nome do arquivo PDF que foi processado.
        dados_extraidos (list): Uma lista de dicionários contendo os dados
                                estruturados resultantes da extração.

    Returns:
        str | None: O ID único do novo documento de histórico criado no
                    Firestore em caso de sucesso. Retorna None se ocorrer
                    qualquer erro durante a operação.
    """
    try:
        # Inicializa a conexão com o banco de dados.
        db = inicializar_firebase()
        email_usuario = st.user.email

        # Prepara um dicionário com todos os dados a serem salvos no Firestore.
        # Organizar os dados assim torna o código mais legível e fácil de manter.
        dados_para_salvar = {
            "modelo_usado": nome_modelo_usado,
            "nome_arquivo": nome_arquivo,
            "dados_extraidos": dados_extraidos,
            "data_extracao": firestore.SERVER_TIMESTAMP  # Usa o timestamp do servidor para consistência
        }

        # Aponta para a subcoleção 'extracao' e usa o método .add().
        # O .add() cria um novo documento com um ID único gerado automaticamente,
        # o que é ideal para registros de histórico onde a ordem de criação importa.
        # Ele retorna uma tupla: (timestamp, DocumentReference).
        timestamp, doc_ref = db.collection("usuarios").document(email_usuario).collection("extracao").add(dados_para_salvar)
        
        print(f"Extração do arquivo '{nome_arquivo}' salva no histórico!")
        
        # A referência ao documento que acabamos de criar está em 'doc_ref'.
        # Retornamos seu ID para que possa ser usado em outra parte do código, se necessário.
        return doc_ref.id

    except Exception as e:
        # Em caso de qualquer falha, exibe um erro no terminal.
        print(f"Erro ao salvar o histórico da extração: {e}")
        # Retorna None para indicar que a operação falhou.
        return None

def criar_base(nome_modelo_usado: str) -> pd.DataFrame | None:
    """
    Consulta o Firestore para encontrar todas as extrações de um usuário
    associadas a um modelo específico e as consolida em um único DataFrame.

    A função busca na subcoleção 'extracao' do usuário logado, filtra
    os documentos pelo nome do modelo fornecido, extrai os dados de cada
    documento e os une em uma tabela final.

    Args:
        nome_modelo_usado (str): O nome (ID) do modelo de variáveis que será
                                 usado como filtro para a consulta.

    Returns:
        pd.DataFrame | None: Um DataFrame do Pandas contendo a base de dados
                              consolidada em caso de sucesso. Se nenhuma extração
                              for encontrada, retorna um DataFrame vazio.
                              Retorna None se ocorrer qualquer erro durante a
                              conexão ou o processamento dos dados.
    """
    try:
        # Inicializa a conexão com o banco de dados.
        db = inicializar_firebase()
        email_usuario = st.user.email
        
        # --- Consulta ao Firebase ---
        # Aponta para a subcoleção 'extracao' do usuário.
        doc_ref = db.collection("usuarios").document(email_usuario).collection("extracao")
        
        # Cria a consulta, filtrando pelo campo 'modelo_usado'.
        consulta_base = doc_ref.where("modelo_usado", "==", nome_modelo_usado)
        
        # Executa a consulta para buscar os documentos.
        docs_encontrados = consulta_base.stream()
        
        # --- Processamento dos Dados ---
        # Prepara uma lista para receber os dados de todos os documentos.
        lista_dados = []
        for documento in docs_encontrados:
            dados = documento.to_dict()
            nome_do_pdf = dados.get('nome_arquivo', 'N/A')
            # Verifica se o documento possui a chave 'dados_extraidos' e se seu valor é uma lista.
            if "dados_extraidos" in dados and isinstance(dados['dados_extraidos'], list):
                for item_extraido in dados['dados_extraidos']:
                    lista_dados.append({'PDF' : nome_do_pdf, **item_extraido})
        
        # --- Criação do DataFrame ---
        # Converte a lista consolidada de dicionários em um DataFrame do Pandas.
        dataframe = pd.DataFrame(lista_dados)
        return dataframe

    except Exception as e:
        # Em caso de qualquer falha, exibe um erro no terminal.
        print(f"Ocorreu um erro ao gerar a base de dados: {e}")
        # Retorna None para indicar que a operação falhou.
        return None