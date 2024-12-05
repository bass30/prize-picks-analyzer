# Prize Picks Analyzer

A comprehensive sports betting analysis tool that helps make informed decisions for player prop bets on Prize Picks. This tool combines historical data analysis, opponent matchup statistics, and injury tracking to provide data-driven betting recommendations.

## Features

### 1. Player Statistics Analysis
- Historical performance tracking
- Moving averages (5 and 10 game periods)
- Trend analysis with confidence levels
- Form-adjusted predictions
- Statistical variance analysis
- Performance outlier detection

### 2. Opponent-Specific Analysis
- Head-to-head performance history
- Matchup-based line adjustments
- Opponent trend analysis (improving/declining/stable)
- Recent performance against specific teams
- Historical matchup statistics

### 3. Injury Impact Analysis
- Real-time injury status tracking
- Team injury impact assessment
- Historical performance post-injury
- Injury trend monitoring
- Return-to-play analysis

### 4. Line Prediction
- Statistically-derived betting lines
- Confidence interval calculations
- Form-adjusted suggestions
- Opponent-specific adjustments
- Trend-based modifications

### 5. Multi-Sport Support
- NBA player props
- NFL player props
- MLB player props
- Sport-specific statistical analysis
- Cross-sport trend analysis

## Usage Guide

### Basic Analysis

```python
from analyzer import PrizePicksAnalyzer

# Initialize analyzer
analyzer = PrizePicksAnalyzer()

# Add game data
analyzer.add_game_data(
    player_name="LeBron James",
    date="2023-12-01",
    stats={
        'points': 28,
        'rebounds': 8,
        'assists': 9,
        'opponent': 'Lakers'
    }
)

# Get basic line suggestion
suggestion = analyzer.suggest_line('LeBron James', 'points')
```

### Opponent-Specific Analysis

```python
# Get line suggestion with opponent context
matchup_suggestion = analyzer.suggest_line_with_matchup(
    player_name="LeBron James",
    metric="points",
    opponent="Lakers"
)

# Analyze trend with opponent history
trend = analyzer.analyze_trend(
    player_name="LeBron James",
    metric="points",
    line=25.5,
    opponent="Lakers"
)
```

### Injury Tracking

```python
from injury_tracker import InjuryTracker

# Initialize tracker
tracker = InjuryTracker()

# Get player injury status
status = tracker.get_player_status("LeBron James")

# Check team injury report
team_report = tracker.get_team_injuries("Lakers")
```

## Understanding the Output

### Line Suggestions
```python
{
    'suggested_line': 26.5,
    'range': (23.5, 29.5),
    'confidence': 0.80,
    'recent_form': 'HOT',
    'mean': 25.8,
    'last_5_avg': 27.2
}
```

### Opponent Analysis
```python
{
    'average': 28.5,
    'games_played': 10,
    'trend': 'IMPROVING',
    'last_performance': 32,
    'last_matchup': '2023-12-01'
}
```

### Trend Analysis
```python
{
    'metric': 'points',
    'line': 25.5,
    'last_5_avg': 27.2,
    'last_10_avg': 25.8,
    'trend': 'UP',
    'recommendation': 'OVER',
    'confidence': 'HIGH',
    'vs_opponent': {
        'average': 28.5,
        'trend': 'IMPROVING'
    }
}
```

## Best Practices

1. **Data Quality**
   - Always ensure you have sufficient historical data
   - Consider recent form more heavily than older games
   - Account for schedule strength and rest days

2. **Opponent Analysis**
   - Minimum of 3-5 games against an opponent for reliable analysis
   - Consider home/away splits in matchup analysis
   - Factor in defensive rankings and team pace

3. **Injury Impact**
   - Always check injury status before placing bets
   - Consider impact of teammate injuries
   - Monitor minutes restrictions and return-to-play protocols

4. **Line Movement**
   - Compare suggested lines with actual Prize Picks lines
   - Monitor line movement throughout the day
   - Consider key lineup changes and breaking news

## Configuration

The analyzer can be configured with different confidence intervals and analysis parameters:

```python
# Adjust confidence interval for line suggestions
suggestion = analyzer.suggest_line(
    player_name="LeBron James",
    metric="points",
    confidence_interval=0.85  # Default is 0.80
)

# Modify games back for averages
averages = analyzer.calculate_averages(
    player_name="LeBron James",
    metric="points",
    games_back=15  # Default is 10
)
```

## Limitations

- Relies on quality of input data
- Past performance doesn't guarantee future results
- Injury data may have slight delays
- Requires regular updates for optimal performance
- Limited by available historical matchup data

## Future Enhancements

1. Machine learning prediction models
2. Advanced statistical analysis
3. User accounts and bet tracking
4. Additional sports coverage
5. Real-time odds comparison
6. Performance visualization tools

## Support

For questions, feature requests, or bug reports, please open an issue in the repository.

## License

MIT License - See LICENSE file for details
