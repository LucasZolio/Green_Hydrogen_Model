import os
import pandas as pd
import streamlit as st
from googletrans import Translator

# Disable file watching to prevent inotify watch limit error
st.set_option('server.fileWatcherType', 'none')

# Instantiate the translator
translator = Translator()

def green_hydrogen_predict():
    # Set default language to English
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  # Starts with English

    # Initialize history in session_state if it doesn't exist
    if 'inputs_history' not in st.session_state:
        try:
            st.session_state['inputs_history'] = pd.read_csv('data/calculated_results.csv')
        except FileNotFoundError:
            st.session_state['inputs_history'] = pd.DataFrame(columns=['Module Type', 'Irradiance', 'Temperature', 'Imax_calculated', 'Vmax_calculated', 'Pmax_calculated'])

    # Function to save updated data in cache and CSV
    def save_to_cache():
        # Use a local directory within the app's environment
        directory = 'data'

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the CSV file in the local directory
        st.session_state['inputs_history'].to_csv(os.path.join(directory, 'calculated_results.csv'), index=False)

    # Title and description with translation
    st.title(translator.translate("Green Hydrogen Performance Predictor", dest=st.session_state.language).text)
    st.write(translator.translate(
        "Input photovoltaic module data and predict the performance of green hydrogen generation under varying solar conditions. This tool provides theoretical calculations based on irradiance and temperature inputs, helping to estimate key parameters like Imax, Vmax, and Pmax.",
        dest=st.session_state.language).text)

    # Separator
    st.write(translator.translate("---", dest=st.session_state.language).text)

    def carregar_dados_cache():
        """Function to load data from cache if available."""
        if 'store_data' in st.session_state:
            return st.session_state['store_data']
        return None

    def carregar_dados_datasheet(arquivo_csv):
        """Function to load data from the CSV provided by the user."""
        try:
            dados = pd.read_csv(arquivo_csv)
            st.session_state['store_data'] = dados
            return dados
        except Exception as e:
            st.error(f"Error loading the CSV file: {e}")
            return None

    # Load data from cache
    dados_eletricos = carregar_dados_cache()

    # Split the screen into two columns
    col1, col2 = st.columns(2)

    # Column 1: File upload
    with col1:
        if dados_eletricos is None:
            st.warning(translator.translate("Module data not found in cache. Please upload the CSV file.", dest=st.session_state.language).text)
            upload_file = st.file_uploader(translator.translate("Upload the photovoltaic module datasheet (CSV)", dest=st.session_state.language).text, type="csv")

            if upload_file is not None:
                dados_eletricos = carregar_dados_datasheet(upload_file)
                if dados_eletricos is not None:
                    st.success(translator.translate("Photovoltaic module electrical data successfully loaded and stored in cache!", dest=st.session_state.language).text)
            else:
                st.stop()

    # Column 2: Calculation type selection
    with col2:
        if dados_eletricos is not None:
            try:
                module_type = dados_eletricos['module_type'].values[0]
                st.write(translator.translate(f"Module Type: {module_type}", dest=st.session_state.language).text)
            except KeyError:
                st.error(translator.translate("The CSV file does not contain all the required columns. Please check the file format.", dest=st.session_state.language).text)
                st.stop()

            tipo_calculo = st.radio(translator.translate("Select the calculation type", dest=st.session_state.language).text, ("Real", "Theoretical"))

    # Continue with calculations as before
    if dados_eletricos is not None and tipo_calculo == "Theoretical":
        with st.container():
            irradiance = st.number_input(translator.translate("Enter the Irradiance (W·m⁻²)", dest=st.session_state.language).text, min_value=0.0, step=0.1)
            temperature = st.number_input(translator.translate("Enter the Temperature (°C)", dest=st.session_state.language).text, min_value=-5.0, step=0.1)

            # Reference values
            Tref = 25  # Reference temperature (°C)
            Gref = 1000  # Reference irradiance (W/m²)

            def calcular_parametros(T, G):
                """Function to calculate theoretical parameters based on irradiance and temperature data."""
                if all(col in dados_eletricos.columns for col in ['isc_datasheet', 'voc_datasheet', 'Imax_datasheet', 'Vmax_datasheet', 'alpha', 'beta']):
                    isc = float(dados_eletricos['isc_datasheet'].values[0])
                    voc = float(dados_eletricos['voc_datasheet'].values[0])
                    imax = float(dados_eletricos['Imax_datasheet'].values[0])
                    vmax = float(dados_eletricos['Vmax_datasheet'].values[0])
                    alpha = float(dados_eletricos['alpha'].values[0])
                    beta = float(dados_eletricos['beta'].values[0])

                    # Calculations based on provided irradiance and temperature
                    Imax_calculado = imax * (G / Gref) * (1 + alpha * (T - Tref))
                    Vmax_calculado = vmax * (1 + beta * (T - Tref))
                    Pmax_calculado = round(Imax_calculado * Vmax_calculado, 2)

                    return Imax_calculado, Vmax_calculado, Pmax_calculado
                else:
                    st.error(translator.translate("The CSV file does not contain all the required columns. Please check the file format.", dest=st.session_state.language).text)
                    return None, None, None

            # Button to calculate parameters
            if st.button(translator.translate("Calculate", dest=st.session_state.language).text):
                if irradiance and temperature:
                    st.success(translator.translate(f"Irradiance: {irradiance} W·m⁻²", dest=st.session_state.language).text)
                    st.success(translator.translate(f"Temperature: {temperature} °C", dest=st.session_state.language).text)

                    # Calculate parameters
                    Imax_calculado, Vmax_calculado, Pmax_calculado = calcular_parametros(temperature, irradiance)

                    if Imax_calculado is not None:
                        st.write(translator.translate(f"Imax calculated: {round(Imax_calculado, 2)} A", dest=st.session_state.language).text)
                        st.write(translator.translate(f"Vmax calculated: {round(Vmax_calculado, 2)} V", dest=st.session_state.language).text)
                        st.write(translator.translate(f"Pmax calculated: {round(Pmax_calculado, 0)} W", dest=st.session_state.language).text)

                        # Save new input to history data
                        novo_input = pd.DataFrame({
                            'Module Type': [module_type],
                            'Irradiance': [irradiance],
                            'Temperature': [temperature],
                            'Imax_calculated': [round(Imax_calculado, 2)],
                            'Vmax_calculated': [round(Vmax_calculado, 2)],
                            'Pmax_calculated': [round(Pmax_calculado, 0)]
                        })

                        st.session_state['inputs_history'] = pd.concat([st.session_state['inputs_history'], novo_input], ignore_index=True)

                        # Save data to a CSV file and cache
                        save_to_cache()

                        csv_historico = st.session_state['inputs_history'].to_csv(index=False)
                        st.download_button(
                            label=translator.translate("Download Updated CSV", dest=st.session_state.language).text,
                            data=csv_historico,
                            file_name="calculated_theoretical_results.csv",
                            mime="text/csv"
                        )
                else:
                    st.error(translator.translate("Please enter the values correctly.", dest=st.session_state.language).text)
    else:
        st.write(translator.translate("Work in Process (W.I.P)", dest=st.session_state.language).text)
