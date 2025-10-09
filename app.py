import streamlit as st
from paginas.funcoes_firebase import (
    inicializar_firebase,
    usuario_login
)

st.set_page_config(
    page_title='ExtractIA',
    initial_sidebar_state='collapsed',
    layout='wide'
)

if not st.user.is_logged_in:
    _, col, _ = st.columns([2,2,2]) # Esta coluna tem uma largura específica
    with col:
        login_card_html = """
        <style>
            /* Importa uma fonte e ícones para um visual mais refinado */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');

            /* Variáveis de cores para facilitar a manutenção */
            :root {
                --primary-color: #007bff; /* Azul vibrante */
                --secondary-color: #6c757d; /* Cinza para detalhes */
                --background-light: #f8f9fa; /* Fundo bem claro */
                --text-dark: #343a40; /* Texto escuro */
                --border-light: #e9ecef; /* Borda suave */
            }

            /* Estilo do nosso card de login */
            .login-card {
                font-family: 'Montserrat', sans-serif;
                background-color: var(--background-light);
                padding: 40px;
                border-radius: 15px;
                text-align: center;
                border: 1px solid var(--border-light);
                box-shadow: 0 10px 25px rgba(0,0,0,0.15); /* Sombra mais pronunciada e moderna */
                /* max-width: 400px; <--- REMOVIDO ou ALTERADO para 100% */
                width: 100%; /* Faz o card ocupar a largura total do contêiner */
                /* margin: 50px auto; <--- REMOVIDO para que a coluna centralize */
                margin-top: 50px; /* Mantém a margem superior se desejar */
                margin-bottom: 20px; /* Adiciona uma margem inferior para separar do botão */
            }

            .login-icon {
                font-size: 4.5rem; /* Tamanho do ícone um pouco maior */
                color: var(--primary-color);
                margin-bottom: 25px;
                /* Adicionando um pequeno gradiente ou efeito para o ícone */
                background: -webkit-linear-gradient(45deg, var(--primary-color), #0056b3);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .login-card h2 {
                color: var(--text-dark);
                font-weight: 700; /* Mais negrito para o título */
                font-size: 2.5rem; /* Título maior */
                margin-bottom: 15px;
                letter-spacing: -0.5px; /* Pequeno ajuste no espaçamento */
            }

            .login-card p {
                color: var(--secondary-color);
                font-size: 1.1rem; /* Descrição um pouco maior */
                line-height: 1.6; /* Espaçamento de linha para melhor leitura */
                margin-bottom: 35px;
            }
        </style>

        <div class="login-card">
            <div class="login-icon"><i class="fa-solid fa-file-import"></i></div> 
            <h2>ExtractIA</h2>
            <p>Extraia dados de PDFs com inteligência artificial e receba bases de dados prontas para análises.</p>
        </div>
        """
        st.markdown(login_card_html, unsafe_allow_html = True)
        if st.button('Log in com o Google', use_container_width=True):
            st.login()
else:
    
    referencia_id = usuario_login()
    with st.sidebar:
        with st.container():
            st.divider() # Uma linha para separar visualmente
            
            # O HTML para a imagem e o nome
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <img src="{st.user.picture}" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;">
                    <div>Olá, <strong>{st.user.name}</strong></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # O botão de logout
            if st.button('Log out', use_container_width=True):
                st.logout()
    
    paginas = {
        'Menu' : [st.Page('paginas/principal.py', title = 'Início', default = True),
        st.Page('paginas/historico.py', title = 'Histórico')]
    }
    pg = st.navigation(paginas)
    pg.run()