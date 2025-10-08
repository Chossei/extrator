import firebase_admin
import streamlit as st
from firebase_admin import firestore
from firebase_admin import credentials

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
                'email': email_usuario
            })
        return doc_ref
    except Exception as e:
        print(f'Erro ao verificar/criar o perfil de usuário:{e}')
        return None
