import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# Função para carregar os dados da API
@st.cache_data
def load_data(parameters_subset, latitude, longitude, start_date, end_date):
    url = f'https://power.larc.nasa.gov/api/temporal/daily/point?parameters={parameters_subset}&community=SB&longitude={longitude}&latitude={latitude}&start={start_date}&end={end_date}&format=CSV'
    response = requests.get(url)
    data = response.text
    data_parts = data.split('-END HEADER-')
    actual_data = data_parts[1].strip()
    df = pd.read_csv(io.StringIO(actual_data))
    df.replace(-999, pd.NA, inplace=True)
    return df

# Definindo os parâmetros
parameters = ['PRECTOTCORR']
parameters_subset = ','.join(parameters)

# Função principal que será executada pelo Streamlit
def main():
    # Interface do Streamlit
    st.title('Visualização de Chuva Acumulada Satélite NASA Power 🌧⛈🌦')
    st.write('Selecione a localização e o período de data para visualizar a chuva acumulada.')

    # Inputs de latitude e longitude
    latitude = st.number_input("Latitude", -90.0, 90.0, -22.805694)
    longitude = st.number_input("Longitude", -180.0, 180.0, -50.481333)

    # Seleção de data
    start_date = st.date_input("Data de Início", pd.to_datetime('2023-04-01'))
    end_date = st.date_input("Data de Fim", pd.to_datetime('2024-07-09'))

    if start_date > end_date:
        st.error("A data de início deve ser anterior à data de fim.")
    else:
        # Carregar os dados
        df = load_data(parameters_subset, latitude, longitude, start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))
        
        # Verificar a estrutura do DataFrame
        st.write("Estrutura do DataFrame:")
        st.write(df.head())
        st.write("Colunas disponíveis:", df.columns)

        # Preencher valores NA com 0 antes de converter para float
        df['PRECTOTCORR'] = df['PRECTOTCORR'].fillna(0).astype(float)
        df['Chuva_Acum'] = df['PRECTOTCORR'].cumsum()  # Chuva acumulada

        # Criar a coluna 'DATE' a partir das colunas 'YEAR', 'MO', 'DY'
        if all(col in df.columns for col in ['YEAR', 'MO', 'DY']):
            df['DATE'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MO'].astype(str).str.zfill(2) + '-' + df['DY'].astype(str).str.zfill(2))
            df['DATE'] = df['DATE'].dt.strftime('%d/%m/%Y')
        else:
            st.error("Não foi possível encontrar colunas adequadas para formar a data.")

        # Exibir a tabela de dados
        st.write('Tabela de Dados')
        st.dataframe(df[['DATE', 'PRECTOTCORR', 'Chuva_Acum']])

        # Calcular o total de chuva acumulada
        total_chuva_acumulada = df['Chuva_Acum'].iloc[-1]
        st.write(f"Total de Chuva Acumulada no Período Selecionado: {total_chuva_acumulada:.2f} mm")

        # Exibir o gráfico de Chuva Acumulada com Plotly
        st.write('Gráfico de Chuva Acumulada')
        fig = px.line(df, x='DATE', y='Chuva_Acum', title='Chuva Acumulada ao Longo do Tempo', labels={'DATE': 'Data', 'Chuva_Acum': 'Chuva Acumulada (mm)'})
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
