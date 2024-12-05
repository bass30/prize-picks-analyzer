import streamlit as st
import pandas as pd
from analyzer import PrizePicksAnalyzer
from injury_tracker import InjuryTracker
from data_scraper import SportsScraper
import plotly.graph_objects as go

# Initialize our classes
scraper = SportsScraper()
analyzer = PrizePicksAnalyzer()
injury_tracker = InjuryTracker()

# Set page config
st.set_page_config(
    page_title="Prize Picks Analyzer",
    layout="wide",
    page_icon="🎯"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .documentation-section {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        background-color: #ffffff;
    }
    .feature-box {
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #ff4b4b;
        background-color: #f8f9fa;
    }
    code {
        padding: 0.2rem 0.4rem;
        background-color: #f8f9fa;
        border-radius: 0.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Analysis", "Injury Tracker", "Documentation"]
)

def create_trend_chart(data, metric):
    """Create an interactive trend chart"""
    fig = go.Figure()
    
    # Add the metric line
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data[metric],
        mode='lines+markers',
        name=metric.title(),
        line=dict(color='#FF4B4B')
    ))
    
    # Calculate moving averages
    ma5 = data[metric].rolling(window=5).mean()
    ma10 = data[metric].rolling(window=10).mean()
    
    # Add moving averages
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=ma5,
        mode='lines',
        name='5-Game MA',
        line=dict(dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=ma10,
        mode='lines',
        name='10-Game MA',
        line=dict(dash='dot')
    ))
    
    # Update layout
    fig.update_layout(
        title=f'{metric.title()} Trend Analysis',
        xaxis_title='Games',
        yaxis_title=metric.title(),
        hovermode='x unified'
    )
    
    return fig

def display_injury_status(player_name, sport):
    """Display injury status for a player"""
    status = injury_tracker.get_player_status(player_name)
    
    if status:
        if "OUT" in status.upper():
            st.error(f"⛔️ {player_name} is OUT!")
        elif "QUESTIONABLE" in status.upper():
            st.warning(f"⚠️ {player_name} is QUESTIONABLE")
        elif "PROBABLE" in status.upper():
            st.info(f"ℹ️ {player_name} is PROBABLE")
        else:
            st.success(f"✅ {player_name} is ACTIVE")
        return True
    return False

def display_suggested_line(suggestion):
    """Display suggested line information"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Suggested Line", f"{suggestion['suggested_line']:.1f}")
        
    with col2:
        st.metric("Recent Form", suggestion['recent_form'])
        
    with col3:
        st.metric("Confidence", f"{suggestion['confidence']*100:.0f}%")
        
    st.write(f"Range: {suggestion['range'][0]:.1f} - {suggestion['range'][1]:.1f}")

if page == "Home":
    st.title("🎯 Prize Picks Analyzer")
    st.markdown("---")
    
    # Sidebar inputs
    st.sidebar.header("Analysis Parameters")
    
    sport = st.sidebar.selectbox(
        "Select Sport",
        ["NBA", "NFL", "MLB"]
    )
    
    player_name = st.sidebar.text_input(
        "Player Name",
        help="Enter the full name of the player"
    )
    
    metric = st.sidebar.selectbox(
        "Select Metric",
        {
            "NBA": ["points", "rebounds", "assists", "threes"],
            "NFL": ["passing_yards", "rushing_yards", "receptions"],
            "MLB": ["strikeouts", "hits", "runs"]
        }.get(sport, [])
    )
    
    line = st.sidebar.number_input(
        "Prize Picks Line",
        min_value=0.0,
        help="Enter the over/under line from Prize Picks"
    )
    
    # Analysis button
    if st.sidebar.button("Analyze", type="primary"):
        if not player_name:
            st.error("Please enter a player name!")
            st.stop()  # Use st.stop() instead of return
            
        with st.spinner(f"Fetching data for {player_name}..."):
            # Check for injuries first
            is_injured = display_injury_status(player_name, sport)
            
            # Get player data
            if sport == "NBA":
                data = scraper.get_nba_stats(player_name)
            elif sport == "NFL":
                data = scraper.get_nfl_stats(player_name)
            else:
                data = scraper.get_mlb_stats(player_name)
            
            if data is None or len(data) == 0:
                st.error("No data found for this player!")
                st.stop()
            
            # Get analysis
            suggestion = analyzer.suggest_line(player_name, metric)
            trend = analyzer.analyze_trend(player_name, metric, line)
            
            # Display results
            st.header("Analysis Results")
            
            # Display suggested line
            display_suggested_line(suggestion)
            
            # Display trend analysis
            st.subheader("Trend Analysis")
            fig = create_trend_chart(data, metric)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display recommendation
            st.subheader("Recommendation")
            if trend['recommendation'] == "OVER":
                st.success(f"🔥 OVER {line} ({trend['confidence']} Confidence)")
            elif trend['recommendation'] == "UNDER":
                st.success(f"❄️ UNDER {line} ({trend['confidence']} Confidence)")
            else:
                st.warning("⚠️ AVOID - Not enough confidence in either direction")
            
            # Warning for injured players
            if is_injured:
                st.warning("⚠️ Consider the injury status before placing any bets!")

elif page == "Analysis":
    st.title("Player Analysis")
    
    # Sport selection
    sport = st.selectbox("Select Sport", ["NBA", "NFL", "MLB"])
    
    # Player selection
    player = st.text_input("Enter Player Name")
    
    # Metric selection
    metrics = {
        "NBA": ["points", "rebounds", "assists", "threes"],
        "NFL": ["passing_yards", "rushing_yards", "receptions"],
        "MLB": ["strikeouts", "hits", "runs"]
    }
    
    metric = st.selectbox("Select Metric", metrics.get(sport, []))
    
    # Opponent selection
    opponent = st.text_input("Enter Opponent (optional)")
    
    if st.button("Analyze"):
        if player and metric:
            # Get analysis
            suggestion = analyzer.suggest_line_with_matchup(player, metric, opponent) if opponent else analyzer.suggest_line(player, metric)
            trend = analyzer.analyze_trend(player, metric, suggestion['suggested_line'], opponent)
            
            # Display results in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Line Suggestion")
                st.metric("Suggested Line", suggestion['suggested_line'])
                st.write(f"Range: {suggestion['range']}")
                st.write(f"Confidence: {suggestion['confidence']}")
                st.write(f"Recent Form: {suggestion['recent_form']}")
            
            with col2:
                st.subheader("Trend Analysis")
                st.write(f"Trend: {trend['trend']}")
                st.write(f"Recommendation: {trend['recommendation']}")
                st.write(f"Confidence: {trend['confidence']}")
                
                if opponent and 'vs_opponent' in trend:
                    st.subheader("Opponent Analysis")
                    st.write(f"Average vs {opponent}: {trend['vs_opponent']['average']}")
                    st.write(f"Trend vs {opponent}: {trend['vs_opponent']['trend']}")

elif page == "Injury Tracker":
    st.title("Injury Tracker")
    
    # Team selection
    team = st.selectbox("Select Team", ["Lakers", "Celtics", "Warriors"])  # Add more teams
    
    if st.button("Get Injury Report"):
        injuries = injury_tracker.get_team_injuries(team)
        if injuries:
            st.table(injuries)
        else:
            st.info("No injuries reported for selected team.")
    
    # Player injury search
    player = st.text_input("Search Player Injury Status")
    if player:
        status = injury_tracker.get_player_status(player)
        st.write(f"Status: {status}")

elif page == "Documentation":
    st.title("📚 Prize Picks Analyzer Documentation")
    
    # Create tabs for different documentation sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Features & Overview",
        "Usage Guide",
        "Best Practices",
        "Configuration"
    ])
    
    with tab1:
        st.header("Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Player Statistics Analysis")
            st.markdown("""
            - Historical performance tracking
            - Moving averages (5 and 10 game periods)
            - Trend analysis with confidence levels
            - Form-adjusted predictions
            - Statistical variance analysis
            """)
            
            st.subheader("Opponent-Specific Analysis")
            st.markdown("""
            - Head-to-head performance history
            - Matchup-based line adjustments
            - Opponent trend analysis
            - Recent performance tracking
            - Historical matchup statistics
            """)
        
        with col2:
            st.subheader("Injury Impact Analysis")
            st.markdown("""
            - Real-time injury status tracking
            - Team injury impact assessment
            - Historical performance post-injury
            - Injury trend monitoring
            - Return-to-play analysis
            """)
            
            st.subheader("Multi-Sport Support")
            st.markdown("""
            - NBA player props
            - NFL player props
            - MLB player props
            - Sport-specific analysis
            - Cross-sport trend analysis
            """)
    
    with tab2:
        st.header("Usage Guide")
        
        st.subheader("Basic Analysis")
        with st.expander("How to Get Basic Line Suggestions"):
            st.markdown("""
            1. Select 'Analysis' from the navigation menu
            2. Choose your sport (NBA/NFL/MLB)
            3. Enter player name
            4. Select the metric (points/assists/etc.)
            5. Click 'Analyze' to get predictions
            """)
            st.code("""
# Example Output:
{
    'suggested_line': 26.5,
    'range': (23.5, 29.5),
    'confidence': 0.80,
    'recent_form': 'HOT'
}
            """)
        
        st.subheader("Opponent Analysis")
        with st.expander("How to Use Opponent-Specific Analysis"):
            st.markdown("""
            1. Follow basic analysis steps
            2. Enter opponent team name
            3. Get matchup-adjusted predictions
            4. Review head-to-head statistics
            """)
            st.code("""
# Example Matchup Analysis:
{
    'average_vs_opponent': 28.5,
    'trend': 'IMPROVING',
    'last_matchup': '2023-12-01',
    'confidence': 'HIGH'
}
            """)
        
        st.subheader("Injury Tracking")
        with st.expander("How to Check Injury Status"):
            st.markdown("""
            1. Select 'Injury Tracker' from navigation
            2. Enter player name or select team
            3. View current injury status
            4. Check historical injury data
            """)
    
    with tab3:
        st.header("Best Practices")
        
        st.info("Follow these guidelines for optimal results")
        
        with st.expander("Data Quality Guidelines"):
            st.markdown("""
            - Ensure minimum 5-game sample size
            - Consider recent form (last 5 games)
            - Account for schedule strength
            - Check for back-to-back games
            """)
        
        with st.expander("Opponent Analysis Tips"):
            st.markdown("""
            - Minimum 3 previous matchups
            - Consider home/away splits
            - Check team defensive rankings
            - Factor in pace of play
            """)
        
        with st.expander("Injury Considerations"):
            st.markdown("""
            - Always check injury status
            - Consider teammate injuries
            - Monitor minutes restrictions
            - Review return-to-play history
            """)
        
        with st.expander("Line Movement"):
            st.markdown("""
            - Compare to actual Prize Picks lines
            - Monitor throughout the day
            - Consider breaking news
            - Check team announcements
            """)
    
    with tab4:
        st.header("Configuration Options")
        
        st.subheader("Analysis Parameters")
        st.markdown("""
        Customize your analysis with these parameters:
        
        1. **Confidence Interval** (default: 0.80)
        - Adjusts prediction range
        - Higher = wider range, more conservative
        - Lower = narrower range, more aggressive
        
        2. **Games Back** (default: 10)
        - Number of recent games to analyze
        - Minimum: 5 games
        - Maximum: 20 games
        
        3. **Form Weight** (default: 0.3)
        - Impact of recent performance
        - Higher = more emphasis on recent games
        - Lower = more emphasis on overall average
        """)
        
        st.subheader("Limitations")
        st.markdown("""
        - Requires quality input data
        - Past performance ≠ future results
        - Injury data may have delays
        - Limited by historical data
        """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ by Cascade")
