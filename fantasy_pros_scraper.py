from bs4 import BeautifulSoup
import requests
import re
import json
import streamlit as st

# Format can be "standard", "half-point-ppr", or "ppr"
# Position can be "rb", "qb", "wr", "te", "k", "flex", or "superflex"
@st.cache_data(show_spinner = False)
def scrape_fantasy_pros(position: str, format: str, ros: str) -> list:
    base_url = "https://www.fantasypros.com/nfl/rankings/"

    if ros == "yes":
        # If ROS is yes
        ros_suffix = "ros-"
        format_suffix = "" if format == "standard" else f"{format}"
        link = f"{base_url}{ros_suffix}{format_suffix}-overall.php"
    else:
        # If ROS is no
        if position.lower() == "qb":
            link = f"{base_url}qb.php"
        elif position.lower() == "k":
          link = f"{base_url}k.php"
        elif position.lower() == "def":
          link = f"{base_url}dst.php"
        else:
          format_suffix = "" if format == "standard" else f"{format}-"
          if position.lower() == "super_flex":
            link = f"{base_url}{format_suffix}{'superflex'}.php"
          else: 
            link = f"{base_url}{format_suffix}{position.lower()}.php"

    results = requests.get(link, timeout=5)
    soup = BeautifulSoup(results.text, "html.parser")

    scripts = soup.find_all("script")
    for script in scripts:
        if script.string:
            ecr = re.search("var ecrData = {.*};", script.string)
            if ecr:
                temp = ecr.group(0).replace("var ecrData = ", "").replace(";", "")
                data = json.loads(temp)
                return data["players"]
            

@st.cache_data(show_spinner = False)
# Get the weekly rankings for each position in a set
def get_weekly_rankings(position_set: set, format: str) -> dict:
    position_rankings = {}

    # Loop through each position in the set
    for position in position_set:
        # Scrape Fantasy Pros rankings for the current position
        rankings = scrape_fantasy_pros(position=position, format=format, ros="no")

        # Store the rankings in the dictionary
        position_rankings[position] = rankings

    return position_rankings