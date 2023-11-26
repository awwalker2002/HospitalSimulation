# FantasyFootballAnalysis
Streamlit application where users can input their Sleeper username, and using the Sleeper API, information on their fantasy football teams/leagues is pulled to provide advice on how to manage their rosters.

## Home Page
The application will prompt the user to input their username. Once they do that, it will pull in information on all the leagues they are a part of from the API. The user will then select which league they are interested in looking at, and their team roster will be printed on the screen. Using the sidebar, users can navigate to different pages for either start/sit advice or trade analysis.

## Start/Sit Advice
Using the selected league's specific scoring settings, a projected score will be calculated and assigned to each player on the user's roster. Then, using the selected league's lineup settings, the starting lineup with the highest possible projection will be shown. Additionally, the application will scrape the current expert consensus rankings from [FantasyPros](https://www.fantasypros.com/) and use those rankings to generate an expert-recommended starting lineup.

## Trade Analysis
On the left side of the screen, there will be the user's roster in a given league, and on the right side of the screen, there will be a dropdown menu for the user to select another team from the league to look at. The user will be able to select players from their own team and another team in their league for a potential trade, and the application will provide recommendations on whether the trade benefits the user or not. The analysis will take rest-of-season expert consensus rankings from [FantasyPros](https://www.fantasypros.com/) into consideration, and it will also calculate the net gain/loss in projected points for each team if the trade were to go through. I am also considering scraping information from fantasy football trade value charts to include in the trade analysis.


