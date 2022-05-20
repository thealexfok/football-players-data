from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
Leagues={
    "Premier League": "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1",
    "Laliga": "https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1",
    "Serie A": "https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1",
    "Bundesliga": "https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1",
    "Ligue 1": "https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1"
}

def soup_page(url):
    headers = {"User-Agent":
           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15"}
    try:
        page = requests.get(url, headers=headers,timeout=5)
        soup = BeautifulSoup(page.content, "html.parser")
    except requests.ConnectionError as e:
        print("OOPS!! Connection Error. No Internet.\n")
        print(str(e))
    except requests.Timeout as e:
        print("OOPS!! Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        print("OOPS!! General Error")
        print(str(e))
    except KeyboardInterrupt:
        print("Someone closed the program")
    return(soup)

def exportdataframe(list_of_dict,encoding="utf-8-sig"):
    df = pd.DataFrame(list_of_dict)
    print("Exporting... \n")
    df.to_csv("export.csv", index= False, encoding=encoding)
    print("Export successful \n")

def get_teams_url(url):
    soup = soup_page(url)
    team_urls = []
    for item in soup.select("#yw1 .no-border-links a:nth-child(1)"):
        link = item["href"]
        if link != None:
            if ("https://www.transfermarkt.com" + link) not in team_urls:
                team_urls.append("https://www.transfermarkt.com" + link)
    print("Number of teams retrieved:" + str(len(team_urls)))
    return(team_urls)

def get_players_url(url):
    soup = soup_page(url)
    player_urls = []
    for item in soup.select(".nowrap a"):
        link = item["href"]
        if link != None:
            if ("https://www.transfermarkt.com" + link) not in player_urls:
                player_urls.append("https://www.transfermarkt.com" + link)
    print("Number of players retrieved:" + str(len(player_urls)))
    return(player_urls)

def get_players_url_from_league(url):
    teams_url= get_teams_url(url)
    player_urls = []
    for urls in teams_url:
        player_urls.extend(get_players_url(urls))
    return(player_urls)

def get_player_info(url,simple=False):
    soup = soup_page(url)
    player_id = url.split("/")[-1]
    player_name = soup.select(".data-header__headline-wrapper")[0].get_text()[29:].replace("\n", "").strip()
    value = None
    club = None
    DOB = None
    year_of_birth = None
    month_of_birth = None
    day_of_birth = None
    citizenship = None
    position = soup.select(".detail-position__position")[0].get_text()
    otherposition = None
    age = None
    height = None
    foot = "right"
    second_citizenship = None
    try:
        value = soup.select(".tm-player-market-value-development__current-value")[0].get_text().replace("\n", "").replace("â‚¬", "").replace("€","").strip()
        if "m" in value:
            value = int(float(value.replace("m","")) * 1000000)
        elif "Th." in value:
            value = int(value.replace("Th.","")) * 1000
    except:
        pass
    club = soup.select(".info-table__content--flex a+ a")[0].get_text()
    if len(soup.select(".detail-position__position")) > 1:
        otherposition=[]
        for pos in soup.select(".detail-position__position .detail-position__position"):
            otherposition.append(pos.get_text())
    for i in range(len(soup.select(".info-table__content--regular"))+1):
        for item in soup.select(".info-table__content--regular:nth-child("+str(i)+")"):
            rowname = item.get_text()
            tempvalue = soup.select(".info-table__content--bold:nth-child("+str(i+1)+")")[0].get_text()
            if rowname == "Age:":
                age = tempvalue
            if rowname == "Height:":
                height = int(float(tempvalue.replace("m", "").replace(",", "."))*100)
            if rowname == "Date of birth:":
                DOB=tempvalue
            if rowname == "Foot:":
                foot = tempvalue
            if rowname == "Citizenship:":
                citizenship = soup.select(".info-table__content--bold:nth-child("+str(i+1)+")")[0].select("img")[0]["alt"]
                no_of_citizenships = len(soup.select(".info-table__content--bold:nth-child("+str(i+1)+")")[0].select("img"))
                if no_of_citizenships > 1:
                    second_citizenship = soup.select(".info-table__content--bold:nth-child("+str(i+1)+")")[0].select("img")[1]["alt"]
                
    if DOB != None:
        DOB = DOB.replace(",", "")
        year_of_birth = int(datetime.datetime.strptime(DOB.split(" ")[2], "%Y").year)
        month_of_birth = int(datetime.datetime.strptime(DOB.split(" ")[0], "%b").month)
        day_of_birth = int(datetime.datetime.strptime(DOB.split(" ")[1], "%d").day)
        DOB = str(year_of_birth) + "-" + str(month_of_birth) + "-" + str(day_of_birth)

    if simple:
        biodict = {
        "player_name": player_name,
        "position": position,
        "value": value,
        "club": club
        }
        return(biodict)
    biodict = {
        "player_id": player_id,
        "player_name": player_name,
        "value": value,
        "club": club,
        "age": age,
        "day_of_birth": day_of_birth,
        "month_of_birth": month_of_birth,
        "year_of_birth": year_of_birth,
        "citizenship": citizenship,
        "dob": DOB,
        "position": position,
        "other_position": otherposition,
        "height": height,
        "foot": foot,
        "second_citizenship": second_citizenship
    }

    return(biodict)

def get_players_info_from_league(url):
    playersurl = get_players_url_from_league(url)
    playerlist = []
    for link in playersurl:
        current_player_info = get_player_info(link)
        print("Adding "+current_player_info["player_name"]+" from " +current_player_info["club"])
        playerlist.append(current_player_info)
        print("Number of Players: " + str(len(playerlist)))
    return playerlist

#exportdataframe(get_players_info_from_league(Leagues["Premier League"]))

