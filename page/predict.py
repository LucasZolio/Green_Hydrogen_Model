import pandas as pd
import streamlit as st
from googletrans import Translator
import os

# Instancia o tradutor
translator = Translator()

def green_hydrogen_predict():
    # Define o idioma padrão como inglês
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  # Começa com inglês

    # Inicializa o histórico no session_state, se ainda não existir
    if 'inputs_history' not in st.session_state:
        try:
            st.session_state['inputs_history'] = pd.read_csv('/mnt/data/calculated_results.csv')
        except FileNotFoundError:
            st.session_state['inputs_history'] = pd.DataFrame(columns=['Module Type', 'Irradiance', 'Temperature', 'Imax_calculated', 'Vmax_calculated', 'Pmax_calculated'])

    # Função para salvar dados atualizados no cache e no CSV
    def save_to_cache():
        directory = '/mnt/data/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        st.session_state['inputs_history'].to_csv(os.path.join(directory, 'calculated_results.csv'), index=False)

    st.title(translator.translate("Green Hydrogen Performance Predictor", dest=st.session_state.language).text)
    st.write(translator.translate(
        "Input data photovoltaic module or plant and predict the performance under varying solar conditions. This tool provides theoretical calculations based on irradiance and temperature inputs, helping to estimate key parameters like Imax, Vmax, and Pmax.",
        dest=st.session_state.language).text)

    st.write(translator.translate("---", dest=st.session_state.language).text)

    @st.cache_data
    def carregar_dados_cache():
        if 'store_data' in st.session_state:
            return st.session_state['store_data']
        return None

    @st.cache_data
    def carregar_dados_datasheet(arquivo_csv):
        try:
            dados = pd.read_csv(arquivo_csv)
            st.session_state['store_data'] = dados
            return dados
        except Exception as e:
            st.error(f"Error loading the CSV file: {e}")
            return None

    dados_eletricos = carregar_dados_cache()

    col1, col2 = st.columns(2)

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

    with col2:
        if dados_eletricos is not None:
            try:
                module_type = dados_eletricos['module_type'].values[0]
                st.write(translator.translate(f"Module Type: {module_type}", dest=st.session_state.language).text)
            except KeyError:
                st.error(translator.translate("The CSV file does not contain all the required columns. Please check the file format.", dest=st.session_state.language).text)
                st.stop()

            tipo_calculo = st.radio(translator.translate("Select the calculation type", dest=st.session_state.language).text, ("Real", "Theoretical"), index=1)

    if dados_eletricos is not None and tipo_calculo == "Theoretical":
        with st.container():
            irradiance = st.number_input(translator.translate("Enter the Irradiance (W·m⁻²)", dest=st.session_state.language).text, min_value=0.0, step=0.1)
            temperature = st.number_input(translator.translate("Enter the Temperature (°C)", dest=st.session_state.language).text, min_value=-5.0, step=0.1)

            Tref = 25  # Temperatura de referência (°C)
            Gref = 1000  # Irradiância de referência (W/m²)

            def calcular_parametros(T, G, row):
                try:
                    if all(col in row.index for col in ['isc_datasheet', 'voc_datasheet', 'Imax_datasheet', 'Vmax_datasheet', 'alpha', 'beta', 'Imax_sis', 'Vmax_sis', 'Pmax_sis']):
                        isc = float(row['isc_datasheet'])
                        voc = float(row['voc_datasheet'])
                        imax = float(row['Imax_datasheet'])
                        vmax = float(row['Vmax_datasheet'])
                        alpha = float(row['alpha'])
                        beta = float(row['beta'])
                        Imax_sis = float(row['Imax_sis'])
                        Vmax_sis = float(row['Vmax_sis'])
                        Pmax_sis = float(row['Pmax_sis'])

                        Imax_calculado = imax * (G / Gref)
                        Vmax_calculado = vmax * (1 + beta * (T - Tref))
                        Pmax_calculado = round(Imax_calculado * Vmax_calculado, 2)
                        Imax_sis_calculado = Imax_sis * (G / Gref)
                        Vmax_sis_calculado = Vmax_sis * (1 + beta * (T - Tref))
                        Pmax_sis_calculado = Imax_sis_calculado * Vmax_sis_calculado

                        return Imax_calculado, Vmax_calculado, Pmax_calculado, Imax_sis_calculado, Vmax_sis_calculado, Pmax_sis_calculado
                except KeyError as e:
                    st.error(translator.translate(f"Missing required column in CSV: {str(e)}", dest=st.session_state.language).text)
                return None, None, None, None, None, None

            if st.button(translator.translate("Calculate", dest=st.session_state.language).text):
                if irradiance and temperature:
                    st.success(translator.translate(f"Irradiance: {irradiance} W·m⁻²", dest=st.session_state.language).text)
                    st.success(translator.translate(f"Temperature: {temperature} °C", dest=st.session_state.language).text)

                    novos_dados = []
                     # Para cada linha de dados, realiza o cálculo
                    for idx, row in dados_eletricos.iterrows():
                        Imax_calculado, Vmax_calculado, Pmax_calculado, Imax_sis_calculado, Vmax_sis_calculado, Pmax_sis_calculado = calcular_parametros(temperature, irradiance, row)
                        
                        # Aplicar lógica de conversão de unidades
                        # Converter Pmax_sis
                        if Pmax_sis_calculado >= 1000000:
                            Pmax_sis_calculado = round(Pmax_sis_calculado / 1000000, 2)  # Converter para TW
                            unidade_potencia = "TW"
                        elif Pmax_sis_calculado >= 1000:
                            Pmax_sis_calculado = round(Pmax_sis_calculado / 1000, 2)  # Converter para MW
                            unidade_potencia = "MW"
                        else:
                            Pmax_sis_calculado = round(Pmax_sis_calculado, 2)  # Manter em W
                            unidade_potencia = "W"

                        # Converter Imax_sis
                        if Imax_sis_calculado >= 1000:
                            Imax_sis_calculado = round(Imax_sis_calculado / 1000, 2)  # Converter para kA
                            unidade_corrente = "kA"
                        else:
                            Imax_sis_calculado = round(Imax_sis_calculado, 2)  # Manter em A
                            unidade_corrente = "A"

                        # Converter Vmax_sis
                        if Vmax_sis_calculado >= 1000:
                            Vmax_sis_calculado = round(Vmax_sis_calculado / 1000, 2)  # Converter para kV
                            unidade_tensao = "kV"
                        else:
                            Vmax_sis_calculado = round(Vmax_sis_calculado, 2)  # Manter em V
                            unidade_tensao = "V"

                        if Imax_calculado is not None:
                            novos_dados.append({
                                'Module Type': row['module_type'],
                                'Irradiance': irradiance,
                                'Temperature': temperature,
                                'Imax': round(Imax_calculado, 2),
                                'Vmax': round(Vmax_calculado, 2),
                                'Pmax': round(Pmax_calculado, 0),
                                'Imax_sis': round(Imax_sis_calculado, 2),
                                'Vmax_sis': round(Vmax_sis_calculado, 2),
                                'Pmax_sis': round(Pmax_sis_calculado, 0)
                            })
                            
                            # Exibir os resultados para o módulo
                            #st.write(f"Imax Calculado (Módulo): {Imax_calculado} A")
                            #st.write(f"Vmax Calculado (Módulo): {Vmax_calculado} V")
                            #st.write(f"Pmax Calculado (Módulo): {Pmax_calculado} W")
                            
                            # Exibir os resultados com as unidades convertidas
                            st.write(f"Imax Calculado (Usina): {Imax_sis_calculado} {unidade_corrente}")
                            st.write(f"Vmax Calculado (Usina): {Vmax_sis_calculado} {unidade_tensao}")
                            st.write(f"Pmax Calculado (Usina): {Pmax_sis_calculado} {unidade_potencia}")

                    # Adiciona os novos dados ao histórico
                    novos_dados_df = pd.DataFrame(novos_dados)

                    # Atualiza o histórico no session state
                    st.session_state['inputs_history'] = pd.concat([st.session_state['inputs_history'], novos_dados_df], ignore_index=True)
                    
                    # Salva no cache
                    save_to_cache()

                    # Exibe o botão de download do CSV
                    csv_historico = novos_dados_df.to_csv(index=False)
                    st.download_button(
                        label=translator.translate("Download Updated CSV", dest=st.session_state.language).text,
                        data=csv_historico,
                        file_name="calculated_system_results.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(translator.translate("Please enter the values correctly.", dest=st.session_state.language).text)
    else:
        st.write(translator.translate("Work in Process (W.I.P)", dest=st.session_state.language).text)
