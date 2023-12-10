import streamlit as st

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
    selected_players = []
    for player in player_list:
        fantasy_positions = ', '.join(player.get('fantasy_positions', [])) if 'fantasy_positions' in player else None
        label = f"{player['full_name'] if player['full_name'] else player['player_id']} - {fantasy_positions}"
        selected = st.checkbox(label, key=f"user_checkbox_{player['player_id']}")
        if selected:
            # Append the full name
            selected_players.append(player)
    return selected_players
