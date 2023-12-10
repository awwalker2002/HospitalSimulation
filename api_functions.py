import requests
from PIL import Image
from io import BytesIO
import json
from datetime import datetime, timedelta
from typing import Union
import sqlite3
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner = False)
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
    
@st.cache_data(show_spinner = False)
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
    

@st.cache_data(show_spinner = False)
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


@st.cache_data(show_spinner = False)    
def get_selected_league_info(user_leagues: list, selected_league_name: Union[str,int]) -> dict:
    selected_league = [league for league in user_leagues if league['name'] == selected_league_name]

    if selected_league:
        return selected_league[0] # Returns dictionary with league information
    else:
        print(f"Selected league with ID {selected_league_name} not found.")
        return None
    

@st.cache_data(show_spinner = False)
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

@st.cache_data(show_spinner=False)
def get_other_league_usernames(league_rosters: list, user_info: dict) -> dict:
    league_usernames_dict = {}
    for roster in league_rosters:
        if roster['owner_id'] != user_info['user_id']:
            user_id = roster['owner_id']
            info = get_user_info(user_id)
            league_usernames_dict[user_id] = info['username']
    return league_usernames_dict
    

@st.cache_data(show_spinner = False)
def get_user_roster_info(league_rosters: list, user_id: Union[str,int]) -> dict:
    user_roster = [roster for roster in league_rosters if roster['owner_id'] == user_id]

    if user_roster:
        return user_roster[0] # Returns dictionary with user roster information
    else:
        print(f"Roster with Owner ID {user_id} not found.")
        return None
    

@st.cache_data(show_spinner = False)
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


@st.cache_data(show_spinner = False)
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


@st.cache_data(show_spinner = False)
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



def add_projections(user_roster_players: list, projections: dict) -> list:
  projections_added = []

  for player in user_roster_players:
    player_id = player.get('player_id')
    if player_id in projections:
      merged_player_info = {**player, **projections[player_id]}
      projections_added.append(merged_player_info)

  return projections_added



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




@st.cache_data(show_spinner = False)
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
            else:
                # Add empty slot for FLEX if no candidates
                starting_lineup.append({'position': 'FLEX', 'full_name': 'EMPTY', 'projected_points': 0})
                continue  # Move to the next position

        # Deal with superflex
        if position == 'SUPER_FLEX':
            superflex_candidates = [player for player in player_list if any(pos in player['fantasy_positions'] for pos in ['QB', 'RB', 'WR', 'TE']) and player not in starting_lineup]
            if superflex_candidates:
                max_superflex_candidate = max(superflex_candidates, key=lambda x: x['projected_points'])
                max_superflex_candidate['position'] = 'SUPER_FLEX'
                starting_lineup.append(max_superflex_candidate)
                continue  # Move to the next position
            else:
                # Add empty slot for SUPER_FLEX if no candidates
                starting_lineup.append({'position': 'SUPER_FLEX', 'full_name': 'EMPTY', 'projected_points': 0})
                continue  # Move to the next position

        # Filter players by the current position
        players_for_position = [player for player in player_list if position in player['fantasy_positions'] and player not in starting_lineup]

        if players_for_position:
            # Find the player with the maximum projected points for the current position
            max_projected_player = max(players_for_position, key=lambda x: x['projected_points'])
            max_projected_player['position'] = position

            # Add the player to the starting lineup
            starting_lineup.append(max_projected_player)
        else:
            # Add empty slot if no candidates for the current position
            starting_lineup.append({'position': position, 'full_name': 'EMPTY', 'projected_points': 0})

    return starting_lineup


# Get league format from settings
def get_format(rec_value: int) -> str:
  if rec_value == 0:
      format = 'standard'
  elif rec_value == 0.5:
      format = 'half-ppr'
  elif rec_value == 1:
      format = 'ppr'

  return format


# Get each unique position in selected leagues starting lineup
def get_starting_positions_set(selected_league: dict) -> set:
  starting_positions = {position for position in selected_league['roster_positions'] if position != 'BN'}
  return starting_positions


# Match weekly FantasyPros rankings to the roster using the database
@st.cache_data(show_spinner = False)
def add_weekly_rankings(player_list, position_rankings, database_file):
    # Connect to the database
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    # Create a new list to store the updated player information
    updated_player_list = []

    # Iterate through each player in the player list
    for player_info in player_list:
        # Make a copy of the player dictionary
        updated_player_info = player_info.copy()

        player_name = updated_player_info.get('full_name') or updated_player_info.get('player_id', '')

        # Get the fantasy pros name using a parameterized query
        query = "SELECT fantasy_pros_name FROM matched_names WHERE sleeper_name = ?"
        cursor.execute(query, (player_name,))
        result = cursor.fetchone()

        if result is not None:
            fantasy_pros_name = result[0]

            # Find the corresponding position for the player
            positions = updated_player_info.get('fantasy_positions', [])

            for position in positions:
                # Get the rankings for the player's position
                position_ranking = position_rankings.get(position, [])

                # Find the player's ranking in the position rankings
                player_ranking = next(
                    (player.get('rank_ecr', 'unranked') for player in position_ranking if (player['player_name'] == fantasy_pros_name or player['player_team_id'] == fantasy_pros_name)),
                    'unranked'
                )

                # Add the ranking to the player's copied dictionary
                key = f'{position.lower()}_ecr_ranking'
                updated_player_info[key] = player_ranking

            # Add FLEX and SUPER_FLEX rankings for every player
            flex_ranking = next(
                (player.get('rank_ecr', 'unranked') for player in position_rankings.get('FLEX', []) if player['player_name'] == fantasy_pros_name),
                'unranked'
            )
            updated_player_info['flex_ecr_ranking'] = flex_ranking

            super_flex_ranking = next(
                (player.get('rank_ecr', 'unranked') for player in position_rankings.get('SUPER_FLEX', []) if player['player_name'] == fantasy_pros_name),
                'unranked'
            )
            updated_player_info['super_flex_ecr_ranking'] = super_flex_ranking

        else:
            # If no match found in the database, set rank_ecr to "unranked" for each position
            for position in positions:
                key = f'{position.lower()}_ecr_ranking'
                updated_player_info[key] = 'unranked'

            # Set FLEX and SUPER_FLEX rankings to "unranked" if positions are not found
            updated_player_info['flex_ecr_ranking'] = 'unranked'
            updated_player_info['super_flex_ecr_ranking'] = 'unranked'

        # Add the updated player information to the new list
        updated_player_list.append(updated_player_info)

    # Close the database connection
    connection.close()

    return updated_player_list



@st.cache_data(show_spinner = False)
def add_ros_rankings(player_list, ros_rankings, database_file):
    # Connect to the database
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    # Create a new list to store the updated player information
    updated_player_list = []

    # Iterate through each player in the player list
    for player_info in player_list:
        # Make a copy of the player dictionary
        updated_player_info = player_info.copy()

        player_name = updated_player_info.get('full_name') or updated_player_info.get('player_id', '')

        # Get the fantasy pros name using a parameterized query
        query = "SELECT fantasy_pros_name FROM matched_names WHERE sleeper_name = ?"
        cursor.execute(query, (player_name,))
        result = cursor.fetchone()

        if result is not None:
            fantasy_pros_name = result[0]
            # Find the player's ranking in the position rankings
            # Special case if player is team defense
            if updated_player_info['fantasy_positions'][0] == 'DEF':
                player_ranking = next(
                    (player.get('rank_ecr', 'unranked') for player in ros_rankings if (player['player_position_id'] == "DST" and player['player_team_id'] == fantasy_pros_name)),
                    'unranked'
                )
            else:
                player_ranking = next(
                    (player.get('rank_ecr', 'unranked') for player in ros_rankings if (player['player_name'] == fantasy_pros_name or player['player_team_id'] == fantasy_pros_name)),
                    'unranked'
                )
            updated_player_info['ros_ecr_ranking'] = player_ranking
        else:
            updated_player_info['ros_ecr_ranking'] = 'unranked'
        # Add updated player info with ros rankings to list
        updated_player_list.append(updated_player_info)
    
    # Close the database connection
    connection.close()

    return updated_player_list
        



# Use weekly rankings to generate expert recommended starting lineup
@st.cache_data(show_spinner = False)
def optimize_starting_lineup_rankings(roster_with_rankings, positions):
    # Create a copy of the roster to avoid modifying the original
    temp_rost = roster_with_rankings.copy()

    # Create a starting lineup object
    starting_lineup = []

    # Iterate through the list of positions until the bench position
    for position in positions:
        if position == "BN":
            break

        # Determine the key for the ranking based on the position
        key = f'{position.lower()}_ecr_ranking'

        # If position is FLEX or SUPER_FLEX, select the player with the best flex/superflex ranking among all remaining players
        if position == 'FLEX':
            # For FLEX, eligible positions are WR, RB, and TE
            eligible_players = [player for player in temp_rost if any(pos in player['fantasy_positions'] for pos in ['WR', 'RB', 'TE'])]
        elif position == 'SUPER_FLEX':
            # For SUPER_FLEX, eligible positions are QB, WR, RB, and TE
            eligible_players = [player for player in temp_rost if any(pos in player['fantasy_positions'] for pos in ['QB', 'WR', 'RB', 'TE'])]
        else:
            # For other positions, filter players based on the current position
            eligible_players = [player for player in temp_rost if position in player['fantasy_positions']]

        if not eligible_players or all(player.get(key, 'unranked') == 'unranked' for player in eligible_players):
            # If no eligible players or all players are unranked, add an empty slot/placeholder to the starting lineup
            starting_lineup.append({'position': position, 'starting_position': position, 'is_starting': False, 'full_name': 'EMPTY'})
        else:
            # For other positions, select the player with the best ranking
            best_player = min(eligible_players, key=lambda x: x.get(key, float('inf')) if x.get(key, 'unranked') != 'unranked' else float('inf'))

            # Add the selected player to the starting lineup
            best_player['starting_position'] = position
            best_player['is_starting'] = True
            starting_lineup.append(best_player)

            # Remove the selected player from the list of eligible players
            temp_rost.remove(best_player)

    return starting_lineup


@st.cache_data(show_spinner = False)
def get_end_week(league_info: dict) -> int:
    num_teams = league_info['settings']['playoff_teams']
    playoff_weeks = 0
    while num_teams > 1:
        num_teams /= 2
        playoff_weeks += 1
    if league_info['settings']['playoff_round_type'] == 0:
        pass 
    elif league_info['settings']['playoff_round_type'] == 1:
        playoff_weeks += 1 
    elif league_info['settings']['playoff_round_type'] == 2:
        playoff_weeks *= 1
    else:
        print("Playoff format not recognized")
        return
    end_week = playoff_weeks + league_info['settings']['playoff_week_start'] - 1
    return end_week
    

def swap_players(team1: list, team2: list, players_to_swap_from_team1: list, players_to_swap_from_team2: list) -> list:
    # Remove players from team1 and add them to team2
    team1_copy = [player.copy() for player in team1]
    team2_copy = [player.copy() for player in team2]

    for player_to_swap in players_to_swap_from_team1:
        matching_players = [p for p in team1_copy if p['full_name'] == player_to_swap['full_name']]
        if matching_players:
            team1_copy.remove(matching_players[0])
            team2_copy.append(matching_players[0])

    # Remove players from team2 and add them to team1
    for player_to_swap in players_to_swap_from_team2:
        matching_players = [p for p in team2_copy if p['full_name'] == player_to_swap['full_name']]
        if matching_players:
            team2_copy.remove(matching_players[0])
            team1_copy.append(matching_players[0])

    return team1_copy, team2_copy



def get_total_score(starting_lineup: list) -> float:
    total_score = 0
    for player in starting_lineup:
        total_score += player['projected_points']
    return round(total_score, 2)



def calculate_total_projection_differences(team1_before: list, team1_after: list, team2_before: list, team2_after: list, current_season: int, current_week: int, end_week: int, selected_league: dict):
    team1_before_total = 0
    team1_after_total = 0
    team2_before_total = 0
    team2_after_total = 0
    for week in range(current_week, end_week + 1):
        # Get projections for the week
        week_projections = get_week_projections('regular', current_season, week)
        # Add projections to each team
        team1_before_projections = add_projections(team1_before, week_projections)
        team1_after_projections = add_projections(team1_after, week_projections)
        team2_before_projections = add_projections(team2_before, week_projections)
        team2_after_projections = add_projections(team2_after, week_projections)
        # Get projected scores for each team
        team1_before_scores = calculate_projections(team1_before_projections, selected_league['scoring_settings'])
        team1_after_scores = calculate_projections(team1_after_projections, selected_league['scoring_settings'])
        team2_before_scores = calculate_projections(team2_before_projections, selected_league['scoring_settings'])
        team2_after_scores = calculate_projections(team2_after_projections, selected_league['scoring_settings'])
        # Optimize starters for each team
        team1_before_optimized = optimize_starters_projections(team1_before_scores, selected_league['roster_positions'])
        team1_after_optimized = optimize_starters_projections(team1_after_scores, selected_league['roster_positions'])
        team2_before_optimized = optimize_starters_projections(team2_before_scores, selected_league['roster_positions'])
        team2_after_optimized = optimize_starters_projections(team2_after_scores, selected_league['roster_positions'])
        # Sum up the total score for each team
        team1_before_score = get_total_score(team1_before_optimized)
        team1_after_score = get_total_score(team1_after_optimized)
        team2_before_score = get_total_score(team2_before_optimized)
        team2_after_score = get_total_score(team2_after_optimized)
        # Add total scores to running totals
        team1_before_total += team1_before_score
        team1_after_total += team1_after_score
        team2_before_total += team2_before_score
        team2_after_total += team2_after_score
    # Calculate the differences between after and before rosters
    team1_difference = team1_after_total - team1_before_total
    team2_difference = team2_after_total - team2_before_total
    return round(team1_difference, 2), round(team2_difference, 2)



def calculate_average_rankings(players_with_ros_rankings: list) -> float:
    if not players_with_ros_rankings:
        return 420
    
    # Replace "unranked" with 420 in the list
    modified_rankings = [420 if player["ros_ecr_ranking"] == "unranked" else player["ros_ecr_ranking"] for player in players_with_ros_rankings]

    # Calculate the average
    average_ranking = sum(modified_rankings) / len(modified_rankings)

    return round(average_ranking, 2)
