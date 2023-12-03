import streamlit as st
from api_functions import *
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



# Start of webpage
st.set_page_config(layout="wide")
st.title('Fantasy Football Advice')
st.markdown('This is an application to provide fantasy football advice \
            to Sleeper Users. Use the sidebar to navigate the webpage.')
st.sidebar.title('Navigation')
page = st.sidebar.radio('Pages', options = ['Home', 'Start/Sit Advice', 'Trade Analysis'])


#get user info from inputted username
username = st.text_input('Enter your Sleeper Username')
user_info = get_user_info(username)
if username and user_info is None:
    st.write("**Username does not exist**")

#get user avatar images
if user_info:
    full_size_image, thumbnail_image = get_avatar_images(user_info)
    st.image(thumbnail_image)
#pull up leagues so user can pick one 
    current_state = get_current_state('nfl')
    user_leagues = get_user_leagues(user_info['user_id'], current_state['league_season'])
    if not user_leagues:
        st.write("**User is not in any leagues**")
    else:
        selected_league = st.selectbox(label = "Which league would you like to look at?",
                    options = [(league['name']) for league in user_leagues])

    #once user selects league, show their roster with projections
        if 'selected_league' in locals(): #PROBABLY have to change this line to avoid error when no leagues
            # ALSO could be reuse of selected_league variable name
            selected_league = get_selected_league_info(user_leagues, selected_league)
            #get league rosters here, need to use league id from selected_league
            league_rosters = get_league_rosters(selected_league['league_id'])
            user_roster_info = get_user_roster_info(league_rosters, user_info['user_id'])
            player_data = get_player_info()
            user_roster_players = get_user_roster_players(player_data, user_roster_info)
            projections = get_week_projections('regular', current_state['league_season'], current_state['week'])
            roster_projections = add_projections(user_roster_players, projections)
            roster_with_projected_scores = calculate_projections(roster_projections, selected_league['scoring_settings'])
            if page == 'Home':
                st.markdown("**Your Roster :football::**")
                print_players_projections(roster_with_projected_scores)



        #Start/Sit Advice Page
        if page == 'Start/Sit Advice':
            col1, col2 = st.columns(2)

            with col1:
                #Show max projected lineup
                st.markdown("**Highest Projected Starting Lineup :football:**")
                optimized_projections = optimize_starters_projections(roster_with_projected_scores, selected_league['roster_positions'])
                print_players_projections(optimized_projections)

            with col2:
                #Show expert recommended lineup
                st.write("**Expert Recommended Starting Lineup :football::**")
                format = get_format(selected_league['scoring_settings']['rec'])
                starting_positions = get_starting_positions_set(selected_league)
                position_rankings = get_weekly_rankings(starting_positions, format)
                roster_with_weekly_rankings = add_weekly_rankings(user_roster_players, position_rankings, "fantasy_names.db")
                expert_starting_lineup = optimize_starting_lineup_rankings(roster_with_weekly_rankings, selected_league['roster_positions'])
                print_players_rankings(expert_starting_lineup)

#if options = x, then show this page. Elif...
# go back to youtube video when implementing multiple pages





#use get_user_info(username) and pull up all the leagues
#use st.selectbox to have the user pick which league to look at
#then using that league use get_team_info function/get_league_info function
# have a page where you provide start/sit analysis
# have a page where a user can select another person they want to trade with
# and then they can select players from either side
# and then trade analysis is provided
