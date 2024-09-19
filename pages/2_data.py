import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Datasheet Data",
    page_icon="earth_americas",
    layout="wide"
)

# Dicionário com as traduções em inglês e português
texts = {
    "en": {
        "title": "Datasheet Electrical Data",
        "description": "Enter the electrical data of the photovoltaic module!",
        "separator": "---",
        "module_type_label": "Select the type of photovoltaic module to be analyzed:",
        "module_types": ["Monocrystalline (m-Si)", "Polycrystalline (p-Si)", "Cadmium Telluride (CdTe)", "Copper Indium Gallium Selenide (CIGS)", "Perovskite"],
        "power_label": "Power (W):",
        "voltage_max_label": "Maximum Voltage (V):",
        "current_max_label": "Maximum Current (A):",
        "voltage_open_label": "Open-Circuit Voltage (V):",
        "current_short_label": "Short-Circuit Current (A):",
        "alpha_label": "α from datasheet (%/°C):",
        "beta_label": "β from datasheet (%/°C):",
        "gamma_label": "γ from datasheet (%/°C):",
        "mu_label": "μ (%):",
        "noct_label": "NOCT (°C):",
        "cells_label": "Number of photovoltaic cells from the datasheet:",
        "diode_factor_label": "Diode ideality factor:",
        "submit_label": "Submit",
        "success_message": "Data saved successfully!",
        "cached_data": "Data saved in cache:",
        "export_data": "Export Data",
        "choose_format": "Choose the format:",
        "download_csv": "Download CSV"
    },
    "pt": {
        "title": "Dados Elétricos do Datasheet",
        "description": "Insira os dados elétricos do módulo fotovoltaico!",
        "separator": "---",
        "module_type_label": "Selecione o tipo de módulo fotovoltaico a ser analisado:",
        "module_types": ["Monocristalino (m-Si)", "Policristalino (p-Si)", "Telureto de Cádmio (CdTe)", "Seleneto de Cobre, Índio e Gálio (CIGS)", "Perovskita"],
        "power_label": "Potência (W):",
        "voltage_max_label": "Tensão Máxima (V):",
        "current_max_label": "Corrente Máxima (A):",
        "voltage_open_label": "Tensão de Circuito Aberto (V):",
        "current_short_label": "Corrente de Curto-Circuito (A):",
        "alpha_label": "α do datasheet (%/°C):",
        "beta_label": "β do datasheet (%/°C):",
        "gamma_label": "γ do datasheet (%/°C):",
        "mu_label": "μ (%):",
        "noct_label": "NOCT (°C):",
        "cells_label": "Número de células fotovoltaicas do datasheet:",
        "diode_factor_label": "Fator de idealidade do diodo:",
        "submit_label": "Enviar",
        "success_message": "Dados salvos com sucesso!",
        "cached_data": "Dados salvos em cache:",
        "export_data": "Exportar Dados",
        "choose_format": "Escolha o formato:",
        "download_csv": "Baixar CSV"
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

# Função para armazenar os dados no cache
@st.cache_data
def store_data(module_type, pmax, vmax, imax, voc, isc, alpha, beta, gamma, mu, noct, cells, diode_factor, irradiance, temperature):
    return {
        "module_type": module_type,
        "Pmax_datasheet": pmax,
        "Vmax_datasheet": vmax,
        "Imax_datasheet": imax,
        "voc_datasheet": voc,
        "isc_datasheet": isc,
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "mu": mu,
        "noct": noct,
        "cells": cells,
        "diode_factor": diode_factor,
        "Irradiance": irradiance,
        "Temperature": temperature
    }

# Função para exportar em .csv
def export_csv(data_dict):
    df = pd.DataFrame([data_dict])
    return df.to_csv(index=False)

# Inicializa os dados armazenados na sessão se não existirem
if 'stored_data' not in st.session_state:
    st.session_state['stored_data'] = None

# Exibir o conteúdo da página com base no idioma selecionado
with st.container():
    st.title(texts[st.session_state.language]["title"])
    st.write(texts[st.session_state.language]["description"])

with st.container():
    st.write(texts[st.session_state.language]["separator"])

with st.container():
    form_data = st.form(key="data_datasheet", clear_on_submit=True)
    # Obtendo a lista de tipos de módulos fotovoltaicos com base no idioma
    photovoltaic_module_type = texts[st.session_state.language]["module_types"]

    with form_data:
        # Dividindo as entradas em 3 colunas
        col1, col2, col3 = st.columns(3)

        with col1:
            input_module_type = st.selectbox(texts[st.session_state.language]["module_type_label"], photovoltaic_module_type)
            input_power = st.number_input(texts[st.session_state.language]["power_label"], min_value=0.0)
            input_voltage_max = st.number_input(texts[st.session_state.language]["voltage_max_label"], min_value=0.0)
            input_current_max = st.number_input(texts[st.session_state.language]["current_max_label"], min_value=0.0)
            input_voltage_open = st.number_input(texts[st.session_state.language]["voltage_open_label"], min_value=0.0)

        with col2:
            input_current_short = st.number_input(texts[st.session_state.language]["current_short_label"], min_value=0.0)          
            input_alpha = st.number_input(texts[st.session_state.language]["alpha_label"], min_value=0.0, format="%.5f")
            input_beta = st.number_input(texts[st.session_state.language]["beta_label"], format="%.5f")
            input_gamma = st.number_input(texts[st.session_state.language]["gamma_label"], format="%.5f")
            input_mu = st.number_input(texts[st.session_state.language]["mu_label"], min_value=0.0) / 100
            
        with col3:
            input_noct = st.number_input(texts[st.session_state.language]["noct_label"], min_value=0.0)
            input_cells = st.number_input(texts[st.session_state.language]["cells_label"], min_value=0)
            input_diode_factor = st.number_input(texts[st.session_state.language]["diode_factor_label"], min_value=0.0)

        # Definindo Irradiância e Temperatura padrão
        input_irradiance = 1000  # Padrão: 1000 W/m²
        input_temperature = 25    # Padrão: 25°C

    button_submit = form_data.form_submit_button(texts[st.session_state.language]["submit_label"])

    if button_submit:
        # Salva os dados no cache usando st.session_state
        st.session_state['stored_data'] = store_data(input_module_type, input_power, input_voltage_max, input_current_max,
                                                     input_voltage_open, input_current_short, input_alpha, input_beta,
                                                     input_gamma, input_mu, input_noct, input_cells, input_diode_factor, input_irradiance, input_temperature)
        st.success(texts[st.session_state.language]["success_message"])

# Exibe os dados armazenados e oferece a opção de exportação
if st.session_state['stored_data']:
    # Exibir os dados armazenados
    st.write(texts[st.session_state.language]["cached_data"])
    st.write(st.session_state['stored_data'])

    # Opção para exportar os dados
    st.write(texts[st.session_state.language]["export_data"])
    export_format = st.radio(texts[st.session_state.language]["choose_format"], ("CSV"))

    if export_format == "CSV":
        csv_data = export_csv(st.session_state['stored_data'])
        st.download_button(label=texts[st.session_state.language]["download_csv"], data=csv_data, file_name="datasheet_data.csv", mime="text/csv")
