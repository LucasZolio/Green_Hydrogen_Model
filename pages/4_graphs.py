import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Gráficos",
    page_icon=":earth_americas:",
    layout="wide"
)

# Dicionário com as traduções em inglês e português
texts = {
    "en": {
        "title": "Results Graphs",
        "description": "Comparison between the Datasheet data and the calculated results based on Irradiance and Temperature.",
        "separator": "---",
        "upload_datasheet": "Upload the Datasheet data file",
        "upload_calculated": "Upload the calculated results (CSV)",
        "select_parameter": "Select the parameter to plot",
        "error_no_irradiance": "The calculated results file does not contain an Irradiance column.",
        "error_loading_files": "Error loading files.",
        "warning_upload": "Please upload both files.",
        "graph_title": "Graph of {parameter}: Calculated vs Reference",
        "xaxis_title": "Irradiance (W/m²)",
        "yaxis_titles": {
            "Imax": "Current (A)",
            "Vmax": "Voltage (V)",
            "Pmax": "Power (W)"
        }
    },
    "pt": {
        "title": "Gráficos dos Resultados",
        "description": "Comparação entre os dados do Datasheet e os resultados calculados com base na Irradiância e Temperatura.",
        "separator": "---",
        "upload_datasheet": "Faça o upload do arquivo de dados (Datasheet)",
        "upload_calculated": "Faça o upload dos resultados calculados (CSV)",
        "select_parameter": "Selecione o parâmetro para plotar",
        "error_no_irradiance": "O arquivo de resultados calculados não contém uma coluna de Irradiância.",
        "error_loading_files": "Erro ao carregar os arquivos.",
        "warning_upload": "Por favor, faça o upload de ambos os arquivos.",
        "graph_title": "Gráfico de {parameter}: Previsto vs Referência",
        "xaxis_title": "Irradiância (W/m²)",
        "yaxis_titles": {
            "Imax": "Corrente (A)",
            "Vmax": "Tensão (V)",
            "Pmax": "Potência (W)"
        }
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
    
# Exibir o conteúdo da página com base no idioma selecionado
with st.container():
    st.title(texts[st.session_state.language]["title"])
    st.write(texts[st.session_state.language]["description"])

with st.container():
    st.write(texts[st.session_state.language]["separator"])

# Função para carregar os dados do datasheet e os calculados
@st.cache_data
def load_data(datasheet_file, calculated_file):
    # Carregar os arquivos CSV
    try:
        datasheet = pd.read_csv(datasheet_file)
        calculated = pd.read_csv(calculated_file)
        return datasheet, calculated
    except Exception as e:
        st.error(f"Erro ao carregar os arquivos CSV: {e}")
        return None, None

# Função para gerar gráficos de comparação com base na seleção (Imax, Vmax, Pmax)
def plot_comparison(df, parameter, title, language):
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
        xaxis_title=texts[language]["xaxis_title"],
        yaxis_title=texts[language]["yaxis_titles"][parameter],
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

# Upload dos arquivos CSV (Datasheet e Resultados Calculados)
uploaded_datasheet = st.sidebar.file_uploader(texts[st.session_state.language]["upload_datasheet"], type=["csv"])
uploaded_calculated = st.sidebar.file_uploader(texts[st.session_state.language]["upload_calculated"], type=["csv"])

# Adicionando as opções de seleção para os parâmetros com Radio Buttons
selected_parameter = st.sidebar.radio(texts[st.session_state.language]["select_parameter"], options=['Imax', 'Vmax', 'Pmax'])

# Verificar se ambos os arquivos foram carregados corretamente
if uploaded_datasheet is not None and uploaded_calculated is not None:
    # Carregar os arquivos
    datasheet, calculated = load_data(uploaded_datasheet, uploaded_calculated)
    
    if datasheet is not None and calculated is not None:
        # Unir os dados de acordo com a Irradiância
        if 'Irradiance' in calculated.columns:
            df_combined = pd.merge(calculated, datasheet, how='left', on='Irradiance', suffixes=('_calculated', '_datasheet'))
        else:
            st.sidebar.error(texts[st.session_state.language]["error_no_irradiance"])
    else:
        st.sidebar.error(texts[st.session_state.language]["error_loading_files"])
else:
    st.sidebar.warning(texts[st.session_state.language]["warning_upload"])

# Verificar se os dados combinados estão prontos para exibir os gráficos
if 'df_combined' in locals():
    # Exibindo o gráfico selecionado com tradução de eixos
    with st.container():
        st.plotly_chart(plot_comparison(df_combined, selected_parameter, texts[st.session_state.language]["graph_title"].format(parameter=selected_parameter), st.session_state.language), use_container_width=True)

    # Separador final
    with st.container():
        st.write("---")
