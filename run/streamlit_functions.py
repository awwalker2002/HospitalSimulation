import streamlit as st
from data_functions import * 
from fantasy_pros_scraper import * 


def print_players_projections(players: list):
    for player in players:
        if 'full_name' in player and player['full_name'] is not None:
            full_name = player['full_name']
            if 'fantasy_positions' in player and player['fantasy_positions'] is not None:
                fantasy_positions = ', '.join(player['fantasy_positions'])
            else:
                fantasy_positions = None

            # Get projected points
            projected_points = player.get('projected_points', None)

            # Display full name, position(s), and projected points
            st.write(f"{full_name} - {fantasy_positions} - Projected Points: {projected_points}")

        elif 'player_id' in player:
            # Handling defenses, which don't have a full name
            fantasy_positions = ', '.join(player.get('fantasy_positions', [])) if 'fantasy_positions' in player else None
            projected_points = player.get('projected_points', None)
            st.write(f"{player['player_id']} - {fantasy_positions} - Projected Points: {projected_points}")




def print_players_rankings(players: list):
    for player_info in players:
        player_name = player_info.get('full_name', '')
        starting_position = player_info.get('starting_position', '')
        ranking_key = f'{starting_position.lower()}_ecr_ranking'
        ranking = player_info.get(ranking_key, 'unranked')
        starting_position = starting_position.replace("_", "")

        if starting_position == 'DEF':
            # Print format for DEF
            st.write(f"{player_info.get('player_id', '')} - {starting_position} -Expert Position Ranking: {ranking}")
        else:
            if player_name != "EMPTY":
                # Print format for non-DEF with player name
                st.write(f"{player_name} - {starting_position} - Expert Position Ranking: {ranking}")
            else:
                # Print format for non-DEF without player name
                st.write(f"{player_name} - {starting_position}")




def checkbox_players(player_list: list):
    """ Takes a list of players and creates selectable checkboxes for each player
    Arguments:
        - player_list: list of dictionaries where each dictionary corresponds to a player and has their info
    Returns:
        - list containing the dictionary for each selected player
    """
    selected_players = []
    for player in player_list:
        fantasy_positions = ', '.join(player.get('fantasy_positions', [])) if 'fantasy_positions' in player else None
        label = f"{player['full_name'] if player['full_name'] else player['player_id']} - {fantasy_positions}"
        selected = st.checkbox(label, key=f"user_checkbox_{player['player_id']}")
        if selected:
            # Append the full name
            selected_players.append(player)
    return selected_players




def show_trade_form(username: str, league_rosters: list, user_info, user_roster_ros_rankings: list, ros_rankings: list, player_data: dict):
    """ Creates the streamlit form that allows user to select players and submit a trade to be analyzed
    
    Returns:
        - submit_button that tells the application to analyze a trade
    """
    
    col1, col2 = st.columns(2)

    with st.form("Trade Analyzer"):
        with col1:
            user_team = st.selectbox("**Your Roster :football::**", options=[username])
            user_selected_players = checkbox_players(user_roster_ros_rankings)

        with col2:
            other_league_usernames = get_other_league_usernames(league_rosters, user_info)
            team_to_trade_with = st.selectbox("**Select a user to trade with :football::**", options=other_league_usernames.values())

            trade_selected_players = []
            if team_to_trade_with:
                trade_user_id = next((user_id for user_id, username in other_league_usernames.items() if username == team_to_trade_with), None)
                trade_roster_info = get_user_roster_info(league_rosters, trade_user_id)
                trade_roster_players = get_user_roster_players(player_data, trade_roster_info)
                trade_ros_rankings = add_ros_rankings(trade_roster_players, ros_rankings, "fantasy_names.db")
                trade_selected_players = checkbox_players(trade_ros_rankings)

        submit_button = st.form_submit_button("Analyze Trade")

    return user_selected_players, trade_selected_players, team_to_trade_with, submit_button, trade_ros_rankings




def analyze_trade(user_roster_ros_rankings: list, ros_rankings: list, user_selected_players: list, trade_selected_players: list, selected_league: dict, current_state: dict):
    """
    
    Uses functions from api_functions to calculate the overall differences in projections before and after the trade
    
    """
    end_week = get_end_week(selected_league)
    user_roster_after, trade_roster_after = swap_players(user_roster_ros_rankings, ros_rankings, user_selected_players, trade_selected_players)
    user_difference, trade_difference = calculate_total_projection_differences(user_roster_ros_rankings, user_roster_after, ros_rankings, trade_roster_after, current_state['league_season'], current_state['week'], end_week, selected_league)
    
    return user_difference, trade_difference, user_selected_players, trade_selected_players




def display_trade_results(username: str, user_difference: float, trade_difference: float, user_selected_players: list, trade_selected_players: list, team_to_trade_with: str):
    """
    
    Displays the players involved in a proposed trade along with their rankings
    Returns the average rankings of both sides of the trade to be used for future analysis
    
    """
    
    col1, col2 = st.columns(2)

    with col1:
        trend_emoji = ":chart_with_downwards_trend:" if user_difference < 0 else ":chart_with_upwards_trend:"
        st.write(f"**Net Change In Points for {username}:** {user_difference} {trend_emoji}")
        st.write("Players Received:")
        for player in trade_selected_players:
            st.write(f"- {player['full_name'] if player['full_name'] else player['player_id']} ({', '.join(player['fantasy_positions'])}) - Expert ROS Ranking: {player['ros_ecr_ranking']}")
        avg_rank_received = calculate_average_rankings(trade_selected_players)

    with col2:
        trend_emoji2 = ":chart_with_downwards_trend:" if trade_difference < 0 else ":chart_with_upwards_trend:"
        st.write(f"**Net Change In Points for {team_to_trade_with}:** {trade_difference} {trend_emoji2}")
        st.write("Players Traded Away:")
        for player in user_selected_players:
            st.write(f"- {player['full_name'] if player['full_name'] else player['player_id']} ({', '.join(player['fantasy_positions'])}) - Expert ROS Ranking: {player['ros_ecr_ranking']}")
        avg_rank_sent = calculate_average_rankings(user_selected_players)

    return avg_rank_received, avg_rank_sent




def display_trade_decision(user_difference: float, trade_difference: float, avg_rank_received: float, avg_rank_sent: float):
    """
    
    Need to improve the logic, but it provides a "recommendation" based on change in projections after the trade and the average rankings of
    the players involved in the trade. Doesn't provide great recommendations because it just calculates average ranking.
    
    """
    
    if (user_difference > trade_difference) and (user_difference > 0) and (avg_rank_received < avg_rank_sent):
        st.header("This trade is likely to benefit your team! :100:")
    elif (user_difference < 0) and (avg_rank_received > avg_rank_sent):
        st.header("This trade is unlikely to benefit your team :cry:")
    else:
        st.header("This is a fairly even trade. Make the decision that you feel is best :shrug:")
