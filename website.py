import streamlit as st
from api_functions import *
from fantasy_pros_scraper import *
from streamlit_functions import *


# Start of webpage
st.set_page_config(layout="wide")
st.title('Fantasy Football Advice')
st.markdown('This is an application to provide fantasy football advice \
            to Sleeper Users. Use the sidebar to navigate the webpage.')
st.sidebar.title('Navigation')
page = st.sidebar.radio('Pages', options = ['Home', 'Start/Sit Advice', 'Trade Analysis'])


# Get user info from inputted username
username = st.text_input('Enter your Sleeper Username')
user_info = get_user_info(username)
if username and user_info is None:
    st.write("**Username does not exist**")

# Get user avatar images
if user_info:
    full_size_image, thumbnail_image = get_avatar_images(user_info)
    st.image(thumbnail_image)
# Pull up leagues so user can pick one 
    current_state = get_current_state('nfl')
    user_leagues = get_user_leagues(user_info['user_id'], current_state['league_season'])
    if not user_leagues:
        st.write("**User is not in any leagues**")
    else:
        selected_league = st.selectbox(label = "Which league would you like to look at?",
                    options = [(league['name']) for league in user_leagues])

    # Once user selects league, show their roster with projections
        if 'selected_league' in locals():
            selected_league = get_selected_league_info(user_leagues, selected_league)
            # Get league rosters here, need to use league id from selected_league
            league_rosters = get_league_rosters(selected_league['league_id'])
            user_roster_info = get_user_roster_info(league_rosters, user_info['user_id'])
            player_data = get_player_info()
            user_roster_players = get_user_roster_players(player_data, user_roster_info)
            projections = get_week_projections('regular', current_state['league_season'], current_state['week'])
            roster_projections = add_projections(user_roster_players, projections)
            roster_with_projected_scores = calculate_projections(roster_projections, selected_league['scoring_settings'])
            format = get_format(selected_league['scoring_settings']['rec'])
            starting_positions = get_starting_positions_set(selected_league)
            if page == 'Home':
                st.markdown("**Your Roster :football::**")
                print_players_projections(roster_with_projected_scores)



        # Start/Sit Advice Page
        if page == 'Start/Sit Advice':
            col1, col2 = st.columns(2)

            with col1:
                # Show max projected lineup
                st.markdown("**Highest Projected Starting Lineup :football:**")
                optimized_projections = optimize_starters_projections(roster_with_projected_scores, selected_league['roster_positions'])
                print_players_projections(optimized_projections)

            with col2:
                # Show expert recommended lineup
                st.write("**Expert Recommended Starting Lineup :football::**")
                format = get_format(selected_league['scoring_settings']['rec'])
                starting_positions = get_starting_positions_set(selected_league)
                position_rankings = get_weekly_rankings(starting_positions, format)
                roster_with_weekly_rankings = add_weekly_rankings(user_roster_players, position_rankings, "fantasy_names.db")
                expert_starting_lineup = optimize_starting_lineup_rankings(roster_with_weekly_rankings, selected_league['roster_positions'])
                print_players_rankings(expert_starting_lineup)


        if page == 'Trade Analysis':
            col1, col2, = st.columns(2)
            ros_rankings = scrape_fantasy_pros(position = None, format = format, ros = "yes")
            user_selected_players = []
            trade_selected_players = []
            user_roster_ros_rankings = add_ros_rankings(user_roster_players, ros_rankings, "fantasy_names.db")
            with st.form("Trade Analyzer"):
                with col1:
                    user_team = st.selectbox("**Your Roster :football::**", options = [username])
                    user_selected_players = checkbox_players(user_roster_ros_rankings)

                with col2:
                    other_league_usernames = get_other_league_usernames(league_rosters, user_info)
                    team_to_trade_with = st.selectbox("**Select a user to trade with :football::**", options = other_league_usernames.values())
                    if team_to_trade_with:
                        trade_user_id = next((user_id for user_id, username in other_league_usernames.items() if username == team_to_trade_with), None)
                        # now need to get the roster with projections and all that?
                        trade_roster_info = get_user_roster_info(league_rosters, trade_user_id)
                        trade_roster_players = get_user_roster_players(player_data, trade_roster_info)
                        # now add ros rankings to trade roster
                        trade_ros_rankings = add_ros_rankings(trade_roster_players, ros_rankings, "fantasy_names.db")
                        trade_selected_players = checkbox_players(trade_ros_rankings)

                
                submit_button = st.form_submit_button("Analyze Trade")
    

            if submit_button:
                end_week = get_end_week(selected_league)
                # user_selected_players # has all player info
                # trade_selected_players # has player info
                user_roster_after, trade_roster_after = swap_players(user_roster_ros_rankings, trade_ros_rankings, user_selected_players, trade_selected_players)
                user_difference, trade_difference = calculate_total_projection_differences(user_roster_ros_rankings, user_roster_after, trade_ros_rankings, trade_roster_after, current_state['league_season'], current_state['week'], end_week, selected_league)
                
                col1, col2 = st.columns(2)
                with col1:
                    trend_emoji = ":chart_with_downwards_trend:" if user_difference < 0 else ":chart_with_upwards_trend:"
                    st.write(f"**Net Change In Points for {username}:** {user_difference} {trend_emoji}")
                    st.write("Players Received:")
                    for player in trade_selected_players:
                        st.write(f"- {player['full_name'] if player['full_name'] else player['player_id']} ({', '.join(player['fantasy_positions'])}) - Expert ROS Ranking: {player['ros_ecr_ranking']}")
                    avg_rank_receieved = calculate_average_rankings(trade_selected_players)
                    

                with col2:
                    trend_emoji2 = ":chart_with_downwards_trend:" if trade_difference < 0 else ":chart_with_upwards_trend:"
                    st.write(f"**Net Change In Points for {team_to_trade_with}:** {trade_difference} {trend_emoji2}")
                    st.write("Players Traded Away:")
                    for player in user_selected_players:
                        st.write(f"- {player['full_name'] if player['full_name'] else player['player_id']} ({', '.join(player['fantasy_positions'])}) - Expert ROS Ranking: {player['ros_ecr_ranking']}")
                    avg_rank_sent = calculate_average_rankings(user_selected_players)
                
                if ((user_difference > 0) and (avg_rank_receieved < avg_rank_sent)):
                    st.header("This trade is likely to benefit your team! :100:")
                elif ((user_difference < 0) and (avg_rank_receieved > avg_rank_sent)):
                    st.header("This trade is unlikely to benefit your team :cry:")
                else:
                    st.header("This is a fairly even trade. Make the decision that you feel is best :shrug:")
                
# MAYBE CHANGE LOGIC SO THAT IT TAKES INTO ACCOUNT BEST RANKING AS WELL
# FIXED BELOW ERROR
# ERROR IS WHEN THERE ARE NO PLAYERS LEFT FOR A CERTAIN POSITION ON A ROSTER

                
