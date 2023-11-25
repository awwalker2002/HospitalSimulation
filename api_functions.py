import requests
from PIL import Image
from io import BytesIO
import json
from datetime import datetime, timedelta
from typing import Union

def get_user_info(username_or_user_id: Union[str,int]):
    base_url = 'https://api.sleeper.app/v1/'
    endpoint = f'user/{username_or_user_id}'

    # Construct the full URL
    full_url = f'{base_url}{endpoint}'

    # Make the API request
    response = requests.get(full_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        user_data = response.json()
        return user_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    

def get_avatar_images(user_info: dict):
    if user_info:
        avatar_id = user_info.get('avatar')

        if avatar_id:
            # Construct full-size and thumbnail URLs
            full_size_url = f'https://sleepercdn.com/avatars/{avatar_id}'
            thumbnail_url = f'https://sleepercdn.com/avatars/thumbs/{avatar_id}'

            # Download full-size image
            full_size_image_response = requests.get(full_size_url)
            full_size_image = Image.open(BytesIO(full_size_image_response.content))

            # Download thumbnail image
            thumbnail_image_response = requests.get(thumbnail_url)
            thumbnail_image = Image.open(BytesIO(thumbnail_image_response.content))

            return full_size_image, thumbnail_image
        else:
            print("User has no avatar.")
    else:
        print("User information not available.")
        return None, None
    


def get_user_leagues(user_id: Union[str,int], season: Union[str,int]) -> list:
    base_url = 'https://api.sleeper.app/v1/'
    endpoint = f'user/{user_id}/leagues/nfl/{season}'

    # Construct the full URL
    full_url = f'{base_url}{endpoint}'

    # Make the API request
    response = requests.get(full_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        leagues_data = response.json()
        return leagues_data # is a list of dictionaries
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


    
def get_selected_league_info(user_leagues: list, selected_league_name: Union[str,int]) -> dict:
    selected_league = [league for league in user_leagues if league['name'] == selected_league_name]

    if selected_league:
        return selected_league[0] # Returns dictionary with league information
    else:
        print(f"Selected league with ID {selected_league_name} not found.")
        return None
    


def get_league_rosters(league_id: Union[str,int]) -> list:
    base_url = 'https://api.sleeper.app/v1/'
    endpoint = f'league/{league_id}/rosters'

    # Construct the full URL
    full_url = f'{base_url}{endpoint}'

    # Make the API request
    response = requests.get(full_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        rosters_data = response.json()
        return rosters_data # Returns a list of dictionaries with roster info
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    


def get_user_roster_info(league_rosters: list, user_id: Union[str,int]) -> dict:
    user_roster = [roster for roster in league_rosters if roster['owner_id'] == user_id]

    if user_roster:
        return user_roster[0] # Returns dictionary with user roster information
    else:
        print(f"Roster with Owner ID {user_id} not found.")
        return None
    


def get_player_info() -> dict:
    # Check if the player info is saved locally and up-to-date
    try:
        with open('player_info.json', 'r') as file:
            player_info = json.load(file)
            last_updated = datetime.strptime(player_info.get('last_updated'), '%Y-%m-%d')
            
            # Only call the API if it hasn't been updated in the last 24 hours
            if datetime.now() - last_updated < timedelta(days=1):
                return player_info['data']
    except FileNotFoundError:
        pass  # File not found, or first-time retrieval

    # If local file is not available or outdated, make the API call
    base_url = 'https://api.sleeper.app/v1/'
    endpoint = 'players/nfl'

    # Construct the full URL
    full_url = f'{base_url}{endpoint}'

    # Make the API request
    response = requests.get(full_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        player_data = response.json()
        
        # Save the player info locally for future use
        player_info = {'last_updated': datetime.now().strftime('%Y-%m-%d'), 'data': player_data}
        with open('player_info.json', 'w') as file:
            json.dump(player_info, file)
        
        return player_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    


def get_user_roster_players(all_players: dict, user_roster: dict) -> list:
  user_roster_players = [
      {
            'full_name': all_players.get(player_id, {}).get('full_name'),
            'player_id': all_players.get(player_id, {}).get('player_id'),
            'fantasy_positions': all_players.get(player_id, {}).get('fantasy_positions'),
            'team': all_players.get(player_id, {}).get('team'),
            'stats_id': all_players.get(player_id, {}).get('stats_id'),
            'sportradar_id': all_players.get(player_id, {}).get('fantasy_data_id')
      }
      for player_id in user_roster['players']
    ]
  return user_roster_players #is a list of dictionaries with player info



def get_user_starters(all_players: dict, user_roster: dict) -> list:
  user_starter_players = [
      {
            'full_name': all_players.get(player_id, {}).get('full_name'),
            'player_id': all_players.get(player_id, {}).get('player_id'),
            'fantasy_positions': all_players.get(player_id, {}).get('fantasy_positions'),
            'team': all_players.get(player_id, {}).get('team'),
            'stats_id': all_players.get(player_id, {}).get('stats_id'),
            'sportradar_id': all_players.get(player_id, {}).get('fantasy_data_id')
      }
      for player_id in user_roster['starters']
    ]
  return user_starter_players #is a list of dictionaries with player info


def get_current_state(sport:str) -> dict:
    base_url = 'https://api.sleeper.app/v1/'
    endpoint = f'state/{sport}'

    # Construct the full URL
    full_url = f'{base_url}{endpoint}'

    # Make the API request
    response = requests.get(full_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        state_data = response.json()
        return state_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def get_week_projections(season_type: str, season: Union[str, int], week: Union[str, int]) -> dict:
    # Assuming you have a base URL for projections like the one you provided
    projections_base_url = "https://api.sleeper.app/v1/projections/{}".format("nfl")

    # Function to make the API call
    def _call(url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    # Construct the URL and make the API call
    url = "{}/{}/{}/{}".format(projections_base_url, season_type, season, week)
    return _call(url)


def calculate_projections(roster_projections: list, scoring_settings: dict) -> list:
  for player in roster_projections:
    player_projection = 0
    for key, value in player.items():
        if key in scoring_settings:
            player_projection += value * scoring_settings[key]
    # Round player projection to hundredths place
    player_projection = round(player_projection, 2)
    # Add the calculated projection to the player dictionary
    player['projected_points'] = player_projection

  return roster_projections



def add_projections(user_roster_players: list, projections: dict) -> list:
  projections_added = []

  for player in user_roster_players:
    player_id = player.get('player_id')
    if player_id in projections:
      merged_player_info = {**player, **projections[player_id]}
      projections_added.append(merged_player_info)

  return projections_added


def optimize_starters_projections(player_list, positions_list):
    starting_lineup = []

    for position in positions_list:
        if position == 'BN':
            break  # Stop when bench position is encountered

        # Deal with flex
        if position == 'FLEX':
            flex_candidates = [player for player in player_list if any(pos in player['fantasy_positions'] for pos in ['RB', 'WR', 'TE']) and player not in starting_lineup]
            if flex_candidates:
                max_flex_candidate = max(flex_candidates, key=lambda x: x['projected_points'])
                max_flex_candidate['position'] = 'FLEX'
                starting_lineup.append(max_flex_candidate)
                continue  # Move to the next position

        # Deal with superflex
        if position == 'SUPER_FLEX':
            superflex_candidates = [player for player in player_list if any(pos in player['fantasy_positions'] for pos in ['QB', 'RB', 'WR', 'TE']) and player not in starting_lineup]
            if superflex_candidates:
                max_superflex_candidate = max(superflex_candidates, key=lambda x: x['projected_points'])
                max_superflex_candidate['position'] = 'SUPER_FLEX'
                starting_lineup.append(max_superflex_candidate)
                continue  # Move to the next position

        # Filter players by the current position
        players_for_position = [player for player in player_list if position in player['fantasy_positions'] and player not in starting_lineup]

        if players_for_position:
            # Find the player with the maximum projected points for the current position
            max_projected_player = max(players_for_position, key=lambda x: x['projected_points'])
            max_projected_player['position'] = position

            # Add the player to the starting lineup
            starting_lineup.append(max_projected_player)

    return starting_lineup