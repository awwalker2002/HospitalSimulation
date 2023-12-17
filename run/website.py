import streamlit as st
from api_functions import *
from fantasy_pros_scraper import *
from streamlit_functions import *

class FantasyFootballApp:
    def __init__(self):
        st.set_page_config(layout="wide")
        st.title('Fantasy Football Advice')
        st.markdown('This is an application to provide fantasy football advice to Sleeper Users. Use the sidebar to navigate the webpage.')
        self.sidebar()

    def sidebar(self):
        """
        Allows user to navigate between the three pages
        """
        st.sidebar.title('Navigation')
        self.page = st.sidebar.radio('Pages', options=['Home', 'Start/Sit Advice', 'Trade Analysis'])
        self.common_functionality()

    def common_functionality(self):
        """
        Provides what is to be displayed on all three pages
        """
        # Common functionality to be displayed on every page
        self.username = st.text_input('Enter your Sleeper Username')
        self.user_info = get_user_info(self.username)
        if self.username and self.user_info is None:
            st.write("**Username does not exist**")

        # Get user avatar images
        if self.user_info:
            full_size_image, thumbnail_image = get_avatar_images(self.user_info)
            st.image(thumbnail_image)
        # Pull up leagues so user can pick one 
            self.current_state = get_current_state('nfl')
            self.user_leagues = get_user_leagues(self.user_info['user_id'], self.current_state['league_season'])
            if not self.user_leagues:
                st.write("**User is not in any leagues**")
            else:
                selected_league_name = st.selectbox(label = "Which league would you like to look at?",
                            options = [(league['name']) for league in self.user_leagues])
                if 'selected_league_name' in locals():
                    self.selected_league = get_selected_league_info(self.user_leagues, selected_league_name)
                    # Get league rosters here, need to use league id from selected_league
                    self.league_rosters = get_league_rosters(self.selected_league['league_id'])
                    user_roster_info = get_user_roster_info(self.league_rosters, self.user_info['user_id'])
                    self.player_data = get_player_info()
                    self.user_roster_players = get_user_roster_players(self.player_data, user_roster_info)
                    projections = get_week_projections('regular', self.current_state['league_season'], self.current_state['week'])
                    roster_projections = add_projections(self.user_roster_players, projections)
                    self.roster_with_projected_scores = calculate_projections(roster_projections, self.selected_league['scoring_settings'])
                    self.format = get_format(self.selected_league['scoring_settings']['rec'])
                    self.starting_positions = get_starting_positions_set(self.selected_league)

    def handle_page(self):
        if self.page == 'Home':
            self.home_page()
        elif self.page == 'Start/Sit Advice':
            self.start_sit_page()
        elif self.page == 'Trade Analysis':
            self.trade_analysis_page()

    def home_page(self):
        if self.user_info and self.user_leagues:
            st.markdown("**Your Roster :football::**")
            print_players_projections(self.roster_with_projected_scores)

    def start_sit_page(self):
        """
        Optimizes starting lineup based on both projections and rankings, then prints those optimal starting lineups to the screen
        """
        if self.user_info and self.user_leagues:
            if self.user_info:
                col1, col2 = st.columns(2)

                with col1:
                    # Show max projected lineup
                    st.markdown("**Highest Projected Starting Lineup :football:**")
                    optimized_projections = optimize_starters_projections(self.roster_with_projected_scores, self.selected_league['roster_positions'])
                    print_players_projections(optimized_projections)

                with col2:
                    # Show expert recommended lineup
                    st.write("**Expert Recommended Starting Lineup :football::**")
                    position_rankings = get_weekly_rankings(self.starting_positions, self.format)
                    roster_with_weekly_rankings = add_weekly_rankings(self.user_roster_players, position_rankings, "fantasy_names.db")
                    expert_starting_lineup = optimize_starting_lineup_rankings(roster_with_weekly_rankings, self.selected_league['roster_positions'])
                    print_players_rankings(expert_starting_lineup)

    def trade_analysis_page(self):
        """
        Calculates differences in optimal projections for the rest of the season for each team before and after the trade, also
        calculates the average expert consensus rankings of each side of the trade to make a recommendation.
        """
        if self.user_info and self.user_leagues:
            ros_rankings = scrape_fantasy_pros(position=None, format= self.format, ros="yes")
            user_roster_ros_rankings = add_ros_rankings(self.user_roster_players, ros_rankings, "fantasy_names.db")

            user_selected_players, trade_selected_players, team_to_trade_with, submit_button, trade_ros_rankings = show_trade_form(self.username, self.league_rosters, self.user_info, user_roster_ros_rankings, ros_rankings, self.player_data)

            if submit_button:
                user_difference, trade_difference, user_selected_players, trade_selected_players = analyze_trade(user_roster_ros_rankings, trade_ros_rankings, user_selected_players, trade_selected_players, self.selected_league, self.current_state)
                avg_rank_received, avg_rank_sent = display_trade_results(self.username, user_difference, trade_difference, user_selected_players, trade_selected_players, team_to_trade_with)
                display_trade_decision(user_difference, trade_difference, avg_rank_received, avg_rank_sent)


if __name__ == "__main__":
    app = FantasyFootballApp()
    app.handle_page()
