# Importa as Bibliotecas
import streamlit as st
import base64
import requests
from io import BytesIO
from googletrans import Translator
import sys
import os

# Adiciona o diretório 'page' ao caminho de pesquisa do Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'page'))

# Importa as páginas
from data import data
from graphs import graphs
from green_hydrogen_predict import green_hydrogen_predict
from result_table import results

# Configuração da página
st.set_page_config(
    page_title="Home",
    page_icon=":earth_americas:",
    layout="wide"
)

# Função para carregar a imagem de uma URL e convertê-la em base64
def load_flag_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        img = BytesIO(response.content)
        return base64.b64encode(img.read()).decode()
    else:
        st.error("Erro ao carregar a imagem.")
        return None

# URLs das imagens das bandeiras
us_flag_url = "https://cdn-icons-png.flaticon.com/256/940/940207.png"  # URL da bandeira dos EUA
br_flag_url = "https://cdn-icons-png.flaticon.com/512/206/206597.png"  # URL da bandeira do Brasil

# Carregar as bandeiras das URLs
us_flag_base64 = load_flag_image_from_url(us_flag_url)
br_flag_base64 = load_flag_image_from_url(br_flag_url)

# Função para definir o idioma
def set_language(language):
    st.session_state.language = language

# Inicializar o estado do idioma, se não estiver configurado
if 'language' not in st.session_state:
    st.session_state.language = 'pt'  # Padrão é português

# Layout para as bandeiras e troca de idioma no canto superior direito
col1, col2, col3 = st.columns([8, 0.4, 1])  # Diminuindo o espaço entre as colunas

with col2:  # Alterando ordem para exibir US primeiro
    if st.button("🇺🇸"):  # Botão da bandeira dos EUA
        set_language('en')
    
with col3:
    if st.button("🇧🇷"):  # Botão da bandeira brasileira
        set_language('pt')

# Inicializar o estado da página, se não estiver configurado
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'  # Padrão é a página inicial

# Função para definir a página atual
def set_page(page_name):
    st.session_state.current_page = page_name

# Função principal que contém o restante do código
def home():
    # Texto em português (original)
    titulo_pt = "Modelo Matemático Preditivo para Hidrogênio Verde"
    descricao_pt = "Site interativo onde os usuários inserem dados como irradiância solar, temperatura ambiente, eficiência do módulo fotovoltaico, e a quantidade de energia que desejam converter em hidrogênio."

    # Texto em inglês (traduzido)
    titulo_en = "Predictive Mathematical Model for Green Hydrogen"
    descricao_en = "Interactive site where users enter data such as solar irradiance, ambient temperature, photovoltaic module efficiency, and the amount of energy they want to convert into hydrogen."

    # Verificar o idioma atual e definir o conteúdo corretamente
    if st.session_state.language == 'en':
        titulo = titulo_en
        descricao = descricao_en
    else:
        titulo = titulo_pt
        descricao = descricao_pt

    # Exibir o título e descrição
    st.title(titulo)
    st.write(descricao)

# Sidebar com botões para navegação
st.sidebar.header("Menu" if st.session_state.language == 'pt' else "Menu")

# Verificar o idioma e redirecionar para a função correta da página
if st.sidebar.button("Início" if st.session_state.language == 'pt' else "Home"):
    if st.session_state.current_page != 'home':
        set_page('home')

if st.sidebar.button("Dados" if st.session_state.language == 'pt' else "Data"):
    set_page('data')

if st.sidebar.button("Predição de Hidrogênio Verde" if st.session_state.language == 'pt' else "Green Hydrogen Prediction"):
    set_page('green_hydrogen')

if st.sidebar.button("Gráficos" if st.session_state.language == 'pt' else "Graphs"):
    set_page('graphs')

if st.sidebar.button("Resultados" if st.session_state.language == 'pt' else "Results"):
    set_page('results')

# Verificar qual página deve ser exibida
if st.session_state.current_page == 'home':
    home()
elif st.session_state.current_page == 'data':
    data()
elif st.session_state.current_page == 'green_hydrogen':
    green_hydrogen_predict()
elif st.session_state.current_page == 'graphs':
    graphs()
elif st.session_state.current_page == 'results':
    results()
