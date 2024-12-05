import click
import pandas as pd
from analyzer import PrizePicksAnalyzer
from data_scraper import SportsScraper
from tabulate import tabulate

@click.group()
def cli():
    """Prize Picks Analyzer CLI"""
    pass

@cli.command()
@click.option('--sport', type=click.Choice(['NBA', 'NFL', 'MLB']), required=True, help='Sport to analyze')
@click.option('--player', required=True, help='Player name')
@click.option('--metric', required=True, help='Metric to analyze (e.g., points, rebounds)')
@click.option('--line', required=True, type=float, help='Prize Picks line')
@click.option('--games', default=20, help='Number of games to analyze')
def analyze(sport, player, metric, line, games):
    """Analyze player performance and get over/under recommendation"""
    click.echo(f"\nAnalyzing {player} - {metric} (Line: {line})")
    
    # Initialize scraper and analyzer
    scraper = SportsScraper()
    analyzer = PrizePicksAnalyzer()
    
    # Get data based on sport
    if sport == 'NBA':
        data = scraper.get_nba_stats(player, games)
    elif sport == 'NFL':
        data = scraper.get_nfl_stats(player, games)
    elif sport == 'MLB':
        data = scraper.get_mlb_stats(player, games)
    
    if data is None:
        click.echo("Failed to fetch player data")
        return
    
    # Add data to analyzer
    for _, game in data.iterrows():
        analyzer.add_game_data(player, game['date'], game.to_dict())
    
    # Get analysis
    analysis = analyzer.analyze_trend(player, metric, line)
    
    # Display results
    click.echo("\nRecent Performance:")
    click.echo(f"Last 5 games average: {analysis['last_5_avg']:.2f}")
    click.echo(f"Last 10 games average: {analysis['last_10_avg']:.2f}")
    click.echo(f"\nTrend: {analysis['trend']}")
    click.echo(f"Recommendation: {analysis['recommendation']}")
    click.echo(f"Confidence: {analysis['confidence']}")
    
    # Display recent games
    click.echo("\nRecent Games:")
    recent_games = data.tail(5)[['date', metric, 'opponent']]
    click.echo(tabulate(recent_games, headers='keys', tablefmt='grid'))

@cli.command()
@click.option('--sport', type=click.Choice(['NBA', 'NFL', 'MLB']), required=True, help='Sport to analyze')
@click.option('--player', required=True, help='Player name')
@click.option('--games', default=10, help='Number of games to show')
def stats(sport, player, games):
    """View recent player statistics"""
    click.echo(f"\nFetching recent stats for {player}")
    
    scraper = SportsScraper()
    
    # Get data based on sport
    if sport == 'NBA':
        data = scraper.get_nba_stats(player, games)
    elif sport == 'NFL':
        data = scraper.get_nfl_stats(player, games)
    elif sport == 'MLB':
        data = scraper.get_mlb_stats(player, games)
    
    if data is None:
        click.echo("Failed to fetch player data")
        return
    
    # Display stats
    click.echo("\nRecent Games:")
    click.echo(tabulate(data, headers='keys', tablefmt='grid'))
    
    # Calculate and display averages
    click.echo("\nAverages:")
    averages = data.mean(numeric_only=True)
    click.echo(tabulate(pd.DataFrame(averages).T, headers='keys', tablefmt='grid'))

if __name__ == '__main__':
    cli()
