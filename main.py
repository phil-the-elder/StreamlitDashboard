import streamlit as st
import pandas as pd
import plotly.express as px
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(layout="wide")


@st.cache_data
def get_data():
    """
    This function reads the CO2 emission data from a CSV file, extracts unique country names,
    and identifies numeric variables for further analysis.

    Parameters:
    None

    Returns:
    df_total (pandas.DataFrame): The DataFrame containing the total CO2 emission data.
    countries (list): A list of unique country names present in the data.
    variables (list): A list of numeric variables present in the data.
    """
    df_total = pd.read_csv(os.path.join(current_dir, 'data/owid-co2-data.csv'))
    countries = df_total['country'].unique()
    variables = []
    for col in df_total.columns:
        if pd.api.types.is_numeric_dtype(df_total[col]):
            variables.append(col)
    return df_total, countries, variables


def set_column_1(column, df_total, variables):
    """
    This function sets up and displays a column in the Streamlit application.
    It creates a dropdown menu for selecting a variable, a slider for selecting a year,
    and two interactive world maps (scatter and choropleth) based on the selected variable and year.

    Parameters:
    column (st.Column): The Streamlit column object where the content will be displayed.
    df_total (pandas.DataFrame): The DataFrame containing the total CO2 emission data.
    variables (list): A list of variables available for selection.

    Returns:
    None
    """
    with column:
        first_year = df_total['year'].min()
        last_year = df_total['year'].max()
        variable = st.session_state['variable'] = st.selectbox('Select variable', variables)
        st.session_state['year'] = st.slider('Select year', first_year, last_year)
        p = 'equirectangular'
        max = df_total[variable].max()
        min = df_total[variable].min()
        kwargs = {
            'data_frame': df_total[df_total['year'] == st.session_state['year']],
            'locations': "iso_code",
            'color': variable,
            'size': variable,
            'hover_name': "country",
            'range_color': (min, max),
            'scope': 'world',
            'projection': p,
            'title': 'World CO2 Emissions',
            'template': 'plotly_dark',
            'color_continuous_scale': px.colors.sequential.Reds
        }

        fig1 = px.scatter_geo(**kwargs)
        fig1.update_layout(margin={'r': 0, 't': 0, 'b': 0, 'l': 0})
        del kwargs['size']
        fig2 = px.choropleth(**kwargs)
        fig2.update_layout(margin={'r': 0, 't': 0, 'b': 0, 'l': 0})

        map = st.radio("Choose the map style", ["Scatter", "Choropleth"], horizontal=True)
        fig = fig1 if map == 'Scatter' else fig2
        st.plotly_chart(fig, use_container_width=True)


def set_column_2(column, df_total, countries):
    """
    This function sets up and displays a column in the Streamlit application for country-specific data.
    It creates a multiselect dropdown menu for selecting countries, and two tabs for displaying a line graph
    and a table of data for the selected countries.

    Parameters:
    column (st.Column): The Streamlit column object where the content will be displayed.
    df_total (pandas.DataFrame): The DataFrame containing the total CO2 emission data.
    countries (list): A list of country names available for selection.

    Returns:
    None
    """
    variable = st.session_state['variable']
    with column:
        c = st.multiselect('Add a country:', countries, default=['United States', 'China', 'Russia', 'Germany'])
        tab1, tab2 = column.tabs(["Graph", "Table"])

        with tab1:
            fig = px.line(df_total[df_total['country'].isin(c)], x='year', y=variable, color='country')
            st.plotly_chart(fig, use_container_width=True)
        with tab2:
            table = df_total[df_total['year'] == st.session_state['year']]
            st.dataframe(table[table['country'].isin(c)], use_container_width=True)


def main():
    """
    The main function orchestrates the data processing, user interface setup,
    and visualization of global CO2 emission data.

    Parameters:
    None

    Returns:
    None
    """
    default_variable = 'co2'
    df_total, countries, variables = get_data()
    df_total.fillna(0, inplace=True)

    if 'year' not in st.session_state:
        st.session_state['year'] = df_total['year'].max()
    if 'variable' not in st.session_state:
        st.session_state['variable'] = default_variable

    colh1, colh2 = st.columns((4, 2))
    colh1.markdown("## Global CO2 Emissions")
    colh2.markdown("")

    col1, col2 = st.columns((8, 4))

    footer = st.container()
    footer.write("Global CO2 Emission Data from 1750 to 2021. Data derived, with thanks, \
                from [__*Our World in Data*__](https://ourworldindata.org/)")
    set_column_1(col1, df_total, variables)
    set_column_2(col2, df_total, countries)


if __name__ == "__main__":
    main()
