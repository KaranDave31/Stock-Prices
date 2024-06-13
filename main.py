import streamlit as st
import pandas as pd
import os
import io
import matplotlib.pyplot as plt

st.title('Stock Analysis Project')

# Sidebar for navigation
st.sidebar.title('Navigation')
section = st.sidebar.selectbox('Go to', ['Master DataFrame Options', 'Sorting Options', 'Plotting Options', 'Other Financial Options'])

# File uploader
uploaded_files = st.file_uploader("Select your CSV file/files", accept_multiple_files=True, type=["csv"])

dfs = {}
if uploaded_files:
    for uploaded_file in uploaded_files:
        date_part = os.path.basename(uploaded_file.name).split('_')[0]
        dfs[date_part] = pd.read_csv(uploaded_file)
    st.write("Files uploaded successfully.")
else:
    st.write("No file uploaded")

if 'master_df_created' not in st.session_state:
    st.session_state.master_df_created = False

if 'start_date' not in st.session_state:
    st.session_state.start_date = None

if 'end_date' not in st.session_state:
    st.session_state.end_date = None

if 'sort_column' not in st.session_state:
        st.session_state.sort_column = 'OPEN'

# Master DataFrame Options
if section == 'Master DataFrame Options':
    st.sidebar.subheader("Master DataFrame Options")

    if st.sidebar.button('Create a master dataframe'):
        if dfs:
            st.session_state.master_df_created = True
            st.session_state.master_df = pd.concat(dfs.values(), ignore_index=True)
            st.subheader('Master DataFrame head')
            st.write(st.session_state.master_df.head())
        else:
            st.write("No dataframes to concatenate")

    if st.session_state.master_df_created:
        if st.sidebar.button('Show DataFrame Info'):
            buffer = io.StringIO()
            st.session_state.master_df.info(buf=buffer)
            s = buffer.getvalue()
            st.text(s)

        if st.sidebar.button('Show Null Values'):
            st.write(st.session_state.master_df.isnull().sum())

        if st.sidebar.button('Drop Null Values from master dataframe'):
            st.session_state.master_df = st.session_state.master_df.dropna()
            st.subheader('Master DataFrame after Dropping Null Values')
            st.write(st.session_state.master_df.head())

        if st.sidebar.button('Convert TIMESTAMP to datetime and set as index'):
            if 'TIMESTAMP' in st.session_state.master_df.columns:
                st.session_state.master_df['TIMESTAMP'] = pd.to_datetime(st.session_state.master_df['TIMESTAMP'], infer_datetime_format=True)
                st.session_state.master_df = st.session_state.master_df.set_index(['TIMESTAMP'])
                st.subheader('Master DataFrame after Converting TIMESTAMP')
                st.write(st.session_state.master_df.head())
                st.session_state.start_date = st.session_state.master_df.index.min()
                st.session_state.end_date = st.session_state.master_df.index.max()

                st.write(f"Start Date: {st.session_state.start_date}")
                st.write(f"End Date: {st.session_state.end_date}")

# Sorting Options
if section == 'Sorting Options' and st.session_state.master_df_created:
    st.sidebar.subheader("Sorting Options")

    start_date = st.sidebar.date_input('Start Date', value=st.session_state.start_date, key='sort_start_date')
    end_date = st.sidebar.date_input('End Date', value=st.session_state.end_date, key='sort_end_date')

    # Update session state with selected dates
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date

    columns = ('OPEN', 'CLOSE', 'HIGH', 'LOW', 'LAST', 'PREVCLOSE', 'TOTTRDVAL', 'TOTAL TRADES')
    st.session_state.sort_column = st.sidebar.selectbox('Select column to sort by', columns, index=columns.index(st.session_state.sort_column))


    if st.sidebar.button('Display Sorted DataFrame in Ascending Order', key='sort_asc'):
        df_sorted_asc = st.session_state.master_df.loc[st.session_state.start_date:st.session_state.end_date].sort_values(st.session_state.sort_column)
        st.subheader('Sorted DataFrame (Ascending Order)')
        st.write(df_sorted_asc)

    if st.sidebar.button('Display Sorted DataFrame in Descending Order', key='sort_desc'):
        df_sorted_desc = st.session_state.master_df.loc[st.session_state.start_date:st.session_state.end_date].sort_values(st.session_state.sort_column, ascending=False)
        st.subheader('Sorted DataFrame (Descending Order)')
        st.write(df_sorted_desc)

# Plotting Options
if section == 'Plotting Options' and st.session_state.master_df_created:
    st.sidebar.subheader("Plotting Options")

    start_date_plot = st.sidebar.date_input('Start Date', value=st.session_state.start_date, key='plot_start_date')
    end_date_plot = st.sidebar.date_input('End Date', value=st.session_state.end_date, key='plot_end_date')

    # Update session state with selected dates
    st.session_state.start_date_plot = start_date_plot
    st.session_state.end_date_plot = end_date_plot

    if 'plot_graph' not in st.session_state:
        st.session_state.plot_graph = 'line'

    plot_types = ('line', 'bar', 'scatter', 'area', 'hist')
    st.session_state.plot_graph = st.sidebar.selectbox('Select plot type', plot_types, index=plot_types.index(st.session_state.plot_graph), key='plot_type')

    columns = ('SYMBOL','OPEN', 'CLOSE', 'HIGH', 'LOW', 'LAST', 'PREVCLOSE', 'TOTTRDVAL', 'TOTAL TRADES')
    x_column = st.sidebar.selectbox('Select X column', columns, key='x_column')
    y_column = st.sidebar.selectbox('Select Y column', columns, key='y_column')
    length = st.sidebar.number_input('Select length for plotting', min_value=1, max_value=len(st.session_state.master_df), value=10, step=1, key='plot_length')

    def display_plot(startDate, endDate, length, Xcolumn, Ycolumn, plotkind='line', figureSize=(15, 6)):
        df = st.session_state.master_df.loc[startDate:endDate].head(length)
        
        fig, ax = plt.subplots(figsize=figureSize)
        df.plot(kind=plotkind, x=Xcolumn, y=Ycolumn, ax=ax)
       
        plt.xticks(rotation=90, ha='right')
        plt.tight_layout()
        
        st.pyplot(fig)

    if st.sidebar.button('Display plot', key='display_plot'):
        display_plot(st.session_state.start_date_plot, st.session_state.end_date_plot, length, x_column, y_column, st.session_state.plot_graph)

# Other Financial Options (placeholder for additional functionality)
if section == 'Other Financial Options' and st.session_state.master_df_created:
    st.sidebar.subheader("Other Financial Options")

    start_date = st.sidebar.date_input('Start Date', value=st.session_state.start_date, key='plot_start')
    end_date = st.sidebar.date_input('End Date', value=st.session_state.end_date, key='plot_end')

    # Update session state with selected dates
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date


    symbols = st.session_state.master_df['SYMBOL'].unique() if 'SYMBOL' in st.session_state.master_df.columns else []
    selected_symbol = st.sidebar.selectbox('Select Symbol', symbols)

    def calculate_daily_returns(startDate, endDate,symbol):
        df = st.session_state.master_df[startDate:endDate]
        df = df[df['SYMBOL'] == symbol]
        df['Daily Return'] = df['CLOSE'].pct_change()
        return df[['SYMBOL', 'SERIES', 'Daily Return']].dropna()

    def calculate_cumulative_returns(startDate, endDate,symbol):
        df = calculate_daily_returns(startDate, endDate,symbol)
        df = df[df['SYMBOL'] == symbol]
        df['Cumulative Return'] = (1 + df['Daily Return']).cumprod()
        return df[['SYMBOL', 'SERIES', 'Cumulative Return']].dropna()

    if st.sidebar.button('Display daily returns', key='display_daily_returns'):
        st.write(calculate_daily_returns(st.session_state.start_date, st.session_state.end_date,selected_symbol))

    if st.sidebar.button('Display cumulative return', key='display_cumulative_return'):
        st.write(calculate_cumulative_returns(st.session_state.start_date, st.session_state.end_date,selected_symbol))




