import streamlit as st

st.set_page_config(
    page_title='ExtractIA',
    initial_sidebar_state='collapsed',
    layout='wide'
)

if not st.user.is_logged_in:
    _, col, _ = st.columns([1,2,1])
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
        max-width: 400px; /* Limita a largura para melhor visualização */
        margin: 50px auto; /* Centraliza o card na página */
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
    <div class="login-icon"><i class="fa-solid fa-solid fa-file-magnifying-glass"></i></div> 
    <h2>ExtractIA</h2>
    <p>Extraia dados de PDFs com inteligência artificial e receba bases de dados prontas para análises.</p>
</div>
        """
        st.markdown(login_card_html, unsafe_allow_html = True)
        if st.button('Log in com o Google', use_container_width=True):
            st.login()


else:
    paginas = {
        'Menu' : [st.Page('paginas/principal.py', title = 'Extração dinâmica de dados', default = True),
        st.Page('paginas/historico.py', title = 'Visualização de extrações anteriores')]
    }


    pg = st.navigation(paginas)
    pg.run()
    if st.sidebar.button('Log out', use_container_width = True):
        st.logout()