import streamlit as st
import pandas as pd
from googletrans import Translator

def data():
    # Inicializa o tradutor
    translator = Translator()

    # Função para traduzir o texto, exceto para letras gregas e NOCT
    def translate(text, lang):
        if any(greek in text for greek in ["α", "β", "γ", "μ", "NOCT"]):
            return text
        return translator.translate(text, dest=lang).text

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

    # Define o idioma padrão como inglês
    if 'language' not in st.session_state:
        st.session_state.language = 'en'

    # Inicializa 'stored_data' no session_state se não estiver presente
    if 'stored_data' not in st.session_state:
        st.session_state['stored_data'] = None

    # Definir o código do idioma (en = inglês, pt = português)
    lang_code = st.session_state.language

    # Dicas em português e inglês
    hints = {
        "en": {
            "alpha": "Short-Circuit Current Temperature Coefficient (α): Indicates the percentage variation of the short-circuit current with temperature.",
            "beta": "Open-Circuit Voltage Temperature Coefficient (β): Represents the percentage variation of the open-circuit voltage with temperature.",
            "gamma": "Power Temperature Coefficient (γ): Refers to the percentage variation of power with temperature.",
            "mu": "Annual degradation rate (μ): Represents the percentage decrease in module efficiency per year.",
            "noct": "Nominal Operating Cell Temperature (NOCT): The temperature the module reaches under standard test conditions (800 W/m² irradiance, 20°C ambient temperature, and 1 m/s wind speed).",
            "cells": "Number of photovoltaic cells: Number of cells in the photovoltaic module according to the datasheet.",
            "diode_factor": "Diode ideality factor: Represents the quality of the diode in the single diode model."
        },
        "pt": {
            "alpha": "Coeficiente de temperatura da corrente de curto-circuito (α): Indica a variação percentual da corrente de curto-circuito com a temperatura.",
            "beta": "Coeficiente de temperatura da tensão de circuito aberto (β): Representa a variação percentual da tensão de circuito aberto com a temperatura.",
            "gamma": "Coeficiente de temperatura da potência (γ): Refere-se à variação percentual da potência com a temperatura.",
            "mu": "Taxa de degradação anual (μ): Representa a diminuição percentual da eficiência do módulo por ano.",
            "noct": "Temperatura nominal de operação da célula (NOCT): Temperatura que o módulo alcança em condições padrão de teste (800 W/m² de irradiância, 20°C de temperatura ambiente, e 1 m/s de velocidade do vento).",
            "cells": "Número de células fotovoltaicas: Quantidade de células no módulo fotovoltaico conforme o datasheet.",
            "diode_factor": "Fator de idealidade do diodo: Representa a qualidade do diodo no modelo de diodo simples."
        }
    }

    # Exibir o conteúdo da página com base no idioma selecionado
    with st.container():
        # Alteração dos títulos e descrições
        st.title(translate("Dados da folha de dados Dados elétricos", lang_code))  # Título 2 no lugar do Título 1
        st.write(translate("Digite os dados elétricos do módulo fotovoltaico!", lang_code))  # Descrição 2 no lugar da Descrição 1

    with st.container():
        st.write("---")

    with st.container():
        form_data = st.form(key="data_datasheet", clear_on_submit=True)
        # Obtendo a lista de tipos de módulos fotovoltaicos
        photovoltaic_module_type = ["Monocrystalline (m-Si)", "Polycrystalline (p-Si)", "Cadmium Telluride (CdTe)", "Copper Indium Gallium Selenide (CIGS)", "Perovskite"]
        
        # Traduzir a lista de tipos de módulos, se necessário
        photovoltaic_module_type_translated = [translate(module, lang_code) for module in photovoltaic_module_type]

        with form_data:
            # Dividindo as entradas em 3 colunas
            col1, col2, col3 = st.columns(3)

            with col1:
                input_module_type = st.selectbox(translate("Select the type of photovoltaic module to be analyzed:", lang_code), photovoltaic_module_type_translated)
                input_power = st.number_input(translate("Power (W):", lang_code), min_value=0.0)
                input_voltage_max = st.number_input(translate("Maximum Voltage (V):", lang_code), min_value=0.0)
                input_current_max = st.number_input(translate("Maximum Current (A):", lang_code), min_value=0.0)
                input_voltage_open = st.number_input(translate("Open-Circuit Voltage (V):", lang_code), min_value=0.0)

            with col2:
                input_current_short = st.number_input(translate("Short-Circuit Current (A):", lang_code), min_value=0.0)          
                input_alpha = st.number_input(
                    translate("α (%/°C):", lang_code),
                    min_value=0.0,
                    format="%.5f",
                    help=hints[lang_code]["alpha"]
                )
                input_beta = st.number_input(
                    translate("β (%/°C):", lang_code),
                    format="%.5f",
                    help=hints[lang_code]["beta"]
                )
                input_gamma = st.number_input(
                    translate("γ (%/°C):", lang_code),
                    format="%.5f",
                    help=hints[lang_code]["gamma"]
                )
                input_mu = st.number_input(
                    translate("μ (%):", lang_code),
                    min_value=0.0,
                    help=hints[lang_code]["mu"]
                ) / 100
                    
            with col3:
                input_noct = st.number_input(
                    translate("NOCT (°C):", lang_code),
                    min_value=0.0,
                    help=hints[lang_code]["noct"]
                )
                input_cells = st.number_input(
                    translate("Number of photovoltaic cells from the datasheet:", lang_code),
                    min_value=0,
                    help=hints[lang_code]["cells"]
                )
                input_diode_factor = st.number_input(
                    translate("Diode ideality factor:", lang_code),
                    min_value=0.0,
                    help=hints[lang_code]["diode_factor"]
                )

            # Definindo Irradiância e Temperatura padrão
            input_irradiance = 1000  # Padrão: 1000 W/m²
            input_temperature = 25    # Padrão: 25°C

        button_submit = form_data.form_submit_button(translate("Submit", lang_code))

        if button_submit:
            # Salva os dados no cache usando st.session_state
            st.session_state['stored_data'] = store_data(input_module_type, input_power, input_voltage_max, input_current_max,
                                                         input_voltage_open, input_current_short, input_alpha, input_beta,
                                                         input_gamma, input_mu, input_noct, input_cells, input_diode_factor, input_irradiance, input_temperature)
            st.success(translate("Data saved successfully!", lang_code))

    # Exibe os dados armazenados e oferece a opção de exportação
    if st.session_state['stored_data']:
        # Exibir os dados armazenados
        st.write(translate("Data saved in cache:", lang_code))
        st.write(st.session_state['stored_data'])

        # Opção para exportar os dados
        st.write(translate("Export Data", lang_code))
        export_format = st.radio(translate("Choose the format:", lang_code), ("CSV"))

        if export_format == "CSV":
            csv_data = export_csv(st.session_state['stored_data'])
            st.download_button(label=translate("Download CSV", lang_code), data=csv_data, file_name="datasheet_data.csv", mime="text/csv")
