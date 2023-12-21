# FantasyFootballAnalysis
## Overview
Streamlit application where users can input their Sleeper username, and using the Sleeper API, information on their fantasy football teams/leagues is pulled to provide advice on managing their rosters.

### Home Page
The application allows the user to input their username. Once they do that, it pulls information on all the leagues they are in from the API. The user can then select which league they are interested in looking at, and their team roster will be printed on the screen. Using the sidebar, users can navigate to different pages for either start/sit advice or trade analysis.

### Start/Sit Advice
Using the selected league's specific scoring settings, a projected score is calculated and assigned to each player on the user's roster. Then, using the selected league's lineup settings, the starting lineup with the highest possible projection is shown. Additionally, the application scrapes the current expert consensus rankings from [FantasyPros](https://www.fantasypros.com/) and uses those rankings to generate an expert-recommended starting lineup.

### Trade Analysis
On the left side of the screen, the user's roster in a given league is shown, and on the right side of the screen, there is a dropdown menu for the user to select another team from the league to trade with. The user will be able to select players from their team and another team in their league for a potential trade, and the application will provide recommendations concerning whether the trade is likely to benefit the user. The analysis takes rest-of-season expert consensus rankings from [FantasyPros](https://www.fantasypros.com/) into consideration, and it also calculates the net gain/loss in projected points for each team if the trade were to go through.

## How to run the application:
1. Click the green code button and download zipfile
2. Open a terminal/command prompt and navigate to the project folder (FantasyFootballAnalysis)
3. Install "pipenv" if needed
```
pip install pipenv
```
4. Then run the following three statements in order:
```
pipenv install --ignore-pipfile
```
```
pipenv shell
```
```
streamlit run run/website.py
```
5. If you don't have a Sleeper account but would like to test out the webpage, you can use awalker2002 or ianw44.

## More Details on files/functions: 
#### website.py
* Main application file - makes the streamlit website. Uses the functions defined in the other files to conduct analysis and make recommendations. Using the username that a user inputs, it grabs user information. Using the user information, it gathers information on all the leagues that a user is in. The user is then able to select a league, and the application will then calculate projections and scrape rankings for the players on the user's team in the selected league. The home page will contain the user's roster with each player's projected score printed on the screen. The user can use the sidebar to navigate to the Start/Sit Advice page or the Trade Analysis page.
#### data_functions.py
* Contains the functions that grab data from the Sleeper API and make the calculations to conduct analysis. It has the functions to gather all information that is needed for the application (except for the FantasyPros rankings) including user info, league info, team info (for all teams in a league), NFL player info, and projections.
#### fantasy_pros_scraper.py
* Contains the functions that scrape expert rankings from FantasyPros. Can get weekly rankings or rest-of-season rankings. Weekly rankings are gathered individually for each position and rest-of-season rankings are contained in one list with all positions included. Uses the league settings to get the rankings for the correct format (standard, half ppr, or full ppr).
#### streamlit_functions.py
* Contains the functions to display aspects of the streamlit webpage. Functions to print out a list of players with either their projections or rankings displayed. Also contains the functions to create the checkboxes/form to select players on the trade analysis page. Finally, it has functions that analyze a trade based on the players that a user selects and also the functions to print the results of the analysis to the screen.

## Next Steps

I would first like to improve the logic for providing a trade recommendation. While the information that the trade analysis provides can be useful to the user, I ran out of time on the project and was unable to develop a function that provides good recommendations. I need to make significant improvements before the actual recommendation is accurate/useful.\
\
I would also like to improve the speed/efficiency of the application. Once it has the data the application works relatively quickly, but it can take several seconds for the data to load in originally.\
\
Finally, I would like to make the application work for Yahoo and/or ESPN Fantasy users.\
\
**I realized that the data does not update unless you close the application and rerun it from the beginning because the application caches data, so I need to edit my code so that it gets new data if the data it has is too out of date.**
