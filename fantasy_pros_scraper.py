from bs4 import BeautifulSoup
import requests
import re
import json

# Format can be "standard", "half-point-ppr", or "ppr"
# Position can be "rb", "qb", "wr", "te", "k", "flex", or "superflex"
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
        else:
            format_suffix = "" if format == "standard" else f"{format}-"
            link = f"{base_url}{format_suffix}{position}.php"

    results = requests.get(link, timeout=5)
    soup = BeautifulSoup(results.text, "html.parser")

    scripts = soup.find_all("script")
    for script in scripts:
        if script.string:
            z = re.search("var ecrData = {.*};", script.string)
            if z:
                temp = z.group(0).replace("var ecrData = ", "").replace(";", "")
                data = json.loads(temp)
                return data["players"]