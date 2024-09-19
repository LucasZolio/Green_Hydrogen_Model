import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Green Hydrogen Predict",
    page_icon=":earth_americas:",
    layout="wide"
)

# Dicionário com as traduções em inglês e português
texts = {
    "en": {
        "title": "Green Hydrogen Predict",
        "description": "Enter the electrical data of the photovoltaic module!",
        "separator": "---",
        "upload_prompt": "Upload the photovoltaic module datasheet (CSV)",
        "upload_success": "Photovoltaic module electrical data successfully loaded and stored in cache!",
        "module_type": "Module Type: {}",
        "calc_real": "W.I.P",
        "calc_theoretical": "Select the calculation type",
        "irradiance_input": "Enter the Irradiance (W·m⁻²)",
        "temperature_input": "Enter the Temperature (°C)",
        "calc_button": "Calculate",
        "success_irradiance": "Irradiance: {} W·m⁻²",
        "success_temperature": "Temperature: {} °C",
        "result_imax": "Imax calculated: {} A",
        "result_vmax": "Vmax calculated: {} V",
        "result_pmax": "Pmax calculated: {} W",
        "error_csv_format": "The CSV file does not contain all the required columns. Please check the file format.",
        "error_no_cache": "Module data not found in cache. Please upload the CSV file.",
        "download_button": "Download Updated CSV",
        "error_values": "Please enter the values correctly."
    },
    "pt": {
        "title": "Modelo Preditivo de Hidrogênio Verde",
        "description": "Insira os dados elétricos do módulo fotovoltaico!",
        "separator": "---",
        "upload_prompt": "Faça o upload do datasheet do módulo fotovoltaico (CSV)",
        "upload_success": "Dados elétricos do módulo fotovoltaico carregados com sucesso e armazenados no cache!",
        "module_type": "Tipo de Módulo: {}",
        "calc_real": "Em Desenvolvimento",
        "calc_theoretical": "Selecione o tipo de cálculo",
        "irradiance_input": "Insira a Irradiância (W·m⁻²)",
        "temperature_input": "Insira a Temperatura (°C)",
        "calc_button": "Calcular",
        "success_irradiance": "Irradiância: {} W·m⁻²",
        "success_temperature": "Temperatura: {} °C",
        "result_imax": "Imax calculado: {} A",
        "result_vmax": "Vmax calculado: {} V",
        "result_pmax": "Pmax calculado: {} W",
        "error_csv_format": "O arquivo CSV não contém todas as colunas necessárias. Por favor, verifique o formato do arquivo.",
        "error_no_cache": "Dados do módulo não encontrados no cache. Por favor, faça o upload do arquivo CSV.",
        "download_button": "Baixar CSV Atualizado",
        "error_values": "Por favor, insira os valores corretamente."
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

# Inicializa o histórico no session_state, se ainda não existir
if 'inputs_history' not in st.session_state:
    try:
        st.session_state['inputs_history'] = pd.read_csv('/mnt/data/calculated_results.csv')
    except FileNotFoundError:
        st.session_state['inputs_history'] = pd.DataFrame(columns=['Module Type', 'Irradiance', 'Temperature', 'Imax_calculated', 'Vmax_calculated', 'Pmax_calculated'])

# Exibir o conteúdo da página com base no idioma selecionado
with st.container():
    st.title(texts[st.session_state.language]["title"])
    st.write(texts[st.session_state.language]["description"])

with st.container():
    st.write(texts[st.session_state.language]["separator"])

@st.cache_data
def carregar_dados_cache():
    if 'store_data' in st.session_state:
        return st.session_state['store_data']
    else:
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

if dados_eletricos is None:
    st.warning(texts[st.session_state.language]["error_no_cache"])
    upload_file = st.file_uploader(texts[st.session_state.language]["upload_prompt"], type="csv")
    
    if upload_file is not None:
        dados_eletricos = carregar_dados_datasheet(upload_file)
        if dados_eletricos is not None:
            st.success(texts[st.session_state.language]["upload_success"])
    else:
        st.stop()

if dados_eletricos is not None:
    try:
        module_type = dados_eletricos['module_type'].values[0]
        st.write(f"Module Type: {module_type}")
    except KeyError:
        st.error(texts[st.session_state.language]["error_csv_format"])
        st.stop()

    with st.sidebar:
        tipo_calculo = st.radio(texts[st.session_state.language]["calc_theoretical"], ("Real", "Teórico"))

    if tipo_calculo == "Real":
        st.write(texts[st.session_state.language]["calc_real"])
    
    if tipo_calculo == "Teórico":
        with st.container():
            irradiance = st.number_input(texts[st.session_state.language]["irradiance_input"], min_value=0.0, step=0.1)
            temperature = st.number_input(texts[st.session_state.language]["temperature_input"], min_value=-5.0, step=0.1)

            def calcular_parametros(T, G):
                if all(col in dados_eletricos.columns for col in ['isc_datasheet', 'voc_datasheet', 'Imax_datasheet', 'Vmax_datasheet', 'alpha', 'beta']):
                    isc = float(dados_eletricos['isc_datasheet'].values[0])
                    voc = float(dados_eletricos['voc_datasheet'].values[0])
                    imax = float(dados_eletricos['Imax_datasheet'].values[0])
                    vmax = float(dados_eletricos['Vmax_datasheet'].values[0])
                    alpha = float(dados_eletricos['alpha'].values[0])
                    beta = float(dados_eletricos['beta'].values[0])

                    Imax_calculado = imax * (G / Gref) * (1 + alpha * (T - Tref))
                    Vmax_calculado = vmax * (1 + beta * (T - Tref))
                    Pmax_calculado = round(Imax_calculado * Vmax_calculado, 2)

                    return Imax_calculado, Vmax_calculado, Pmax_calculado
                else:
                    st.error(texts[st.session_state.language]["error_csv_format"])
                    return None, None, None

            Tref = 25
            Gref = 1000

            if st.button(texts[st.session_state.language]["calc_button"]):
                if irradiance is not None and temperature is not None:
                    st.success(texts[st.session_state.language]["success_irradiance"].format(irradiance))
                    st.success(texts[st.session_state.language]["success_temperature"].format(temperature))

                    Imax_calculado, Vmax_calculado, Pmax_calculado = calcular_parametros(temperature, irradiance)

                    if Imax_calculado is not None:
                        st.write(texts[st.session_state.language]["result_imax"].format(round(Imax_calculado, 2)))
                        st.write(texts[st.session_state.language]["result_vmax"].format(round(Vmax_calculado, 2)))
                        st.write(texts[st.session_state.language]["result_pmax"].format(round(Pmax_calculado, 0)))

                        novo_input = pd.DataFrame({
                            'Module Type': [module_type],
                            'Irradiance': [irradiance],
                            'Temperature': [temperature],
                            'Imax_calculated': [round(Imax_calculado, 2)],
                            'Vmax_calculated': [round(Vmax_calculado, 2)],
                            'Pmax_calculated': [round(Pmax_calculado, 0)]
                        })

                        st.session_state['inputs_history'] = pd.concat([st.session_state['inputs_history'], novo_input], ignore_index=True)

                        with open('/mnt/data/calculated_theorical_results.csv', 'a') as f:
                            novo_input.to_csv(f, header=f.tell()==0, index=False)

                        csv_historico = st.session_state['inputs_history'].to_csv(index=False)
                        st.download_button(
                            label=texts[st.session_state.language]["download_button"],
                            data=csv_historico,
                            file_name="calculated_theorical_results.csv",
                            mime="text/csv"
                        )
                else:
                    st.error(texts[st.session_state.language]["error_values"])
