import streamlit as st
from data_scraper import SportsScraper
from analyzer import PrizePicksAnalyzer

# Initialize scraper and analyzer
scraper = SportsScraper()
analyzer = PrizePicksAnalyzer()

# Simple title
st.title("Test App")

# Player input
player_name = st.text_input("Enter NBA Player Name")

if st.button("Test"):
    if not player_name:
        st.error("Please enter a player name")
    else:
        st.write("Starting test...")
        data = scraper.get_nba_stats(player_name)
        st.write(f"Data shape: {data.shape if data is not None else 'No data'}")
        
        if data is not None and len(data) > 0:
            st.write("Sample of retrieved data:")
            st.write(data.head())
        else:
            st.error("No data found for player")
