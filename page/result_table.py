import streamlit as st
import pandas as pd
from googletrans import Translator

# Instancia o tradutor
translator = Translator()

def results():
    # Define o idioma com base no idioma do navegador/sistema
    user_lang = st.session_state.get('language', 'en')

    # Função para traduzir texto
    def translate_text(text, dest_lang='pt'):
        return translator.translate(text, dest=dest_lang).text

    # Verifica o idioma e define o destino da tradução
    dest_lang = 'pt' if user_lang.startswith('pt') else 'en'

    # Textos originais em inglês
    texts = {
        "title": "Calculated Data Results",
        "description": "Here you will find the calculated results, including hydrogen production forecasts based on the provided irradiance and temperature data, as well as the maximum values of current, voltage, and power for the photovoltaic module.",
        "separator": "---",
        "upload_label": "Upload the calculated results (CSV)",
        "results_table_title": "Results Table",
        "results_table_description": "Results Table with Datasheet data and Hydrogen Prediction based on the entered Irradiance and Temperature data!",
        "missing_column_error": "The column '{col}' is missing in the CSV file. Please check the file and try again.",
        "upload_prompt": "Please upload a CSV file to display the table."
    }

    # Traduz os textos conforme o idioma detectado
    translated_texts = {key: translate_text(texts[key], dest_lang) for key in texts}

    # Exibir o conteúdo da página com base no idioma selecionado
    with st.container():
        st.title(translated_texts["title"])
        st.write(translated_texts["description"])

    with st.container():
        st.write(translated_texts["separator"])

    # Upload do arquivo CSV
    uploaded_file = st.file_uploader(translated_texts["upload_label"], type="csv")

    # Verifica se o arquivo foi carregado
    if uploaded_file is not None:
        try:
            # Carregar os dados do arquivo CSV
            df = pd.read_csv(uploaded_file)

            # Verificar se as colunas necessárias estão presentes
            required_columns = ['Irradiance', 'Temperature', 'Pmax_calculated', 'Imax_calculated', 'Vmax_calculated']
            for col in required_columns:
                if col not in df.columns:
                    raise KeyError(translated_texts["missing_column_error"].format(col=col))

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
                st.write(f"### {translated_texts['results_table_title']}")
                st.write(translated_texts["results_table_description"])
                st.dataframe(df.style.hide(axis="index"))

        except KeyError as e:
            st.error(f"{e}")
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
    else:
        st.write(translated_texts["upload_prompt"])
