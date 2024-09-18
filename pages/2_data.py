import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Hidrogênio Verde",
    page_icon="earth_americas",
    layout="wide"
)


# Função para armazenar os dados no cache
@st.cache_data
def store_data(module_type, pmax, vmax, imax, voc, isc, alpha, beta, gamma, mu, noct, cells, diode_factor):
    return {
        "module_type": module_type,
        "power": pmax,
        "voltage_max": vmax,
        "current_max": imax,
        "voltage_open": voc,
        "current_short": isc,
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "mu": mu,
        "noct": noct,
        "cells": cells,
        "diode_factor": diode_factor
    }


# Função para exportar em .csv
def export_csv(data_dict):
    df = pd.DataFrame([data_dict])
    return df.to_csv(index=False)


# Função para exportar em .txt
def export_txt(data_dict):
    lines = [f"{key}: {value}" for key, value in data_dict.items()]
    return "\n".join(lines)


# Interface
with st.container():
    st.title("Dados Elétricos do Datasheet")
    st.write("Insira os dados elétricos do módulo fotovoltaico!")

with st.container():
    st.write("---")

with st.container():
    form_data = st.form(key="data_datasheet", clear_on_submit=True)
    photovoltaic_module_type = ["Monocristalino (m-Si)", "Policristalino (p-Si)", "Telureto de Cádmio (CdTe)",
                                "Cobre-índio-gálio-selênio (CIGS)", "Perovskita"]

    with form_data:
        input_module_type = st.selectbox("Selecione o tipo de Módulo fotovoltaico a ser analisado: ",
                                         photovoltaic_module_type)

        # Dados do Datasheet
        input_power = st.number_input("Potência (W):", min_value=0.0)
        input_voltage_max = st.number_input("Tensão Máxima (em STC) (V):", min_value=0.0)
        input_current_max = st.number_input("Corrente Máxima (em STC) (A):", min_value=0.0)
        input_voltage_open = st.number_input("Tensão de circuito aberto (em STC) (V):", min_value=0.0)
        input_current_short = st.number_input("Corrente de curto-circuito (em STC) (A):", min_value=0.0)
        input_alpha = st.number_input("α em STC do datasheet (%/°C):", min_value=0.0, format="%.5f")
        input_beta = st.number_input("β em STC do datasheet (%/°C):", format="%.5f")
        input_gamma = st.number_input("γ em STC do datasheet (%/°C):", format="%.5f")
        input_mu = st.number_input("μ (%):", min_value=0.0) / 100
        input_noct = st.number_input("NOCT (°C):", min_value=0.0)
        input_cells = st.number_input("Número de células fotovoltaicas do datasheet:", min_value=0)
        input_diode_factor = st.number_input("Fator de idealidade do diodo:", min_value=0.0)

    button_submit = form_data.form_submit_button("Confirma")

    # Inicializa stored_data como None
    stored_data = None

    if button_submit:
        # Salva os dados no cache
        stored_data = store_data(input_module_type, input_power, input_voltage_max, input_current_max,
                                 input_voltage_open, input_current_short, input_alpha, input_beta, input_gamma,
                                 input_mu, input_noct, input_cells, input_diode_factor)
        st.success("Dados salvos com sucesso!")

    if stored_data:
        # Opção para exportar os dados
        st.write("Exportar dados")
        export_format = st.radio("Escolha o formato:", ("CSV", "TXT"))

        if export_format == "CSV":
            csv_data = export_csv(stored_data)
            st.download_button(label="Baixar CSV", data=csv_data, file_name="dados_datasheet.csv", mime="text/csv")
