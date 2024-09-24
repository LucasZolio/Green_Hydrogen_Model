import streamlit as st
import pandas as pd
import plotly.express as px
from googletrans import Translator

# Inicializa o tradutor
translator = Translator()

def graphs():
    # Verifica o estado da sessão para definir o idioma padrão
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  # Começa com inglês

    # Espaçamento de 50px abaixo dos botões de tradução
    st.write('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)

    # Função de tradução automática usando googletrans
    def translate_text(text, dest_language):
        try:
            return translator.translate(text, dest=dest_language).text
        except Exception as e:
            st.error(f"Translation failed: {e}")
            return text

    # Título e descrição da página
    title = "Graphs"
    description = "Comparison between the Datasheet data and the calculated results based on Irradiance and Temperature."

    # Traduz o título e a descrição com base no idioma selecionado
    if st.session_state.language == 'pt':
        title = translate_text("Gráficos", 'pt')
        description = translate_text("Comparison between the Datasheet data and the calculated results based on Irradiance and Temperature.", 'pt')

    st.title(title)
    st.write(description)

    # Função para carregar os dados do datasheet e os calculados
    @st.cache_data
    def load_data(datasheet_file, calculated_file):
        try:
            datasheet = pd.read_csv(datasheet_file)
            calculated = pd.read_csv(calculated_file)
            return datasheet, calculated
        except Exception as e:
            st.error(f"Erro ao carregar os arquivos CSV: {e}")
            return None, None

    # Função para armazenar os arquivos no cache
    def cache_files(file, key):
        if file is not None:
            st.session_state[key] = file
        return st.session_state.get(key)

    # Layout das importações dos arquivos lado a lado
    col1, col2 = st.columns(2)

    # Texto traduzido
    upload_datasheet_text = translate_text("Upload the Datasheet data file", 'pt') if st.session_state.language == 'pt' else "Upload the Datasheet data file"
    upload_calculated_text = translate_text("Upload the calculated results (CSV)", 'pt') if st.session_state.language == 'pt' else "Upload the calculated results (CSV)"
    select_parameter_text = translate_text("Select the parameter to plot", 'pt') if st.session_state.language == 'pt' else "Select the parameter to plot"

    with col1:
        uploaded_datasheet = st.file_uploader(upload_datasheet_text, type=["csv"], key="datasheet")
        datasheet_file = cache_files(uploaded_datasheet, 'datasheet_file')

    with col2:
        uploaded_calculated = st.file_uploader(upload_calculated_text, type=["csv"], key="calculated")
        calculated_file = cache_files(uploaded_calculated, 'calculated_file')

    # Layout dos radio buttons lado a lado
    col3, col4, col5 = st.columns(3)

    with col3:
        selected_parameter = st.radio(select_parameter_text, options=['Imax', 'Vmax', 'Pmax'], horizontal=True)

    # Função para gerar gráficos de comparação com base na seleção (Imax, Vmax, Pmax)
    def plot_comparison(df, parameter, title):
        # Criando scatter plot com customização do marker
        fig = px.scatter(df,
                        x='Irradiance',
                        y=[f'{parameter}_datasheet', f'{parameter}_calculated'],
                        labels={"variable": "Legenda", "value": f'{parameter} (A)'},
                        title=title)

        # Atualizando símbolos e cores dos markers
        fig.for_each_trace(lambda t: t.update(marker_symbol="x", marker_color="red")
                        if t.name == f'{parameter}_datasheet' else t.update(marker_symbol="circle", marker_color="blue"))

        # Customizando o layout e movendo a legenda para baixo
        fig.update_layout(
            xaxis_title=translate_text("Irradiance (W/m²)", 'pt') if st.session_state.language == 'pt' else "Irradiance (W/m²)",
            yaxis_title=translate_text("Current (A)", 'pt') if st.session_state.language == 'pt' else "Current (A)",
            legend_title_text='Tipo',
            legend=dict(
                orientation="h",  # Legenda horizontal
                yanchor="top",
                y=-0.2,  # Coloca a legenda abaixo do gráfico
                xanchor="center",
                x=0.5
            )
        )

        return fig

    # Verificar se ambos os arquivos foram carregados corretamente
    if datasheet_file is not None and calculated_file is not None:
        # Carregar os arquivos
        datasheet, calculated = load_data(datasheet_file, calculated_file)

        if datasheet is not None and calculated is not None:
            # Unir os dados de acordo com a Irradiância
            if 'Irradiance' in calculated.columns:
                df_combined = pd.merge(calculated, datasheet, how='left', on='Irradiance', suffixes=('_calculated', '_datasheet'))
            else:
                st.error(translate_text("The calculated results file does not contain an Irradiance column.", 'pt') if st.session_state.language == 'pt' else "The calculated results file does not contain an Irradiance column.")
        else:
            st.error(translate_text("Error loading files.", 'pt') if st.session_state.language == 'pt' else "Error loading files.")
    else:
        st.warning(translate_text("Please upload both files.", 'pt') if st.session_state.language == 'pt' else "Please upload both files.")

    # Verificar se os dados combinados estão prontos para exibir os gráficos
    if 'df_combined' in locals():
        # Exibindo o gráfico selecionado com tradução de eixos
        title = translate_text(f"Graph of {selected_parameter}: Predicted vs Reference", 'pt') if st.session_state.language == 'pt' else f"Graph of {selected_parameter}: Predicted vs Reference"
        with st.container():
            st.plotly_chart(plot_comparison(df_combined, selected_parameter, title), use_container_width=True)

        # Separador final
        with st.container():
            st.write("---") 