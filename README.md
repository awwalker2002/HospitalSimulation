# FantasyFootballAnalysis
Goal is to create an application where users can input their Sleeper (fantasy football platform) username, and the application will pull up their team(s)/league(s) info and provide information such as start/sit recommendations, trade analysis, etc. 
Will use player data collected from [Fantasy Pros](https://www.fantasypros.com/nfl/rankings/ros-overall.php) and [ProFootballReference](https://www.pro-football-reference.com/years/2023/fantasy.htm) and will use the [Sleeper API](https://docs.sleeper.com/) to pull all user info, including the leagues they are in, all team rosters in those leagues, league standings, points scored, etc.
\
\
The application will prompt the user to input their username. Once they do that, it will pull the information on all the leagues they are in from the API. The user will then select which league they are interested in looking at, and their team info will be pulled from the API. Using projections and team roster data, the application will provide a recommended optimal starting lineup. The user will also be able to input potential trades and be provided with an analysis of the trade that includes projections before and after the trade, calculated values for each player in the trade, etc.

