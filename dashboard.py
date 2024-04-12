import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Setup page configuration and title as the very first command
st.set_page_config(page_title="Big Tech Data Center Dashboard", layout="wide")

# Set a style for matplotlib to match dark mode
plt.style.use('dark_background')

# Load the dataset with caching
@st.cache_data
def load_data():
    data = pd.read_csv('combined_data.csv')
    data.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True)
    data['Opened'] = pd.to_datetime(data['Opened'], errors='coerce')
    data['Opened Year'] = data['Opened'].dt.year.fillna(0).astype(int)
    return data

data = load_data()

# Add a title
st.title("Big Tech Data Center Dashboard")

# Sidebar for filters
st.sidebar.header("Filter Data")

selected_companies = st.sidebar.multiselect('Select companies:', options=data['Company'].unique(), default=data['Company'].unique())
selected_continents = st.sidebar.multiselect('Select continents:', options=data['Continent'].unique())
selected_countries = st.sidebar.multiselect('Select countries:', options=data['Country'].unique())
min_year, max_year = data['Opened Year'].min(), data['Opened Year'].max()
selected_years = st.sidebar.slider('Select year range:', min_value=int(min_year), max_value=int(max_year), value=(int(min_year), int(max_year)))

# Sidebar link to the dataset
st.sidebar.markdown("[Download Full Dataset on Kaggle](https://www.kaggle.com/datasets/farnazamiri/datacentermap-toptechcompanies/data)")

filtered_data = data[data['Company'].isin(selected_companies)]
if selected_continents:
    filtered_data = filtered_data[filtered_data['Continent'].isin(selected_continents)]
if selected_countries:
    filtered_data = filtered_data[filtered_data['Country'].isin(selected_countries)]
if selected_years:
    filtered_data = filtered_data[(filtered_data['Opened Year'] >= selected_years[0]) & (filtered_data['Opened Year'] <= selected_years[1])]

# Filtering out invalid years (e.g., zero which we used for N/A)
valid_year_data = filtered_data[filtered_data['Opened Year'] > 0]

# Metrics layout using columns
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Locations", value=valid_year_data.shape[0])
with col2:
    st.metric(label="Countries Covered", value=valid_year_data['Country'].nunique())
with col3:
    st.metric(label="Companies Represented", value=valid_year_data['Company'].nunique())

# Displaying a map with the locations of the filtered data
st.map(valid_year_data[['lat', 'lon']])

# Bar chart for company distribution within selected countries
st.header("Company Presence by Country")
company_country_data = valid_year_data.groupby(['Country', 'Company']).size().unstack().fillna(0)
fig, ax = plt.subplots()
company_country_data.plot(kind='bar', stacked=True, ax=ax)
ax.set_xlabel("Country")
ax.set_ylabel("Number of Locations")
ax.set_facecolor('#303030')  # Setting background to dark grey
ax.legend(title="Company")
st.pyplot(fig)

# Pie chart for market share by company
st.header("Market Share by Company")
fig2, ax2 = plt.subplots()
company_counts = valid_year_data['Company'].value_counts()
ax2.pie(company_counts, labels=company_counts.index, autopct='%1.1f%%', startangle=90)
ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
st.pyplot(fig2)

# Histogram for yearly openings
st.header("Distribution of Openings by Year")
if selected_years:
    fig3, ax3 = plt.subplots()
    # Calculate bins and labels
    min_year = int(valid_year_data['Opened Year'].min())
    max_year = int(valid_year_data['Opened Year'].max())
    bins = range(min_year, max_year + 2)  # Ensure full coverage of the last year
    ax3.hist(valid_year_data['Opened Year'], bins=bins, color='cyan', edgecolor='black')
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Number of Openings")
    ax3.set_title("Yearly Distribution of Openings")

    # Set x-ticks to show labels every 5 years
    tick_labels = range(min_year, max_year + 1, 5)
    ax3.set_xticks(tick_labels)  # Apply the ticks to the x-axis

    st.pyplot(fig3)

# Displaying the filtered data table
st.dataframe(valid_year_data[['City', 'Country', 'Opened Year', 'Company', 'Location']].style.format({'Opened Year': lambda x: 'N/A' if x == 0 else x}))

# Streamlit theme adjustment with CSS for dark mode
st.markdown("""
<style>
    .css-1d391kg {
        background-color: #1e1e1e;  # Setting main background color
        color: #ffffff;  # Setting text color to white
    }
</style>
""", unsafe_allow_html=True)
