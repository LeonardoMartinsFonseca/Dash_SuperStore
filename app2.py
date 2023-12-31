import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="SuperStore!!!", page_icon=":bar_chart:", layout="wide")

st.title(" :bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader("Upload a file", type=(["csv","txt","xlsx","xls","xlsb"]))

if fl is not None:
    try:
        df = pd.read_excel(fl, engine="openpyxl")  # Usando 'engine="openpyxl"' para arquivos XLSX e XLS
    except Exception as e:
        st.warning(f"Failed to read the file: {e}")
        st.stop()
else:
    st.warning("Please upload a file to continue.")
    st.stop()

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])
    
# Getting the min  and max date
StartDate = pd.to_datetime(df["Order Date"]).min()
EndDate = pd.to_datetime(df["Order Date"]).max()
    
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", StartDate))
        
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", EndDate))
        
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)]. copy()
    
st.sidebar.header("Choose your Filter: ")
    
#Create for Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]
        
#Create for State
state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]
    
#Create for City
city = st.sidebar.multiselect("Pick the City", df3["City"].unique())
    
#Filter the data base on Region, State and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]                
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:  
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]
        
category_df = filtered_df.groupby(by= ["Category"], as_index= False)["Sales"].sum()
    
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text= ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)
    
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)
        
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df)
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                               help = 'Click here to Download the data as a CSV file')
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region)
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                               help = 'Click here to Download the data as a CSV file')  
      
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"}, height=500, width= 1000,template="gridon")          
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    linechart["month_year"] = linechart["month_year"].astype(str)

    # Converta o DataFrame para um formato HTML
    table_html = linechart.to_html(header=False, escape=False, index=False)

    # Adicione um estilo CSS para a tabela
    style = """
        <style>
        table {
            width: 100%;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
        </style>
    """
    
    # Adicione o estilo CSS
    st.write(style, unsafe_allow_html=True)
    
    # Renderize a tabela HTML usando st.write com um limite de altura para adicionar uma barra de rolagem
    st.write(table_html, unsafe_allow_html=True, height=500)  # Defina a altura desejada aqui

    # Adicione um botão de download como você fez antes, exportando os dados na orientação vertical
    csv_vertical = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv_vertical, file_name="TimeSeries.csv", mime='text/csv')
    
#Create a treem based on Region, category, sub-category
st.subheader("Hierarchical view of sales TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region", "Category", "Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)
    
import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig,use_container_width=True)
    
    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_Category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_Category_Year)
    
#Create a scatter plot
data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship betwenn Sales and Profits Using Scatter Plot.",
                    titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                    yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2])
    
#Download original Dataset
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")
