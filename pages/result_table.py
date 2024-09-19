import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Result Table",
    page_icon=":earth_americas:",
    layout="wide"
)

# Dicionário com as traduções em inglês e português
texts = {
    "en": {
        "title": "Datasheet Electrical Data",
        "description": "Enter the electrical data of the photovoltaic module!",
        "separator": "---",
        "upload_label": "Upload the calculated results (CSV)",
        "results_table_title": "Results Table",
        "results_table_description": "Results Table with Datasheet data and Hydrogen Prediction based on the entered Irradiance and Temperature data!",
        "missing_column_error": "The column '{col}' is missing in the CSV file. Please check the file and try again.",
        "upload_prompt": "Please upload a CSV file to display the table."
    },
    "pt": {
        "title": "Tabela de Resultados",
        "description": "Tabela de Resultados com os dados do Datasheet e a Previsão de Hidrogênio baseada nos dados inseridos de Irradiância e Temperatura!",
        "separator": "---",
        "upload_label": "Faça o upload dos resultados calculados (CSV)",
        "results_table_title": "Tabela de Resultados",
        "results_table_description": "Tabela de Resultados com os dados do Datasheet e a Previsão de Hidrogênio baseada nos dados inseridos de Irradiância e Temperatura!",
        "missing_column_error": "A coluna '{col}' está faltando no arquivo CSV. Verifique o arquivo e tente novamente.",
        "upload_prompt": "Por favor, faça o upload de um arquivo CSV para exibir a tabela."
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

# Upload do arquivo CSV
uploaded_file = st.file_uploader(texts[st.session_state.language]["upload_label"], type="csv")

# Verifica se o arquivo foi carregado
if uploaded_file is not None:
    try:
        # Carregar os dados do arquivo CSV
        df = pd.read_csv(uploaded_file)

        # Verificar se as colunas necessárias estão presentes
        required_columns = ['Irradiance', 'Temperature', 'Pmax_calculated', 'Imax_calculated', 'Vmax_calculated']
        for col in required_columns:
            if col not in df.columns:
                raise KeyError(texts[st.session_state.language]["missing_column_error"].format(col=col))

        # Formatar as colunas com 0 casas decimais
        df['Irradiance'] = df['Irradiance'].map('{:.0f}'.format)
        df['Temperature'] = df['Temperature'].map('{:.0f}'.format)
        df['Pmax_calculated'] = df['Pmax_calculated'].map('{:.0f}'.format)

        # Formatar as colunas com 2 casas decimais
        df['Imax_calculated'] = df['Imax_calculated'].map('{:.2f}'.format)
        df['Vmax_calculated'] = df['Vmax_calculated'].map('{:.2f}'.format)

        # Mostrar a tabela sem o índice
        with st.container():
            st.write("---")
            st.write(f"### {texts[st.session_state.language]['results_table_title']}")
            st.write(texts[st.session_state.language]["results_table_description"])
            st.dataframe(df.style.hide(axis="index"))

    except KeyError as e:
        st.error(f"{e}")
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
else:
    st.write(texts[st.session_state.language]["upload_prompt"])
