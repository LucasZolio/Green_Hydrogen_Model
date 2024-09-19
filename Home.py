import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Home",
    page_icon=":earth_americas:",
    layout="wide"
)

# Dicionário com as traduções em inglês e português
texts = {
    "en": {
        "title": "Predictive Mathematical Model for Green Hydrogen",
        "description": "This model will predict the amount of hydrogen by inputting data from the photovoltaic module datasheet!",
        "separator": "---"
    },
    "pt": {
        "title": "Modelo Matemático Preditivo para Hidrogênio Verde",
        "description": "Este modelo preverá a quantidade de hidrogênio inserindo dados da folha de dados do módulo fotovoltaico!",
        "separator": "---"
    }
}

# Define o idioma padrão como inglês
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Começa com inglês

# Simulação de toggle para alternar entre inglês e português
on_off = st.toggle('Exibir em português', value=True if st.session_state.language == 'pt' else False)

# Atualiza o idioma com base no toggle
if on_off:
    st.session_state.language = 'pt'  # Se marcado, exibe português
else:
    st.session_state.language = 'en'  # Se desmarcado, exibe inglês

# Exibir o conteúdo da página com base no idioma selecionado
with st.container():
    st.title(texts[st.session_state.language]["title"])
    st.write(texts[st.session_state.language]["description"])

with st.container():
    st.write(texts[st.session_state.language]["separator"])
