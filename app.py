import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.express as px
import psycopg2
import pandas as pd
from PIL import Image
import openai
from loguru import logger

openai.api_key = 'f77b178d2e77459d8d47e92d85865d7a'
openai.api_base = 'https://otaimage.openai.azure.com/'
openai.api_type = 'azure'
openai.api_version = '2024-02-01' # this may change in the future

# connecting to database
def connect_to_db():
    conn = psycopg2.connect(
        host='10.62.48.125',
        dbname='bdc_extranet_data',
        user='readonly_user',
        password='readonlypassword',
        port=5432
    )
    return conn
def load_data():
    conn = connect_to_db()
    bdc_churned_properties = '''Select * from intl_churned_prop where country_name in ('United States', 'Canada')'''
    data_churned_prop = pd.read_sql_query(bdc_churned_properties, conn)
    return data_churned_prop
    
def revenue_trend_display(df):
    # Attempt to convert 'year_month' to datetime, handling errors
    df['year_month'] = pd.to_datetime(df['year_month'], errors='coerce', format='%Y-%m')

    # Check if any values couldn't be converted
    if df['year_month'].isnull().any():
        st.write("Some dates couldn't be converted. Please check the 'year_month' column for non-standard date formats or other issues.")
    else:
        # Group by year_month and hotel_id, then calculate the total revenue
        monthly_revenue = df.groupby(['year_month', 'hotel_id'])['total_gmv'].sum().reset_index()

        st.write('### Monthly Revenue Trend')

        # Plot the line graph
        plt.figure(figsize=(10, 6))
        fig = px.line(monthly_revenue, x='year_month', y='total_gmv', color='hotel_id', markers=True)
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='GMV',
            xaxis_tickformat='%Y-%m',
            template='plotly_white'
        )
        live_date = pd.to_datetime(df['Live_date'].iloc[0])
        churned_date = pd.to_datetime(df['Churned_date'].iloc[0])

        fig.add_vline(x=datetime.timestamp(live_date)*1000, line_width=2, line_dash="dash", line_color="green", annotation_text="Live Date")
        fig.add_vline(x=datetime.timestamp(churned_date)*1000, line_width=2, line_dash="dash", line_color="red", annotation_text="Churned Date")
        
        # Display plot
        st.plotly_chart(fig)


def adr_trend_display(df):
   # Attempt to convert 'year_month' to datetime, handling errors
    df['year_month'] = pd.to_datetime(df['year_month'], errors='coerce', format='%Y-%m')

    # Check if any values couldn't be converted
    if df['year_month'].isnull().any():
        st.write("Some dates couldn't be converted. Please check the 'year_month' column for non-standard date formats or other issues.")
    else:
        # Group by year_month and hotel_id, then calculate the total revenue
        monthly_revenue = df.groupby(['year_month', 'hotel_id'])['average_daily_rate'].sum().reset_index()

        st.write('### Monthly ADR Trend')

        # Plot the line graph
        plt.figure(figsize=(10, 6))
        fig = px.line(monthly_revenue, x='year_month', y='average_daily_rate', color='hotel_id', markers=True)
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='ADR',
            xaxis_tickformat='%Y-%m',
            template='plotly_white'
        )
        live_date = pd.to_datetime(df['Live_date'].iloc[0])
        churned_date = pd.to_datetime(df['Churned_date'].iloc[0])

        fig.add_vline(x=datetime.timestamp(live_date)*1000, line_width=2, line_dash="dash", line_color="green", annotation_text="Live Date")
        fig.add_vline(x=datetime.timestamp(churned_date)*1000, line_width=2, line_dash="dash", line_color="red", annotation_text="Churned Date")
        
        # Display plot
        st.plotly_chart(fig)
        
def room_nights_trend_display(df):
    # Attempt to convert 'year_month' to datetime, handling errors
    df['year_month'] = pd.to_datetime(df['year_month'], errors='coerce', format='%Y-%m')

    # Check if any values couldn't be converted
    if df['year_month'].isnull().any():
        st.write("Some dates couldn't be converted. Please check the 'year_month' column for non-standard date formats or other issues.")
    else:
        # Group by year_month and hotel_id, then calculate the total revenue
        monthly_revenue = df.groupby(['year_month', 'hotel_id'])['room_nights'].sum().reset_index()
        st.write('### Monthly Room nights Trend')

        # Plot the line graph
        plt.figure(figsize=(10, 6))
        fig = px.line(monthly_revenue, x='year_month', y='room_nights', color='hotel_id', markers=True)
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Room nights',
            xaxis_tickformat='%Y-%m',
            template='plotly_white'
        )
        live_date = pd.to_datetime(df['Live_date'].iloc[0])
        churned_date = pd.to_datetime(df['Churned_date'].iloc[0])

        fig.add_vline(x=datetime.timestamp(live_date)*1000, line_width=2, line_dash="dash", line_color="green", annotation_text="Live Date")
        fig.add_vline(x=datetime.timestamp(churned_date)*1000, line_width=2, line_dash="dash", line_color="red", annotation_text="Churned Date")
        
        # Display plot
        st.plotly_chart(fig)
    
def summary_table(master_df):
    # Get the unique oyo_ids
    unique_oyo_ids = master_df['oyo_id'].unique()
    consolidated_data = []
    for oyo_id in unique_oyo_ids:
        df = master_df[master_df['oyo_id'] == oyo_id]
        # Separate the data into different periods
        pre_oyo = df[df['Live_date'] > df['revenue_date']].fillna(0)
        with_oyo = df[(df['Live_date'] < df['revenue_date']) & (df['Churned_date'] > df['revenue_date'])].fillna(0)
        post_oyo = df[df['Churned_date'] < df['revenue_date']].fillna(0)

        # Calculate averages for each period
        averages = {
            'Pre OYO': [pre_oyo['total_gmv'].mean(), pre_oyo['average_daily_rate'].mean(), pre_oyo['room_nights'].mean()],
            'With OYO': [with_oyo['total_gmv'].mean(), with_oyo['average_daily_rate'].mean(), with_oyo['room_nights'].mean()],
            'Post OYO': [post_oyo['total_gmv'].mean(), post_oyo['average_daily_rate'].mean(), post_oyo['room_nights'].mean()]
        }

        rounded_averages = {key: [round(value) if not pd.isna(value) else 0 for value in averages[key]] for key in averages}
        # Round the averages and convert NaN values to 0
        if len(unique_oyo_ids) == 1:
            return rounded_averages
        else:
            # Append the consolidated row to the list
            consolidated_data.append({
                'oyo_id': oyo_id,
                'pre_oyo_avg_adr': rounded_averages['Pre OYO'][0],
                'pre_oyo_avg_night': rounded_averages['Pre OYO'][1],
                'pre_oyo_avg_gvm': rounded_averages['Pre OYO'][2],
                'with_oyo_avg_adr': rounded_averages['With OYO'][0],
                'with_oyo_avg_night': rounded_averages['With OYO'][1],
                'with_oyo_avg_gvm': rounded_averages['With OYO'][2],
                'post_oyo_avg_adr': rounded_averages['Post OYO'][0],
                'post_oyo_avg_night': rounded_averages['Post OYO'][1],
                'post_oyo_avg_gvm': rounded_averages['Post OYO'][2]
            })

    # Create a new DataFrame from the consolidated data
    consolidated_df = pd.DataFrame(consolidated_data)
    return consolidated_df

def get_Chatcompletion(prompt):
    try:
        deployment_name='oyopinion'
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create( 
            engine=deployment_name,
            messages=messages,
            temperature=0, # most probable output (least random)
        )
        return response.choices[0].message["content"]
    except Exception as e:
        logger.error(f'An error occurred: {str(e)}')


def main():
    
    df = load_data()
    df['year_month'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str))
    df['revenue_date'] = pd.to_datetime(df['year_month'], errors='coerce', format='%Y-%m')
    df = df.fillna(0)
    ids = df['oyo_id'].unique()
    # Selectbox for selecting OYO ID
    selected_oyo_id = 0
    selected_oyo_id = st.sidebar.selectbox('Select Churned OYO ID', ids)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("# About")
    st.sidebar.markdown(
            "Churn Analyzer is designed to provide in-depth insights into churned hotel’s performance. You can select a churned hotel from the dropdown menu and explore its performance metrics, including Gross Merchandise Value (GMV), Average Daily Rate (ADR), and Room Nights, all under the Performance tab.\n"
            "Next, navigate to the Summary tab, where our advanced AI model generates a comprehensive summary based on the hotel’s performance data. "
        )
    
    home_button = st.button('Reset')
    # Home button
    if home_button:
        consolidated_df = summary_table(df)
        #Homapage        
        st.dataframe(consolidated_df)
            
    else:
        # Filter the DataFrame based on the selected OYO ID
        selected_data = df[df['oyo_id'] == selected_oyo_id]
        dic = {
            'OYO Id': [df['oyo_id'].iloc[0]],
            'Hotel Name': [df['hotel_name'].iloc[0]],
            'Country Name': [df['country_name'].iloc[0]]
        }
        st.dataframe(pd.DataFrame(dic))
          
        #Create tabs
        tab_titles = ['Performance','Summary']
        performance, summary= st.tabs(tab_titles)
        
        with performance:
            st.markdown("<br>", unsafe_allow_html=True)
            revenue_trend_display(selected_data)
            st.markdown("<br>", unsafe_allow_html=True)
            adr_trend_display(selected_data)
            st.markdown("<br>", unsafe_allow_html=True)
            room_nights_trend_display(selected_data)
            st.markdown("<br>", unsafe_allow_html=True)
            # Create a summary DataFrame
            rounded_averages = summary_table(selected_data)
            summary_df = pd.DataFrame(rounded_averages, index=['Total GMV', 'ADR', 'Room Nights'])

            # Streamlit app to display the summary DataFrame
            st.write('### Churned property performance Summary Table')
            st.dataframe(summary_df)
        
        with summary: 
            prompt_text = """Analyse the hotel performance in terms of GMV, ADR and Room Nights from {} in three broad categories pre OYO, with OYO and post OYO. 
                            pre OYO is the time period before Live_date, with OYO is the time period after Live_date and before Churned_date and post OYO is the time period after Churned_date.
                            Provide a elegant and crisp conclusion Whether or not the hotel can be taken back by OYO. If Post OYO revenue is good there is no possibility. 
                            Output should not be more than hundred words.
                          """
            table_str = selected_data.to_string(index=False)
            response = get_Chatcompletion(prompt_text.format(table_str))
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.write(response)
            
            
if __name__ == "__main__":
    st.write("# Churn Analyzer")
    st.write('#### Property performance before OYO, with OYO and After OYO')
    image = Image.open('/app/oyo.png')
    resized_image = image.resize((200, 200))
    st.sidebar.image(resized_image, use_column_width=True)
    main()