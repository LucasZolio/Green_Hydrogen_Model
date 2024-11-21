import streamlit as st
import pandas as pd
from googletrans import Translator

# Função para traduzir o texto, exceto para letras gregas e NOCT
def translate(text, lang, translator):
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
        "mu": mu,  # Salva o valor de mu
        "noct": noct,
        "cells": cells,
        "diode_factor": diode_factor,
        "Irradiance": irradiance,
        "Temperature": temperature  # Inclui o parâmetro de temperatura
    }

# Função para exportar em .csv
def export_csv(data_dict, calculated_data=None):
    # Inclui os dados calculados da usina, se fornecidos
    if calculated_data:
        data_dict.update(calculated_data)
    df = pd.DataFrame([data_dict])
    return df.to_csv(index=False)

# Função principal para cálculos de predição de hidrogênio verde
def data():
    # Inicializa o tradutor
    translator = Translator()

    # Define o idioma padrão como inglês
    if 'language' not in st.session_state:
        st.session_state.language = 'en'

    # Inicializa 'stored_data' no session_state se não estiver presente
    if 'stored_data' not in st.session_state:
        st.session_state['stored_data'] = {}

    # Definir o código do idioma (en = inglês, pt = português)
    lang_code = st.session_state.language

    # Dicas em português e inglês
    hints = {
        "en": {
            "alpha": "Short-Circuit Current Temperature Coefficient (α): Indicates the percentage variation of the short-circuit current with temperature.",
            "beta": "Open-Circuit Voltage Temperature Coefficient (β): Represents the percentage variation of the open-circuit voltage with temperature.",
            "gamma": "Power Temperature Coefficient (γ): Refers to the percentage variation of power with temperature.",
            "mu": "Efficiency (μ): Represents the percentage decrease in module efficiency per year.",
            "noct": "Nominal Operating Cell Temperature (NOCT): The temperature the module reaches under standard test conditions (800 W/m² irradiance, 20°C ambient temperature, and 1 m/s wind speed).",
            "cells": "Number of photovoltaic cells: Number of cells in the photovoltaic module.",
            "diode_factor": "Diode ideality factor: Represents the quality of the diode in the single diode model."
        },
        "pt": {
            "alpha": "Coeficiente de temperatura da corrente de curto-circuito (α): Indica a variação percentual da corrente de curto-circuito com a temperatura.",
            "beta": "Coeficiente de temperatura da tensão de circuito aberto (β): Representa a variação percentual da tensão de circuito aberto com a temperatura.",
            "gamma": "Coeficiente de temperatura da potência (γ): Refere-se a variação percentual da potência com a temperatura.",
            "mu": "Eficiência (μ): Representa a diminuição em percentual da eficiência do módulo por ano.",
            "noct": "Temperatura nominal de operação da célula (NOCT): Temperatura que o módulo alcança em condições padrão de teste (800 W/m² de irradiância, 20°C de temperatura ambiente, e 1 m/s de velocidade do vento).",
            "cells": "Número de células fotovoltaicas: Quantidade de células disponíveis no módulo fotovoltaico.",
            "diode_factor": "Fator de idealidade do diodo: Representa a qualidade do diodo no modelo de diodo simples."
        }
    }

    # Exibir o conteúdo da página com base no idioma selecionado
    with st.container():
        # Alteração dos títulos e descrições
        st.title(translate("Dados da folha de dados Dados elétricos", lang_code, translator))  # Título
        st.write(translate("Digite os dados elétricos do módulo fotovoltaico ou da Usina fotovoltaica!", lang_code, translator))  # Descrição

    with st.container():
        st.write("---")

    # Adicionar botões de rádio logo abaixo da linha
    source_type = st.radio(
        translate("Fonte de dados", lang_code, translator),
        [translate("Usina fotovoltaica", lang_code, translator), translate("Módulo fotovoltaico", lang_code, translator)]
    )

    if source_type == translate("Usina fotovoltaica", lang_code, translator):
        # Verifica se os dados já foram carregados no cache
        if 'stored_data' not in st.session_state or not st.session_state['stored_data']:
            st.warning("Dados do módulo não encontrados no cache. Faça o upload do arquivo CSV.")
        
        # Upload do arquivo CSV
        uploaded_file = st.file_uploader(translate("Carregue a folha de dados do módulo fotovoltaico (CSV)", lang_code, translator), type="csv")

        if uploaded_file:
            # Carregar os dados do CSV em um DataFrame
            df = pd.read_csv(uploaded_file)
            st.session_state['stored_data'] = df.to_dict(orient="records")[0]  # Armazena os dados no cache
            st.success("Dados elétricos do módulo fotovoltaico carregados e armazenados com sucesso em cache!")

        if 'stored_data' in st.session_state:
            # Verifique se as chaves existem antes de acessá-las
            if all(key in st.session_state['stored_data'] for key in ['Pmax_datasheet', 'Vmax_datasheet', 'Imax_datasheet']):
                pmax = st.session_state['stored_data']['Pmax_datasheet']
                vmax = st.session_state['stored_data']['Vmax_datasheet']
                imax = st.session_state['stored_data']['Imax_datasheet']
                mu = st.session_state['stored_data']['mu'] / 100 # Pega o valor de mu
            else:
                st.error("Os dados elétricos necessários não foram encontrados no arquivo CSV.")
                return
            
            # Adicionar botões de rádio para escolher antes ou após o inversor
            inversor_posicao = st.radio(translate("Posição de medição", lang_code, translator), 
                            [translate("Antes do Inversor", lang_code, translator), translate("Após o Inversor", lang_code, translator)])

            # Se "Antes do Inversor" estiver selecionado
            if inversor_posicao == translate("Antes do Inversor", lang_code, translator):
                # Seletor de tipo de conexão: agora com botões de rádio
                tipo_conexao = st.radio(translate("Tipo de Conexão", lang_code, translator), 
                                        [translate("Série", lang_code, translator), translate("Paralelo", lang_code, translator)])

                # Entradas numéricas para o número de módulos por string e número de strings com chaves únicas
                num_modulos = st.number_input(translate("Número de módulos por string", lang_code, translator), min_value=1, key="num_modulos")
                num_strings = st.number_input(translate("Número de strings", lang_code, translator), min_value=1, key="num_strings")

                # Função de cálculo com base na conexão
                if tipo_conexao == translate("Série", lang_code, translator):
                    Vmax_sis = vmax * num_modulos  # Tensão é somada em série
                    Imax_sis = imax  # Corrente é mantida
                elif tipo_conexao == translate("Paralelo", lang_code, translator):
                    Vmax_sis = vmax  # Tensão é mantida em paralelo
                    Imax_sis = imax * num_modulos  # Corrente é somada

                # Condicional para verificar se está "Antes do Inversor" e manter os cálculos e visualização como na figura
                Pmax_sis = pmax * num_modulos * num_strings * (1 - mu)  # Inclui a degradação de mu

                # Definir valores padrão
                unidade_tensao = "V"
                unidade_corrente = "A"
                unidade_potencia = "W"

                # Lógica de conversão para unidades maiores
                if Pmax_sis >= 1000000:
                    Pmax_sis = round(Pmax_sis / 1000000, 2)  # Converter para MW
                    unidade_potencia = "TW"
                elif Pmax_sis >= 1000:
                    Pmax_sis = round(Pmax_sis / 1000, 2)  # Converter para MW
                    unidade_potencia = "MW"
                else:
                    Pmax_sis = round(Pmax_sis, 2)  # Manter em W
                    unidade_potencia = "W"

                # Transformar valores de corrente
                if Imax_sis >= 1000:
                    Imax_sis = round(Imax_sis / 1000, 2)  # Converter para kA
                    unidade_corrente = "kA"
                else:
                    Imax_sis = round(Imax_sis, 2)  # Manter em A

                # Transformar valores de tensão
                if Vmax_sis >= 1000:
                    Vmax_sis = round(Vmax_sis / 1000, 2)  # Converter para kV
                    unidade_tensao = "kV"
                else:
                    Vmax_sis = round(Vmax_sis, 2)  # Manter em V

                # Exibir os resultados como na figura
                total_modulos = num_modulos * num_strings
                st.write(f"Total de módulos na usina: {total_modulos}")
                st.write(f"Corrente total da usina: {Imax_sis} {unidade_corrente}")
                st.write(f"Tensão total da usina: {Vmax_sis} {unidade_tensao}")
                st.write(f"Potência total da usina: {Pmax_sis} {unidade_potencia}")

                # Botão para salvar os dados em CSV (somente se for Antes do Inversor)
                calculated_data = {
                    "total_modulos": total_modulos,
                    "Imax_sis": Imax_sis,
                    "Vmax_sis": Vmax_sis,
                    "Pmax_sis": Pmax_sis
                }
                csv_data = export_csv(st.session_state['stored_data'], calculated_data)
                st.download_button(label=translate("Baixe CSV", lang_code, translator), data=csv_data, file_name="photovoltaic_plant_data.csv", mime="text/csv")

            # Se "Após o Inversor" estiver selecionado
            elif inversor_posicao == translate("Após o Inversor", lang_code, translator):
                # Definir dados do inversor
                Pinv_nom = st.number_input(translate("Potência nominal do inversor (kW)", lang_code, translator), min_value=1.0)
                Pinv_max = st.number_input(translate("Potência máxima do inversor (kW)", lang_code, translator), min_value=1.0)
                Iinv_max = st.number_input(translate("Corrente máxima do inversor (A)", lang_code, translator), min_value=1.0)
                Vinv_max = st.number_input(translate("Tensão máxima do inversor (V)", lang_code, translator), min_value=1.0)

                # Dados do módulo fotovoltaico
                Pmod = 300  # Potência do módulo em Watts
                num_modulos = 40  # Número de módulos, extraído do arquivo

                # Cálculo da potência total do arranjo
                P_arranjo = num_modulos * Pmod / 1000  # Converter para kW

                # Fator de dimensionamento
                FDI = (P_arranjo / Pinv_nom) * 100
                st.write(f"{translate('Fator de dimensionamento (FDI)', lang_code, translator)}: {round(FDI, 2)}%")

                # Verificar se a potência total do arranjo está dentro dos limites do inversor
                if P_arranjo > Pinv_max:
                    st.write(translate("A potência do arranjo excede a potência máxima do inversor.", lang_code, translator))
                else:
                    st.write(translate("A potência do arranjo está dentro dos limites do inversor.", lang_code, translator))

                # Número máximo de strings
                corrente_string = st.number_input(translate("Corrente por string (A)", lang_code, translator), min_value=1.0)
                num_strings_max = Iinv_max / corrente_string
                st.write(f"{translate('Número máximo de strings permitidos', lang_code, translator)}: {int(num_strings_max)}")

                # Exibir os resultados finais
                st.write(f"{translate('Potência total do arranjo', lang_code, translator)}: {round(P_arranjo, 2)} kW")

    else:
        # Lógica para Módulo fotovoltaico
        form_data = st.form(key="data_datasheet", clear_on_submit=True)
        # Obtendo a lista de tipos de módulos fotovoltaicos
        photovoltaic_module_type = ["Monocrystalline (m-Si)", "Polycrystalline (p-Si)", "Cadmium Telluride (CdTe)", "Copper Indium Gallium Selenide (CIGS)", "Perovskite"]

        # Traduzir a lista de tipos de módulos, se necessário
        photovoltaic_module_type_translated = [translate(module, lang_code, translator) for module in photovoltaic_module_type]

        with form_data:
            # Dividindo as entradas em 3 colunas
            col1, col2, col3 = st.columns(3)

            with col1:
                input_module_type = st.selectbox(translate("Selecione o tipo de módulo fotovoltaico a ser analisado:", lang_code, translator), photovoltaic_module_type_translated)
                input_power = st.number_input(translate("Potência (W):", lang_code, translator), min_value=0.0)
                input_voltage_max = st.number_input(translate("Tensão máxima (V):", lang_code, translator), min_value=0.0)
                input_current_max = st.number_input(translate("Corrente máxima (A):", lang_code, translator), min_value=0.0)
                input_voltage_open = st.number_input(translate("Tensão de circuito aberto (V):", lang_code, translator), min_value=0.0)

            with col2:
                input_current_short = st.number_input(translate("Corrente de curto-circuito (A):", lang_code, translator), min_value=0.0)
                input_alpha = st.number_input(
                    translate("α (%/°C):", lang_code, translator),
                    min_value=0.0,
                    format="%.5f",
                    help=hints[lang_code]["alpha"]
                )
                input_beta = st.number_input(
                    translate("β (%/°C):", lang_code, translator),
                    format="%.5f",
                    help=hints[lang_code]["beta"]
                )
                input_gamma = st.number_input(
                    translate("γ (%/°C):", lang_code, translator),
                    format="%.5f",
                    help=hints[lang_code]["gamma"]
                )
                input_mu = st.number_input(
                    translate("μ (%):", lang_code, translator),
                    min_value=0.0,
                    help=hints[lang_code]["mu"]
                ) / 100

            with col3:
                input_noct = st.number_input(
                    translate("NOCT (°C):", lang_code, translator),
                    min_value=0.0,
                    help=hints[lang_code]["noct"]
                )
                input_cells = st.number_input(
                    translate("Número de células fotovoltaicas da folha de dados:", lang_code, translator),
                    min_value=0,
                    help=hints[lang_code]["cells"]
                )
                input_diode_factor = st.number_input(
                    translate("Fator de idealidade do diodo:", lang_code, translator),
                    min_value=0.0,
                    help=hints[lang_code]["diode_factor"]
                )

            button_submit = form_data.form_submit_button(translate("Enviar", lang_code, translator))

        if button_submit:
            # Valores padrão para Irradiância e Temperatura
            input_irradiance = 1000  # Padrão: 1000 W/m²
            input_temperature = 25    # Padrão: 25°C

            # Salva os dados no cache usando st.session_state
            st.session_state['stored_data'] = store_data(input_module_type, input_power, input_voltage_max, input_current_max,
                                                        input_voltage_open, input_current_short, input_alpha, input_beta,
                                                        input_gamma, input_mu, input_noct, input_cells, input_diode_factor, 
                                                        input_irradiance, input_temperature)
            st.success(translate("Dados salvos com sucesso!", lang_code, translator))

        # Botão para salvar os dados em CSV (fora do formulário)
        if 'stored_data' in st.session_state:
            csv_data = export_csv(st.session_state['stored_data'])
            st.download_button(label=translate("Baixe CSV", lang_code, translator), data=csv_data, file_name="datasheet_data.csv", mime="text/csv")
