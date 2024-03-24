import streamlit as st
import pandas as pd
import plotly.express as px
import locale
#locale.setlocale(locale.LC_ALL, '')

def dash():
    
    #with open('./style.css') as f:
        #css = f.read()
    # Title input
    dashboard_title = st.sidebar.text_input("Enter the title of the dashboard:")
    st.title(dashboard_title)
   

    # File uploader
    uploaded_file = st.sidebar.file_uploader('Choose the file to upload', type='xlsx')
    if uploaded_file:
        # st.sidebar.markdown('----------------------------------')
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        number_of_rows = int(st.sidebar.number_input("Select number of rows:",min_value=1))
        for row in range(number_of_rows):
            select_row_item = st.sidebar.radio(f"What you want in row {row+1}",["Cards","Graphs"], horizontal=True)
            
            if select_row_item == 'Cards':
                cards = int(st.sidebar.number_input(f"How many KPI cards in row {row+1} ??",min_value=2))
                
                columns = st.columns(cards)

                # Dynamically create and customize each card
                for i, col in enumerate(columns):
                    with col:
                        try:
                            # st.write(f"Card {i+1}")
                            metrics_col = st.sidebar.multiselect(
                            'Select metrics for row '+str(row+1)+ ' column '+str(i+1),
                            df.columns.tolist(),
                            key='metrics_col'+str(row+1)+str(i+1))
                            total_col = df[metrics_col].sum().sum() / 1000000
                            col_name = ",".join(metrics_col)
                            total_col_accounting = float(total_col)
                            st.metric(f"{col_name}", f" ${total_col_accounting:.0f} M")
                        except Exception as err:
                            st.warning('Please select only numeric!!!')

            elif select_row_item == 'Graphs':

                # Number of graphs selection
                num_graphs = st.sidebar.number_input(f'How many graphs do you want in row {row+1}?', max_value=4, min_value=1)
                graph_columns = st.columns(num_graphs)
                graph_count = 0
                for i, col in enumerate(graph_columns):
                    with col:
                        fig =  None
                        output_columns = st.sidebar.multiselect(
                            f'What you would like to analyze in {row+1}{i + 1} ??',
                            df.columns.tolist(),
                            key=f"output_columns_{row+1}{i + 1}"
                        )
                        groupby_column = st.sidebar.selectbox(
                            f'Filter By?{row+1}{i + 1}',
                            df.columns.tolist(),
                            key=f"groupby_column_{row+1}{i + 1}"
                        )
                        chart_type = st.sidebar.selectbox(
                            f'Select Chart Type: {row+1}{i + 1}',
                            ['Pie Chart', 'Bar Chart', 'Donut Chart', 'Line Chart', 'Clustered Bar Chart', 'Stacked Bar Chart',
                            'Area Chart', 'Scatter Chart', 'Treemap'],
                            key=f"chart_type_{row+1}{i + 1}"
                        )

                        df_grouped = df.groupby(by=[groupby_column], as_index=False)[output_columns].sum()

                        if not output_columns:
                            st.warning("Please select at least one column for analysis.")
                            continue
                        output_column = None
                        if chart_type == 'Bar Chart' or chart_type == 'Pie Chart' or chart_type == 'Donut Chart' or chart_type == 'Line Chart' or chart_type == 'Area Chart' or chart_type == 'Scatter Chart' or chart_type == 'Treemap':
                            if len(output_columns) > 1:
                                st.warning(f"Select only one column for {chart_type}{row+1}{i+1}.")
                                continue
                            output_column = output_columns[0]  # Select the first column
                            if chart_type == 'Bar Chart':
                                fig = px.bar(
                                    df_grouped,
                                    x=groupby_column,
                                    y=output_column,
                                    title=f"{output_column} BY {groupby_column}"
                                )
                            elif chart_type == 'Pie Chart':
                                fig = px.pie(
                                    df_grouped,
                                    values=output_column,
                                    names=groupby_column,
                                    title=f"{output_column} BY {groupby_column}"
                                )
                            elif chart_type == 'Donut Chart':
                                fig = px.pie(
                                    df_grouped,
                                    values=output_columns[0],
                                    names=groupby_column,
                                    hole=0.5,
                                    title=f"{output_column} BY {groupby_column}"
                                )
                            elif chart_type == 'Line Chart':
                                fig = px.line(
                                    df_grouped,
                                    x=groupby_column,
                                    y=output_columns[0],
                                    title=f"{output_column} BY {groupby_column}"
                                )
                        
                        elif chart_type == 'Clustered Bar Chart' or chart_type == 'Stacked Bar Chart':
                            if len(output_columns) <= 1:
                                st.warning(f"Select more than one column for {chart_type}.")
                                continue
                            if chart_type == 'Clustered Bar Chart':
                                fig = px.bar(
                                    df_grouped,
                                    x=groupby_column,
                                    y=output_columns,
                                    title=f"{output_column} BY {groupby_column}",
                                    barmode='group'
                                )
                            elif chart_type == 'Stacked Bar Chart':
                                fig = px.bar(
                                    df_grouped,
                                    x=groupby_column,
                                    y=output_columns,
                                    title=f"{output_column} BY {groupby_column}",
                                    barmode='stack'
                                )
                        if fig:
                            fig.update_layout(width=500, height=400)
                            st.plotly_chart(fig)
                        else :
                            st.warning("Charts cannot be created")