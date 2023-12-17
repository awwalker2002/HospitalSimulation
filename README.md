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
## Next Steps

I would first like to improve the logic for providing a trade recommendation. While the information that the trade analysis provides can be useful to the user, I ran out of time on the project and was unable to develop a function that provides good recommendations. I need to make significant improvements before the actual recommendation is accurate/useful.\
\
I would also like to improve the speed/efficiency of the application. Once it has the data the application works relatively quickly, but it can take several seconds for the data to load in originally.\
\
Finally, I would like to make the application work for Yahoo and/or ESPN Fantasy users.

