from riotwatcher import LolWatcher, RiotWatcher, ApiError
from match_data import MatchData, TeamData, PlayerData
import time

class RawDataScraper:
    def __init__(self, apikey:str):
        self.riotWatcher = RiotWatcher(apikey)
        self.lolWatcher = LolWatcher(apikey)
        self.rate_sec:int = 0
        self.rate_min:int = 0

    def api_rate_limit(self):
        self.rate_sec += 1
        self.rate_min += 1
        if self.rate_sec > 20:
            print("Sec limit reached waiting 2 seconds")
            time.sleep(2)
            self.rate_sec = 0
        if self.rate_min > 100:
            print("Min limit reached waiting 2 minutes")
            time.sleep(121)
            self.rate_min = 0   

    def get_champ_id_name(self):
        game_version = self.lolWatcher.data_dragon.versions_for_region('eune')
        champions_version = game_version['n']['champion']
        champions_dict:dict = self.lolWatcher.data_dragon.champions(champions_version, full=True)['keys']
        filepath = f"D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\LeagueAssets\\ChampIdAndName.csv"
        with open(filepath, 'w') as file:
            file.write("ID,Name\n")
        with open(filepath, 'a') as file:
            for key, value in champions_dict.items():
                if value == "MonkeyKing":
                    file.write(f"{key},{"Wukong"}\n")
                else:
                    file.write(f"{key},{value}\n")
        print("ChampIdAndName file is complete")

    def get_item_id_price(self):
        game_version = self.lolWatcher.data_dragon.versions_for_region('eune')
        item_version = game_version['n']['item']
        item_dict:dict = self.lolWatcher.data_dragon.items(item_version)
        data:dict = item_dict['data']
        filepath = f"D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\LeagueAssets\\ItemIdNameGold.csv"
        with open(filepath, 'w') as file:
            file.write("ID;Name;Gold\n")
        with open(filepath, 'a') as file:
            for key, value in data.items():
                if bool(value['maps']['11']):
                        file.write(f"{key};{value['name']};{value['gold']['total']}\n")
        print("Item CVS file is complete!")
            

    def scrape_ranked_data_from_api(self, dataNumber: int, fileName: str, playerName: str, playerTag: str):
        try:
            filepath = f"D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\League_Match_Data\\{fileName}.csv"
            if not os.path.exists(filepath):
                with open(filepath, 'x') as file:
                    file.write("GameVersion,"
                               +"GameDuration,"
                               +"BlueTeamWin,"
                               +"BlueTeamKills,"
                               +"BlueTeamGoldSpent,"
                               +"BlueTeamTowersTaken,"
                               +"BlueTeamInhibitorsTaken,"
                               +"BlueTeamDragonsTaken,"
                               +"BlueTeamGrubsTaken,"
                               +"BlueTeamRiftheraldTaken,"
                               +"BlueTeamBaronTaken,")
                    for i in range(1, 6):
                        file.write(f"BluePlayer{i}Role,"
                                   +f"BluePlayer{i}ChampionId,"
                                   +f"BluePlayer{i}ChampionName,"
                                   +f"BluePlayer{i}GoldSpent,"
                                   +f"BluePlayer{i}Level,"
                                   +f"BluePlayer{i}Kills,"
                                   +f"BluePlayer{i}Deaths,"
                                   +f"BluePlayer{i}Assists,"
                                   +f"BluePlayer{i}CreepScore,"
                                   +f"BluePlayer{i}WardScore,")
                    file.write("RedTeamWin,"
                               +"RedTeamKills,"
                               +"RedTeamGoldSpent,"
                               +"RedTeamTowersTaken,"
                               +"RedTeamInhibitorsTaken,"
                               +"RedTeamDragonsTaken,"
                               +"RedTeamGrubsTaken,"
                               +"RedTeamRiftheraldTaken,"
                               +"RedTeamBaronTaken,")
                    for i in range(1, 6):
                        file.write(f"RedPlayer{i}Role,"
                                   +f"RedPlayer{i}ChampionId,"
                                   +f"RedPlayer{i}ChampionName,"
                                   +f"RedPlayer{i}GoldSpent,"
                                   +f"RedPlayer{i}Level,"
                                   +f"RedPlayer{i}Kills,"
                                   +f"RedPlayer{i}Deaths,"
                                   +f"RedPlayer{i}Assists,"
                                   +f"RedPlayer{i}CreepScore,"
                                   +f"RedPlayer{i}WardScore,")
                    file.write("\n") 

            my_puuid = self.riotWatcher.account.by_riot_id("EUROPE", playerName, playerTag)['puuid']
            puuid_stack = [my_puuid]
            puuid_set = set({my_puuid})

            ranked_match_id_set = set()

            data_count = 0
            
            while data_count < dataNumber and len(puuid_stack) != 0:
                current_puuid = puuid_stack.pop()

                ranked_match_ids = self.lolWatcher.match.matchlist_by_puuid("EUROPE", current_puuid, None, 20, None, "ranked", None, None)

                ranked_match_list: list[MatchData] = []
        
                for matchId in ranked_match_ids:  
                    if not ranked_match_id_set.__contains__(matchId):
                        ranked_match_id_set.add(matchId)

                        ranked_match = self.lolWatcher.match.by_id("EUROPE", matchId)

                        match_details = ranked_match['info']
                        game_version_tmp = match_details['gameVersion'].split(".")[0:2]

                        if match_details['gameEndTimestamp'] != None and match_details['gameDuration'] > 900 and int(game_version_tmp[0]) == 16 and int(game_version_tmp[1]) > 0:

                            players_puuids = ranked_match['metadata']['participants']
                            for player_puuid in players_puuids:
                                if not puuid_set.__contains__(player_puuid):
                                    puuid_stack.append(player_puuid)
                                    puuid_set.add(player_puuid)
                            
                            participants = match_details['participants']
                            players:list[PlayerData] = []
                            for participant in participants:
                                players.append(PlayerData(participant['individualPosition'], 
                                                          participant['championId'],
                                                          participant['championName'],
                                                          participant['goldSpent'],
                                                          participant['champLevel'],
                                                          participant['kills'],
                                                          participant['deaths'],
                                                          participant['assists'],
                                                          (participant['wardsKilled'] + participant['totalMinionsKilled'] + participant['totalAllyJungleMinionsKilled'] + participant['totalEnemyJungleMinionsKilled']),
                                                          participant['visionScore']))

                            match_teams = match_details['teams']
                            match_blue_team = match_teams[0]
                            match_red_team = match_teams[1]
                            
                            blue_team = TeamData(players[0:5],
                                                 int(match_blue_team['win']),
                                                 match_blue_team['objectives']['tower']['kills'],
                                                 match_blue_team['objectives']['inhibitor']['kills'],
                                                 match_blue_team['objectives']['dragon']['kills'],
                                                 match_blue_team['objectives']['horde']['kills'],
                                                 match_blue_team['objectives']['riftHerald']['kills'],
                                                 match_blue_team['objectives']['baron']['kills'])
                            
                            red_team = TeamData(players[5:10],
                                                 int(match_red_team['win']),
                                                 match_red_team['objectives']['tower']['kills'],
                                                 match_red_team['objectives']['inhibitor']['kills'],
                                                 match_red_team['objectives']['dragon']['kills'],
                                                 match_red_team['objectives']['horde']['kills'],
                                                 match_red_team['objectives']['riftHerald']['kills'],
                                                 match_red_team['objectives']['baron']['kills'])
                            
                            current_match_data = MatchData(match_details['gameVersion'],
                                                           match_details['gameDuration'],
                                                           blue_team,
                                                           red_team) 
                            
                            ranked_match_list.append(current_match_data)

                with open(filepath, 'a') as file:
                    for w_match in ranked_match_list:
                        file.write(w_match.game_version+","
                                    +str(w_match.game_duration)+","
                                    +str(w_match.blue_team.win)+","
                                    +str(w_match.blue_team.team_kills)+","
                                    +str(w_match.blue_team.team_gold_spent)+","
                                    +str(w_match.blue_team.towers_taken)+","
                                    +str(w_match.blue_team.inhibitors_taken)+","
                                    +str(w_match.blue_team.dragons_taken)+","
                                    +str(w_match.blue_team.grubs_taken)+","
                                    +str(w_match.blue_team.riftherald_taken)+","
                                    +str(w_match.blue_team.baron_taken)+",")
                        for w_player in w_match.blue_team.players:
                            file.write(w_player.role+","
                                        +str(w_player.champ_id)+","
                                        +w_player.champ_name+","
                                        +str(w_player.gold_spent)+","
                                        +str(w_player.level)+","
                                        +str(w_player.kills)+","
                                        +str(w_player.deaths)+","
                                        +str(w_player.assists)+","
                                        +str(w_player.creepscore)+","
                                        +str(w_player.wardscore)+",")
                        file.write(str(w_match.red_team.win)+","
                                    +str(w_match.red_team.team_kills)+","
                                    +str(w_match.red_team.team_gold_spent)+","
                                    +str(w_match.red_team.towers_taken)+","
                                    +str(w_match.red_team.inhibitors_taken)+","
                                    +str(w_match.red_team.dragons_taken)+","
                                    +str(w_match.red_team.grubs_taken)+","
                                    +str(w_match.red_team.riftherald_taken)+","
                                    +str(w_match.red_team.baron_taken)+",")
                        for w_player in w_match.red_team.players:
                            file.write(w_player.role+","
                                        +str(w_player.champ_id)+","
                                        +w_player.champ_name+","
                                        +str(w_player.gold_spent)+","
                                        +str(w_player.level)+","
                                        +str(w_player.kills)+","
                                        +str(w_player.deaths)+","
                                        +str(w_player.assists)+","
                                        +str(w_player.creepscore)+","
                                        +str(w_player.wardscore)+",")
                        file.write("\n") 

                data_count += len(ranked_match_list)
                print(f"Data count: {data_count}")
                    
        except ApiError as err:
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
                print('this retry-after is handled by default by the RiotWatcher library')
                print('future requests wait until the retry-after time passes')
                return
            elif err.response.status_code == 404:
                print('Request cannot be found')
                return
            else:
                raise

    def api_test(self):
        try:
            self.api_rate_limit()
            my_puuid = self.riotWatcher.account.by_riot_id("EUROPE", "", "")['puuid']
            
            print(my_puuid)
        except ApiError as err:
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
                print('this retry-after is handled by default by the RiotWatcher library')
                print('future requests wait until the retry-after time passes')
                return
            elif err.response.status_code == 404:
                print('Request cannot be found')
                return
            else:
                raise

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    scraper = RawDataScraper(os.getenv('API_KEY'))
    scraper.get_champ_id_name()
    scraper.get_item_id_price()
    scraper.scrape_ranked_data_from_api(10000, "2026_01_09_23_00", "", "")
    
