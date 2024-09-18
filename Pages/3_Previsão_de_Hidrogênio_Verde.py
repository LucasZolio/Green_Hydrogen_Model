import pandas as pd
import streamlit as st

with st.container():
    st.title("Previsão de Hidrôgenio Verde")
    st.write("Insira os dados elétricos do módulo fotovoltaico!")

with st.container():
    st.write("---")

# Criação dos campos de entrada
with st.container():
    irradiance = st.number_input("Insira a Irradiância (W·m⁻²)", min_value=0.0, step=0.1)
    temperature = st.number_input("Insira a Temperatura (°C)", min_value=-5.0, step=0.1)


    # Função para ler os dados do datasheet do módulo e usar cache
    @st.cache_data
    def carregar_dados_datasheet(arquivo_csv):
        return pd.read_csv(arquivo_csv)


    # Carrega os dados elétricos do datasheet
    upload_file = st.file_uploader("Faça o upload do datasheet do módulo fotovoltaico (CSV)", type="csv")
    if upload_file is not None:
        dados_eletricos = carregar_dados_datasheet(upload_file)
        st.write("Dados elétricos do módulo fotovoltaico carregados com sucesso!")

    else:
        st.warning("Por favor, faça o upload do arquivo CSV do datasheet para continuar.")
        st.stop()


    # Função para calcular os parâmetros elétricos
    def calcular_parametros(T, G):
        isc = float(dados_eletricos['current_short'].values[0])
        voc = float(dados_eletricos['voltage_open'].values[0])
        imax = float(dados_eletricos['current_max'].values[0])
        vmax = float(dados_eletricos['voltage_max'].values[0])
        alpha = float(dados_eletricos['alpha'].values[0])
        beta = float(dados_eletricos['beta'].values[0])

        # Cálculos ajustados com base na temperatura e irradiância
        Imax_calculado = (imax + alpha * ((T + 273.15) - Tref) * (G / Gref))
        Vmax_calculado = vmax * (1 + beta * ((T + 273.15) - Tref))
        Pmax_calculado = round(Imax_calculado * Vmax_calculado, 2)

        return Imax_calculado, Vmax_calculado, Pmax_calculado


    # Constantes de referência
    Tref = 25  # Temperatura de referência (°C)
    Gref = 1000  # Irradiância de referência (W·m⁻²)

    # Botão que realiza o calculo de previsão
    if st.button("Calcular"):
        # Validação e exibição dos dados inseridos
        if irradiance and temperature:
            st.success(f"Irradiância: {irradiance} W·m⁻²")
            st.success(f"Temperatura: {temperature} °C")

            # Chama a função de cálculo de parâmetros
            Imax_calculado, Vmax_calculado, Pmax_calculado = calcular_parametros(temperature, irradiance)

            # Exibe os resultados
            st.write(f"Imax ajustado: {round(Imax_calculado, 2)} A")
            st.write(f"Vmax ajustado: {round(Vmax_calculado, 2)} V")
            st.write(f"Pmax calculado: {round(Pmax_calculado, 0)} W")

        else:
            st.error("Por favor, insira os valores corretamente.")
