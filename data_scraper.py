import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import re
from urllib.parse import quote

class SportsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _safe_request(self, url, retries=3, delay=1):
        """Make a safe request with retries and delay"""
        for i in range(retries):
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    time.sleep(delay)  # Be nice to the servers
                    return response
                elif response.status_code == 404:
                    print(f"Player not found: {url}")
                    return None
            except Exception as e:
                if i == retries - 1:
                    print(f"Failed to fetch data after {retries} attempts: {str(e)}")
                    return None
                time.sleep(delay * (i + 1))
        return None

    def _format_player_name(self, name):
        """Format player name for URL"""
        # Convert to lowercase and replace spaces with hyphens
        formatted = name.lower().replace(' ', '-')
        # Remove special characters
        formatted = re.sub(r'[^a-z0-9-]', '', formatted)
        return formatted

    def get_nba_stats(self, player_name, num_games=20):
        """
        Scrape NBA stats from Basketball Reference
        """
        print(f"\nAttempting to fetch data for {player_name}...")
        
        try:
            # Format player name for URL
            formatted_name = self._format_player_name(player_name)
            first_letter = formatted_name[0]
            
            # Direct URL to player's page
            player_url = f"https://www.basketball-reference.com/players/{first_letter}/{formatted_name}.html"
            print(f"Trying direct URL: {player_url}")
            response = self._safe_request(player_url)
            
            if not response:
                print("Direct URL failed, trying search...")
                # Try search if direct URL fails
                search_url = f"https://www.basketball-reference.com/search/search.fcgi?search={quote(player_name)}"
                print(f"Search URL: {search_url}")
                response = self._safe_request(search_url)
                
                if not response:
                    print(f"Could not find player: {player_name}")
                    return pd.DataFrame()
                
                print("Parsing search results...")
                soup = BeautifulSoup(response.content, 'html.parser')
                search_result = soup.find('div', {'class': 'search-item-name'})
                
                if not search_result:
                    print(f"No search results found for: {player_name}")
                    return pd.DataFrame()
                
                player_link = search_result.find('a')['href']
                player_url = f"https://www.basketball-reference.com{player_link}"
                print(f"Found player URL: {player_url}")
                response = self._safe_request(player_url)
                
                if not response:
                    print(f"Could not access player page for: {player_name}")
                    return pd.DataFrame()
            
            # Get current season
            season = datetime.now().year
            if datetime.now().month < 8:  # If before August, use previous season
                season -= 1
            
            # Get game log URL
            gamelog_url = player_url.replace('.html', f'/gamelog/{season}')
            print(f"Fetching game log from: {gamelog_url}")
            response = self._safe_request(gamelog_url)
            
            if not response:
                print(f"Could not access game log for: {player_name}")
                return pd.DataFrame()

            print("Parsing game log data...")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the game log table
            table = soup.find('table', {'id': 'pgl_basic'})
            if not table:
                print("No game log table found!")
                return pd.DataFrame()
                
            # Parse table into DataFrame
            print("Converting table to DataFrame...")
            df = pd.read_html(str(table))[0]
            print(f"Found {len(df)} games")
            print(f"Columns: {list(df.columns)}")
            
            # Clean up the DataFrame
            df = df[df['Rk'].notna()]  # Remove summary rows
            print(f"After cleaning: {len(df)} games")
            
            # Convert relevant columns to numeric
            numeric_cols = ['PTS', 'AST', 'TRB', 'STL', 'BLK', '3P']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print("Final stats shape:", df.shape)
            print("Sample of data:")
            print(df.head())
            
            # Select and rename relevant columns
            cols_to_rename = {
                'PTS': 'points',
                'TRB': 'rebounds',
                'AST': 'assists',
                '3P': 'threes',
                'Date': 'date',
                'Opp': 'opponent',
                'MP': 'minutes'
            }
            
            # Only keep columns that exist in the dataframe
            cols_to_rename = {k: v for k, v in cols_to_rename.items() if k in df.columns}
            df = df.rename(columns=cols_to_rename)
            
            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'], format='mixed')
            
            # Sort by date and get last n games
            df = df.sort_values('date', ascending=False)
            if num_games:
                df = df.head(num_games)
            
            # Fill any missing values with 0
            numeric_cols = ['points', 'rebounds', 'assists', 'threes']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            print(f"Final dataset has {len(df)} rows with columns: {list(df.columns)}")
            print("Sample data:")
            print(df[['date', 'points', 'rebounds', 'assists', 'threes']].head())
            
            return df
            
        except Exception as e:
            print(f"Error in get_nba_stats: {str(e)}")
            import traceback
            print("Traceback:", traceback.format_exc())
            return pd.DataFrame()

    def get_nfl_stats(self, player_name, num_games=20):
        """
        Scrape NFL stats from Pro Football Reference
        """
        try:
            # Format player name for URL
            formatted_name = self._format_player_name(player_name)
            
            # Search for player
            search_url = f"https://www.pro-football-reference.com/search/search.fcgi?search={quote(player_name)}"
            response = self._safe_request(search_url)
            
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the first search result
            search_result = soup.find('div', {'class': 'search-item-name'})
            if not search_result:
                print(f"Player not found: {player_name}")
                return None
                
            player_link = search_result.find('a')['href']
            
            # Get player's game log
            season = datetime.now().year
            if datetime.now().month < 8:  # If before August, use previous season
                season -= 1
                
            gamelog_url = f"https://www.pro-football-reference.com{player_link.replace('.htm', '')}/gamelog/{season}"
            response = self._safe_request(gamelog_url)
            
            if not response:
                return None
                
            # Parse game log
            games_df = pd.read_html(response.content, match='Game Logs')[0]
            
            # Clean up the dataframe
            games_df = games_df[games_df['Date'].notna()]
            
            # Rename columns based on position (we'll need to detect position)
            if 'Pass Yds' in games_df.columns:  # QB stats
                games_df = games_df.rename(columns={
                    'Date': 'date',
                    'Pass Yds': 'passing_yards',
                    'Pass TD': 'passing_td',
                    'Rush Yds': 'rushing_yards',
                    'Int': 'interceptions',
                    'Opp': 'opponent'
                })
            elif 'Rush Yds' in games_df.columns:  # RB stats
                games_df = games_df.rename(columns={
                    'Date': 'date',
                    'Rush Yds': 'rushing_yards',
                    'Rush TD': 'rushing_td',
                    'Rec Yds': 'receiving_yards',
                    'Rec TD': 'receiving_td',
                    'Opp': 'opponent'
                })
            
            # Convert date
            games_df['date'] = pd.to_datetime(games_df['date'])
            
            # Select last n games
            games_df = games_df.tail(num_games)
            
            return games_df
            
        except Exception as e:
            print(f"Error fetching NFL stats: {str(e)}")
            return None

    def get_mlb_stats(self, player_name, num_games=20):
        """
        Scrape MLB stats from Baseball Reference
        """
        try:
            # Search for player
            search_url = f"https://www.baseball-reference.com/search/search.fcgi?search={quote(player_name)}"
            response = self._safe_request(search_url)
            
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the first search result
            search_result = soup.find('div', {'class': 'search-item-name'})
            if not search_result:
                print(f"Player not found: {player_name}")
                return None
                
            player_link = search_result.find('a')['href']
            
            # Get player's game log
            season = datetime.now().year
            if datetime.now().month < 2:  # If before February, use previous season
                season -= 1
                
            gamelog_url = f"https://www.baseball-reference.com{player_link.replace('.shtml', '')}/gamelog/{season}"
            response = self._safe_request(gamelog_url)
            
            if not response:
                return None
                
            # Parse game log
            games_df = pd.read_html(response.content, match='Game Log')[0]
            
            # Clean up the dataframe
            games_df = games_df[games_df['Date'].notna()]
            
            # Rename columns
            games_df = games_df.rename(columns={
                'Date': 'date',
                'H': 'hits',
                'AB': 'at_bats',
                'HR': 'home_runs',
                'RBI': 'rbis',
                'Opp': 'opponent'
            })
            
            # Convert date
            games_df['date'] = pd.to_datetime(games_df['date'])
            
            # Select relevant columns and last n games
            relevant_cols = ['date', 'hits', 'at_bats', 'home_runs', 'rbis', 'opponent']
            games_df = games_df[relevant_cols].tail(num_games)
            
            return games_df
            
        except Exception as e:
            print(f"Error fetching MLB stats: {str(e)}")
            return None

if __name__ == "__main__":
    # Test the scraper
    scraper = SportsScraper()
    
    print("\nTesting NBA stats...")
    nba_stats = scraper.get_nba_stats("LeBron James", 5)
    if nba_stats is not None:
        print("\nNBA Stats Sample:")
        print(nba_stats)
        
    print("\nTesting NFL stats...")
    nfl_stats = scraper.get_nfl_stats("Patrick Mahomes", 5)
    if nfl_stats is not None:
        print("\nNFL Stats Sample:")
        print(nfl_stats)
        
    print("\nTesting MLB stats...")
    mlb_stats = scraper.get_mlb_stats("Mike Trout", 5)
    if mlb_stats is not None:
        print("\nMLB Stats Sample:")
        print(mlb_stats)
