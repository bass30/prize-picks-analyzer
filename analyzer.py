import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from collections import defaultdict

class PrizePicksAnalyzer:
    def __init__(self):
        self.player_stats = {}
        self.trends = {}
        self.opponent_stats = defaultdict(lambda: defaultdict(list))
    
    def add_game_data(self, player_name, date, stats):
        """
        Add game statistics for a player
        stats should be a dictionary containing relevant metrics (points, rebounds, etc.)
        """
        if player_name not in self.player_stats:
            self.player_stats[player_name] = []
            
        game_data = {
            'date': date,
            **stats
        }
        self.player_stats[player_name].append(game_data)
        
        # Add to opponent stats if opponent is available
        if 'opponent' in stats:
            opponent = stats['opponent']
            self.opponent_stats[player_name][opponent].append(game_data)

    def get_opponent_stats(self, player_name, opponent, metric):
        """
        Get player's historical performance against specific opponent
        """
        if player_name not in self.opponent_stats or opponent not in self.opponent_stats[player_name]:
            return None
            
        games = self.opponent_stats[player_name][opponent]
        if not games or metric not in games[0]:
            return None
            
        # Sort games by date
        sorted_games = sorted(games, key=lambda x: x['date'], reverse=True)
        
        # Calculate statistics
        values = [game[metric] for game in sorted_games]
        
        return {
            'games_played': len(values),
            'average': np.mean(values),
            'max': max(values),
            'min': min(values),
            'std_dev': np.std(values) if len(values) > 1 else 0,
            'last_matchup': sorted_games[0]['date'],
            'last_performance': sorted_games[0][metric],
            'trend': self._calculate_opponent_trend(values),
            'recent_games': sorted_games[:5]  # Last 5 games against this opponent
        }
    
    def _calculate_opponent_trend(self, values):
        """Calculate trend against an opponent"""
        if len(values) < 2:
            return 'INSUFFICIENT_DATA'
            
        # Compare most recent performance to average of previous performances
        recent = values[0]
        historical_avg = np.mean(values[1:])
        
        if recent > historical_avg * 1.1:
            return 'IMPROVING'
        elif recent < historical_avg * 0.9:
            return 'DECLINING'
        else:
            return 'STABLE'

    def suggest_line_with_matchup(self, player_name, metric, opponent=None, confidence_interval=0.80):
        """
        Suggest a line based on historical performance, including opponent-specific adjustment
        """
        # Get general line suggestion
        base_suggestion = self.suggest_line(player_name, metric, confidence_interval)
        if not base_suggestion:
            return None
            
        # If no opponent specified, return base suggestion
        if not opponent:
            return base_suggestion
            
        # Get opponent-specific stats
        opponent_stats = self.get_opponent_stats(player_name, opponent, metric)
        if not opponent_stats or opponent_stats['games_played'] < 2:
            return base_suggestion
            
        # Calculate opponent adjustment
        opponent_avg = opponent_stats['average']
        general_avg = base_suggestion['mean']
        
        # Calculate adjustment factor based on historical performance vs this opponent
        adjustment_factor = (opponent_avg - general_avg) * 0.3  # 30% weight to opponent history
        
        # Adjust the suggested line
        adjusted_suggestion = base_suggestion.copy()
        adjusted_suggestion['suggested_line'] = round(base_suggestion['suggested_line'] + adjustment_factor, 1)
        adjusted_suggestion['opponent_factor'] = round(adjustment_factor, 1)
        adjusted_suggestion['vs_opponent'] = {
            'average': round(opponent_avg, 1),
            'games_played': opponent_stats['games_played'],
            'last_matchup': opponent_stats['last_matchup'],
            'last_performance': opponent_stats['last_performance'],
            'trend': opponent_stats['trend']
        }
        
        return adjusted_suggestion

    def calculate_averages(self, player_name, metric, games_back=10):
        """Calculate recent averages for a specific metric"""
        if player_name not in self.player_stats:
            return None
            
        stats = self.player_stats[player_name]
        if not stats:
            return None
            
        # Sort by date and get recent games
        sorted_stats = sorted(stats, key=lambda x: x['date'], reverse=True)
        recent_stats = sorted_stats[:games_back]
        
        if metric not in recent_stats[0]:
            return None
            
        # Calculate averages
        values = [game[metric] for game in recent_stats]
        return {
            'last_5': np.mean(values[:5]) if len(values) >= 5 else None,
            'last_10': np.mean(values) if len(values) >= 10 else None,
            'max': max(values),
            'min': min(values),
            'std_dev': np.std(values)
        }

    def suggest_line(self, player_name, metric, confidence_interval=0.80):
        """Suggest a line based on historical performance"""
        print(f"\nAnalyzing data for {player_name}...")
        print(f"Players in database: {list(self.player_stats.keys())}")
        
        if player_name not in self.player_stats:
            print(f"No data found for {player_name}")
            return None
            
        stats = self.player_stats[player_name]
        print(f"Found {len(stats)} games for {player_name}")
        
        # Check if metric exists in data
        if not stats or metric not in stats[0]:
            print(f"Metric {metric} not found in player data")
            print(f"Available metrics: {list(stats[0].keys()) if stats else 'No stats available'}")
            return None
            
        # Get recent games data
        sorted_stats = sorted(stats, key=lambda x: x['date'], reverse=True)
        recent_values = [game[metric] for game in sorted_stats[:20]]  # Use last 20 games
        print(f"Recent {metric} values: {recent_values}")
        
        if len(recent_values) < 5:
            print(f"Not enough recent games (need 5, got {len(recent_values)})")
            return None
            
        # Calculate basic statistics
        mean = np.mean(recent_values)
        std = np.std(recent_values)
        
        # Calculate confidence interval
        ci = stats.t.interval(confidence_interval, len(recent_values)-1, mean, std)
        
        # Calculate suggested line and range
        suggested_line = mean
        lower_bound = ci[0]
        upper_bound = ci[1]
        
        # Calculate recent form adjustment
        last_5_avg = np.mean(recent_values[:5])
        form_adjustment = (last_5_avg - mean) * 0.2  # 20% weight to recent form
        
        # Adjust suggested line based on recent form
        adjusted_line = suggested_line + form_adjustment
        
        return {
            'suggested_line': round(adjusted_line, 1),
            'range': (round(lower_bound, 1), round(upper_bound, 1)),
            'confidence': confidence_interval,
            'recent_form': 'HOT' if form_adjustment > std/2 else 'COLD' if form_adjustment < -std/2 else 'STABLE',
            'mean': round(mean, 1),
            'last_5_avg': round(last_5_avg, 1)
        }
    
    def analyze_trend(self, player_name, metric, line, opponent=None):
        """Analyze trend and make over/under recommendation"""
        stats = self.calculate_averages(player_name, metric)
        if not stats:
            return "Insufficient data"
        
        # Analysis logic
        last_5_avg = stats['last_5']
        last_10_avg = stats['last_10']
        
        if not last_5_avg or not last_10_avg:
            return "Insufficient data for trend analysis"
        
        # Calculate trend strength
        trend_strength = (last_5_avg - last_10_avg) / stats['std_dev'] if stats['std_dev'] != 0 else 0
        
        # Compare with the line
        avg_vs_line = (last_5_avg - line) / line
        
        # Get opponent-specific performance if available
        opponent_performance = None
        if opponent:
            opponent_stats = self.get_opponent_stats(player_name, opponent, metric)
            if opponent_stats:
                opponent_performance = {
                    'average': round(opponent_stats['average'], 2),
                    'games_played': opponent_stats['games_played'],
                    'trend': opponent_stats['trend'],
                    'last_performance': opponent_stats['last_performance']
                }
        
        recommendation = {
            'metric': metric,
            'line': line,
            'last_5_avg': round(last_5_avg, 2),
            'last_10_avg': round(last_10_avg, 2),
            'trend': 'UP' if trend_strength > 0.2 else 'DOWN' if trend_strength < -0.2 else 'STABLE',
            'recommendation': None,
            'confidence': None,
            'vs_opponent': opponent_performance
        }
        
        # Adjust confidence based on opponent history if available
        confidence_modifier = 0
        if opponent_performance:
            if opponent_performance['trend'] == 'IMPROVING':
                confidence_modifier = 0.1
            elif opponent_performance['trend'] == 'DECLINING':
                confidence_modifier = -0.1
        
        # Make recommendation
        if abs(avg_vs_line) > 0.1:  # 10% difference threshold
            if avg_vs_line > 0:
                recommendation['recommendation'] = 'OVER'
                base_confidence = 'HIGH' if trend_strength > 0 else 'MEDIUM'
            else:
                recommendation['recommendation'] = 'UNDER'
                base_confidence = 'HIGH' if trend_strength < 0 else 'MEDIUM'
            
            # Adjust confidence based on opponent history
            if confidence_modifier > 0 and base_confidence == 'MEDIUM':
                recommendation['confidence'] = 'HIGH'
            elif confidence_modifier < 0 and base_confidence == 'HIGH':
                recommendation['confidence'] = 'MEDIUM'
            else:
                recommendation['confidence'] = base_confidence
        else:
            recommendation['recommendation'] = 'AVOID'
            recommendation['confidence'] = 'LOW'
        
        return recommendation

def main():
    # Example usage
    analyzer = PrizePicksAnalyzer()
    
    # Example: Adding some sample data for LeBron James
    sample_data = [
        {'date': '2023-12-01', 'points': 28, 'rebounds': 8, 'assists': 9, 'opponent': 'Lakers'},
        {'date': '2023-12-03', 'points': 32, 'rebounds': 7, 'assists': 11, 'opponent': 'Celtics'},
        {'date': '2023-12-05', 'points': 25, 'rebounds': 10, 'assists': 8, 'opponent': 'Bulls'},
        # Add more games as needed
    ]
    
    for game in sample_data:
        analyzer.add_game_data('LeBron James', game['date'], game)
    
    # Get analysis for points (example line: 27.5)
    analysis = analyzer.analyze_trend('LeBron James', 'points', 27.5)
    print(f"\nAnalysis for LeBron James (Points):")
    print(f"Last 5 games average: {analysis['last_5_avg']}")
    print(f"Last 10 games average: {analysis['last_10_avg']}")
    print(f"Trend: {analysis['trend']}")
    print(f"Recommendation: {analysis['recommendation']} (Confidence: {analysis['confidence']})")

    # Get suggested line for points
    suggested_line = analyzer.suggest_line('LeBron James', 'points')
    print(f"\nSuggested Line for LeBron James (Points):")
    print(f"Suggested Line: {suggested_line['suggested_line']}")
    print(f"Range: {suggested_line['range']}")
    print(f"Confidence: {suggested_line['confidence']}")
    print(f"Recent Form: {suggested_line['recent_form']}")
    print(f"Mean: {suggested_line['mean']}")
    print(f"Last 5 games average: {suggested_line['last_5_avg']}")

    # Get suggested line with matchup for points
    suggested_line_with_matchup = analyzer.suggest_line_with_matchup('LeBron James', 'points', 'Lakers')
    print(f"\nSuggested Line with Matchup for LeBron James (Points) vs Lakers:")
    print(f"Suggested Line: {suggested_line_with_matchup['suggested_line']}")
    print(f"Range: {suggested_line_with_matchup['range']}")
    print(f"Confidence: {suggested_line_with_matchup['confidence']}")
    print(f"Recent Form: {suggested_line_with_matchup['recent_form']}")
    print(f"Mean: {suggested_line_with_matchup['mean']}")
    print(f"Last 5 games average: {suggested_line_with_matchup['last_5_avg']}")
    print(f"Opponent Factor: {suggested_line_with_matchup['opponent_factor']}")
    print(f"Vs Opponent: {suggested_line_with_matchup['vs_opponent']}")

if __name__ == "__main__":
    main()