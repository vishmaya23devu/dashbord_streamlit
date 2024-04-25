import streamlit as st
import pandas as pd
import plotly.express as px
import pdfkit
from PIL import Image
import base64
from io import BytesIO
from plotly.offline import plot
import kaleido #required
import os
import plotly
import plotly.graph_objects as go
import numpy as np
import base64
import altair as alt




def generate_html(dashboard_title, number_of_rows, df):
    # Generate HTML content
    html_content =f"""
    
    <html>
    <head><title>{dashboard_title}</title></head>
    <body>
    <h1>{dashboard_title}</h1>
    """

    
    for row in range(number_of_rows):
        select_row_item = st.sidebar.radio(f"What you want in row {row+1}",["Cards","Graphs"], key=f"row_select_{row+1}")
        
        if select_row_item == 'Cards':
            cards = int(st.sidebar.number_input(f"How many KPI cards in row {row+1} ??",min_value=2, key=f"cards_{row+1}"))
            columns = st.columns(cards)

            for i, col in enumerate(columns):
                with col:
                    try:
                        metrics_col = st.sidebar.multiselect(
                            'Select metrics for row '+str(row+1)+ ' column '+str(i+1),
                            df.columns.tolist(),
                            key=f'metrics_col_{row+1}_{i+1}'
                        )
                        total_col = df[metrics_col].sum().sum() / 1000000
                        col_name = ",".join(metrics_col)
                        total_col_accounting = float(total_col)
                        st.metric(f"{col_name}", f" ${total_col_accounting:.0f} M")
                        html_content+=f"""
                                    <h1>{col_name}</h1>
                                    <h2>{total_col_accounting}</h2>
                                    """
                    except Exception as err:
                        st.warning('Please select only numeric!!!')

        elif select_row_item == 'Graphs':
            num_graphs = st.sidebar.number_input(f'How many graphs do you want in row {row+1}?', max_value=4, min_value=1, key=f"num_graphs_{row+1}")
            graph_columns = st.columns(num_graphs)

            for i, col in enumerate(graph_columns):
                with col:
                    fig =  None
                    output_columns = st.sidebar.multiselect(
                        f'What you would like to analyze in {row+1}{i + 1} ??',
                        df.columns.tolist(),
                        key=f"output_columns_{row+1}_{i + 1}"
                    )
                    groupby_column = st.sidebar.selectbox(
                        f'Filter By?{row+1}{i + 1}',
                        df.columns.tolist(),
                        key=f"groupby_column_{row+1}_{i + 1}"
                    )
                    chart_type = st.sidebar.selectbox(
                        f'Select Chart Type: {row+1}{i + 1}',
                        ['Pie Chart', 'Bar Chart', 'Donut Chart', 'Line Chart', 'Clustered Bar Chart', 'Stacked Bar Chart',
                        'Area Chart', 'Scatter Chart', 'Treemap'],
                        key=f"chart_type_{row+1}_{i + 1}"
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
                                color_discrete_sequence = ['blue'],
                                title=f"{output_column} BY {groupby_column}"
                            )
                        elif chart_type == 'Pie Chart':
                            fig = px.pie(
                                df_grouped,
                                values=output_column,
                                names=groupby_column,
                                color_discrete_sequence= px.colors.sequential.RdBu,
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
                        plot_div = plot(fig,output_type = 'div',include_plotlyjs=False)
                        rend_out_loc = os.path.join(os.getcwd(),"fig1.png")
                        rend_out_loc_ht = os.path.join(os.getcwd(),"fig1.html")

                        fig.write_html(rend_out_loc_ht)
                        fig.write_image(rend_out_loc)
                        with open(rend_out_loc,"rb") as imgFile :
                            encoded_str = base64.b64encode(imgFile.read())
                            imgafe_div = """
                            <div class="mail_logo mb-2">
                                <img src="data:image/png;base64,%s" alt="">
                            </div>
                            """ % encoded_str.decode("utf-8")
                        html_content+= imgafe_div
                       
                    else :
                        st.warning("Charts cannot be created")
    html_content += """ 
    </body>
    </html>
    """
    return html_content

def convert_to_pdf(html_content):
    options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None
    }
    config_path =pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    pdfkit.from_string(html_content, 'outputs.pdf', options=options, configuration= config_path)
def dash():
    dashboard_title = st.sidebar.text_input("Enter the title of the dashboard:")
    st.title(dashboard_title)
    uploaded_file = st.sidebar.file_uploader('Choose the file to upload', type='xlsx')
    if uploaded_file:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        number_of_rows = int(st.sidebar.number_input("Select number of rows:",min_value=1))
        html_content = generate_html(dashboard_title, number_of_rows, df)
        with open ('outputfile.html','w+') as filename:
            filename.write(html_content)
        if st.sidebar.button("Download as PDF"):
            convert_to_pdf(html_content)
            st.success("PDF generated successfully! You can download it below.")
            st.markdown("[Download PDF](./outputs.pdf)", unsafe_allow_html=True)

dash()