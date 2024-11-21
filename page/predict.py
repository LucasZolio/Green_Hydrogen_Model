import pandas as pd
import streamlit as st
from googletrans import Translator
import os

# Instancia o tradutor
translator = Translator()

def predict_data():
    # Define o idioma padrão como inglês
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  # Começa com inglês

    # Inicializa o histórico no session_state, se ainda não existir
    if 'inputs_history' not in st.session_state:
        try:
            st.session_state['inputs_history'] = pd.read_csv('/mnt/data/calculated_results.csv')
        except FileNotFoundError:
            st.session_state['inputs_history'] = pd.DataFrame(
                columns=['Module Type', 'Irradiance', 'Temperature', 'Imax_calculated', 'Vmax_calculated', 'Pmax_calculated']
            )

    # Função para salvar dados atualizados no cache e no CSV
    def save_to_cache():
        directory = '/mnt/data/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        st.session_state['inputs_history'].to_csv(os.path.join(directory, 'calculated_results.csv'), index=False)

    st.title(translator.translate("Performance Predict", dest=st.session_state.language).text)
    st.write(translator.translate(
        "Input data photovoltaic module or plant and predict the performance under varying solar conditions. This tool provides theoretical calculations based on irradiance and temperature inputs, helping to estimate key parameters like Imax, Vmax, and Pmax.",
        dest=st.session_state.language).text)

    @st.cache_data
    def carregar_dados_datasheet(arquivo_csv):
        try:
            dados = pd.read_csv(arquivo_csv)
            st.session_state['store_data'] = dados
            return dados
        except Exception as e:
            st.error(f"Error loading the CSV file: {e}")
            return None

    # Mantém o arquivo carregado, se existente
    arquivo_padrao = '/mnt/data/datasheet_data.csv'
    if 'store_data' not in st.session_state:
        if os.path.exists(arquivo_padrao):
            dados_eletricos = carregar_dados_datasheet(arquivo_padrao)
        else:
            dados_eletricos = None
    else:
        dados_eletricos = st.session_state['store_data']

    # Permite carregar um arquivo caso o padrão não exista
    if dados_eletricos is None:
        upload_file = st.file_uploader(
            translator.translate("Upload the photovoltaic module datasheet (CSV)", dest=st.session_state.language).text,
            type="csv"
        )
        if upload_file is not None:
            dados_eletricos = carregar_dados_datasheet(upload_file)
            if dados_eletricos is not None:
                st.success(translator.translate(
                    "Photovoltaic module electrical data successfully loaded and stored in cache!",
                    dest=st.session_state.language).text)
        else:
            st.stop()

    if dados_eletricos is not None:
        try:
            module_type = dados_eletricos['module_type'].values[0]
            st.write(translator.translate(f"Module Type: {module_type}", dest=st.session_state.language).text)
        except KeyError:
            st.error(translator.translate(
                "The CSV file does not contain all the required columns. Please check the file format.",
                dest=st.session_state.language).text)
            st.stop()

        tipo_calculo = st.radio(
            translator.translate("Select the calculation type", dest=st.session_state.language).text,
            ("Real", "Theoretical"), index=1
        )

        # Se dados teóricos forem selecionados
        if tipo_calculo == "Theoretical":
            irradiance = st.number_input(
                translator.translate("Enter the Irradiance (W·m⁻²)", dest=st.session_state.language).text,
                min_value=0.0, step=0.1
            )
            temperature = st.number_input(
                translator.translate("Enter the Temperature (°C)", dest=st.session_state.language).text,
                min_value=0.0, step=0.1
            )

            Tref = 25  # Temperatura de referência (°C)
            Gref = 1000  # Irradiância de referência (W·m⁻²)

            def calcular_parametros(T, G, row):
                try:
                    isc = float(row['isc_datasheet'])
                    voc = float(row['voc_datasheet'])
                    imax = float(row['Imax_datasheet'])
                    vmax = float(row['Vmax_datasheet'])
                    alpha = float(row['alpha'])
                    beta = float(row['beta'])

                    Imax_calculado = imax * (G / Gref)
                    Vmax_calculado = vmax * (1 + beta * (T - Tref))
                    Pmax_calculado = round(Imax_calculado * Vmax_calculado, 2)

                    return Imax_calculado, Vmax_calculado, Pmax_calculado
                except KeyError as e:
                    st.error(translator.translate(f"Missing required column in CSV: {str(e)}", dest=st.session_state.language).text)
                    return None, None, None

            if st.button(translator.translate("Calculate", dest=st.session_state.language).text):
                if irradiance > 0 and temperature:
                    row = dados_eletricos.iloc[0]
                    imax_calculated, vmax_calculated, pmax_calculated = calcular_parametros(temperature, irradiance, row)

                    if imax_calculated and vmax_calculated and pmax_calculated:
                        st.success(f"Irradiance: {irradiance} W·m⁻²")
                        st.success(f"Temperature: {temperature} °C")
                        st.info(f"Imax (Calculated): {imax_calculated:.2f} A")
                        st.info(f"Vmax (Calculated): {vmax_calculated:.2f} V")
                        st.info(f"Pmax (Calculated): {pmax_calculated:.2f} W")
                else:
                    st.error(translator.translate("Please enter valid values.", dest=st.session_state.language).text)

        if tipo_calculo == "Real":
            st.warning("Working in Process (W.I.P)")
