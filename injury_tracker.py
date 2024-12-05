import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

class InjuryTracker:
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
                    return None
            except Exception as e:
                if i == retries - 1:
                    print(f"Failed to fetch data after {retries} attempts: {str(e)}")
                    return None
                time.sleep(delay * (i + 1))
        return None

    def get_nba_injuries(self, team_or_player=None):
        """Get NBA injury reports"""
        try:
            url = "https://www.espn.com/nba/injuries"
            response = self._safe_request(url)
            
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            injuries = []
            
            # Parse injury tables
            for item in soup.find_all('tr', class_=['oddrow', 'evenrow']):
                cells = item.find_all('td')
                if len(cells) >= 3:
                    injury_data = {
                        'player': cells[0].get_text(strip=True),
                        'team': cells[0].find('span').get_text(strip=True) if cells[0].find('span') else '',
                        'date': cells[1].get_text(strip=True),
                        'status': cells[2].get_text(strip=True),
                        'details': cells[3].get_text(strip=True) if len(cells) > 3 else ''
                    }
                    
                    # Filter by team or player if specified
                    if team_or_player:
                        if (team_or_player.lower() in injury_data['player'].lower() or 
                            team_or_player.lower() in injury_data['team'].lower()):
                            injuries.append(injury_data)
                    else:
                        injuries.append(injury_data)
            
            return pd.DataFrame(injuries)
            
        except Exception as e:
            print(f"Error fetching NBA injuries: {str(e)}")
            return None

    def get_nfl_injuries(self, team_or_player=None):
        """Get NFL injury reports"""
        try:
            url = "https://www.espn.com/nfl/injuries"
            response = self._safe_request(url)
            
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            injuries = []
            
            # Parse injury tables
            for item in soup.find_all('tr', class_=['oddrow', 'evenrow']):
                cells = item.find_all('td')
                if len(cells) >= 3:
                    injury_data = {
                        'player': cells[0].get_text(strip=True),
                        'team': cells[0].find('span').get_text(strip=True) if cells[0].find('span') else '',
                        'position': cells[1].get_text(strip=True),
                        'status': cells[2].get_text(strip=True),
                        'details': cells[3].get_text(strip=True) if len(cells) > 3 else ''
                    }
                    
                    if team_or_player:
                        if (team_or_player.lower() in injury_data['player'].lower() or 
                            team_or_player.lower() in injury_data['team'].lower()):
                            injuries.append(injury_data)
                    else:
                        injuries.append(injury_data)
            
            return pd.DataFrame(injuries)
            
        except Exception as e:
            print(f"Error fetching NFL injuries: {str(e)}")
            return None

    def get_mlb_injuries(self, team_or_player=None):
        """Get MLB injury reports"""
        try:
            url = "https://www.espn.com/mlb/injuries"
            response = self._safe_request(url)
            
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            injuries = []
            
            # Parse injury tables
            for item in soup.find_all('tr', class_=['oddrow', 'evenrow']):
                cells = item.find_all('td')
                if len(cells) >= 3:
                    injury_data = {
                        'player': cells[0].get_text(strip=True),
                        'team': cells[0].find('span').get_text(strip=True) if cells[0].find('span') else '',
                        'date': cells[1].get_text(strip=True),
                        'status': cells[2].get_text(strip=True),
                        'details': cells[3].get_text(strip=True) if len(cells) > 3 else ''
                    }
                    
                    if team_or_player:
                        if (team_or_player.lower() in injury_data['player'].lower() or 
                            team_or_player.lower() in injury_data['team'].lower()):
                            injuries.append(injury_data)
                    else:
                        injuries.append(injury_data)
            
            return pd.DataFrame(injuries)
            
        except Exception as e:
            print(f"Error fetching MLB injuries: {str(e)}")
            return None

    def check_player_injury(self, player_name, sport):
        """Check if a specific player is injured"""
        if sport == "NBA":
            injuries = self.get_nba_injuries(player_name)
        elif sport == "NFL":
            injuries = self.get_nfl_injuries(player_name)
        elif sport == "MLB":
            injuries = self.get_mlb_injuries(player_name)
        else:
            return None
            
        if injuries is not None and not injuries.empty:
            return injuries.iloc[0].to_dict()
        return None

if __name__ == "__main__":
    # Test the injury tracker
    tracker = InjuryTracker()
    
    # Test NBA injuries
    nba_injuries = tracker.get_nba_injuries("Lakers")
    if nba_injuries is not None:
        print("\nNBA Injuries:")
        print(nba_injuries)
        
    # Test specific player
    lebron_injury = tracker.check_player_injury("LeBron James", "NBA")
    if lebron_injury:
        print("\nLeBron James Injury Status:")
        print(lebron_injury)
