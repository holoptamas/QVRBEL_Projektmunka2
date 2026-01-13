import requests
import match_data
import pandas as pd

class GameClientApiDataRetriever:
    def __init__(self):
        self.base_url = "https://127.0.0.1:2999/liveclientdata/allgamedata"
        self.game_client_data: match_data.GameClientMatchData
        self.champ_id_df = pd.read_csv("D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\LeagueAssets\\ChampIdAndName.csv")
        self.item_id_df = pd.read_csv("D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\LeagueAssets\\ItemIdNameGold.csv", sep=";")

    def data_tester(self):
        response = requests.get(self.base_url, verify=False)
        if response.status_code == 200:
            lol_data = response.json()
            self.raw_match_data(lol_data)
            print("Wow it worked!")
        else:
            print("Rip")

    def write_match_data(self):
        print(f"Current match time: {self.game_client_data.game_duration}")
        print(f"---Blue Team---")
        print(f"Total kills: {self.game_client_data.blue_team.team_kills} | Gold spent: {self.game_client_data.blue_team.team_gold_spent}")
        print(f"Objectives: Towers taken: {self.game_client_data.blue_team.towers_taken} | Inhibitors taken: {self.game_client_data.blue_team.inhibitors_taken} | Dragons slain: {self.game_client_data.blue_team.dragons_taken} | Void Grubs slain: {self.game_client_data.blue_team.grubs_taken} | Rift Herald slain: {self.game_client_data.blue_team.riftherald_taken} | Baron slain: {self.game_client_data.blue_team.baron_taken}")
        for player in self.game_client_data.blue_team.players:
            print(f"{player.role}: Champion: {player.champ_name} | Level: {player.level} | Gold spent: {player.gold_spent} | Kills: {player.kills} | Deaths: {player.deaths} | Assists: {player.assists} | Creep score: {player.creepscore} | Ward score: {player.wardscore}")
        print("")
        print(f"---Red Team---")
        print(f"Total kills: {self.game_client_data.red_team.team_kills} | Gold spent: {self.game_client_data.red_team.team_gold_spent}")
        print(f"Objectives: Towers taken: {self.game_client_data.red_team.towers_taken} | Inhibitors taken: {self.game_client_data.red_team.inhibitors_taken} | Dragons slain: {self.game_client_data.red_team.dragons_taken} | Void Grubs slain: {self.game_client_data.red_team.grubs_taken} | Rift Herald slain: {self.game_client_data.red_team.riftherald_taken} | Baron slain: {self.game_client_data.red_team.baron_taken}")
        for player in self.game_client_data.red_team.players:
            print(f"{player.role}: Champion: {player.champ_name} | Level: {player.level} | Gold spent: {player.gold_spent} | Kills: {player.kills} | Deaths: {player.deaths} | Assists: {player.assists} | Creep score: {player.creepscore} | Ward score: {player.wardscore}")
        print("")

    def raw_match_data(self, lol_data:dict):
        all_player_data = lol_data['allPlayers']
        events_data = lol_data['events']['Events']
        game_data = lol_data['gameData']

        blue_players = ["","","","",""]
        red_players = ["","","","",""]
        blue_player_names = ["","","","",""]
        red_player_names = ["","","","",""]

        for player in all_player_data:
            champion_name = player['championName']
            split_name1 = champion_name.split(" ")
            split_name2 = champion_name.split("\'")
            split_name3 = champion_name.split(". ")

            if len(split_name3) == 2:
                champion_Id = self.champ_id_df[self.champ_id_df['Name'] == split_name3[0] + split_name3[1]]['ID']
            elif len(split_name2) == 2 :
                champion_Id = self.champ_id_df[self.champ_id_df['Name'] == (split_name2[0] + split_name2[1]).capitalize()]['ID'] 
            elif len(split_name1) == 2:
                champion_Id = self.champ_id_df[self.champ_id_df['Name'] == split_name1[0] + split_name1[1]]['ID'] 
            else:
                champion_Id = self.champ_id_df[self.champ_id_df['Name'] == champion_name]['ID']

            gold_spent = 0
            items = player['items']
            for item in items:
                curr_item_gold = self.item_id_df[self.item_id_df['ID'] == item['itemID']]['Gold']
                gold_spent += int(curr_item_gold.iloc[0])

            scores = player['scores']
            current_player = match_data.GameClientPlayerData(player['riotIdGameName'],
                                                             player['position'],
                                                             int(champion_Id.iloc[0]),
                                                             player['championName'],
                                                             gold_spent,
                                                             int(player['level']),
                                                             int(scores['kills']), 
                                                             int(scores['deaths']),
                                                             int(scores['assists']),
                                                             int(scores['creepScore']),
                                                             int(scores['wardScore']))
            if player['team'] == "ORDER":
                if current_player.role == "TOP":
                    blue_players[0] = current_player
                    blue_player_names[0] = current_player.player_name

                    if player['isBot'] == True:
                        blue_player_names[0] = blue_player_names[0] + " Bot"

                elif current_player.role == "JUNGLE":
                    blue_players[1] = current_player
                    blue_player_names[1] = current_player.player_name

                    if player['isBot'] == True:
                        blue_player_names[1] = blue_player_names[1] + " Bot"

                elif current_player.role == "MIDDLE":
                    blue_players[2] = current_player
                    blue_player_names[2] = current_player.player_name

                    if player['isBot'] == True:
                        blue_player_names[2] = blue_player_names[2] + " Bot"

                elif current_player.role == "BOTTOM":
                    blue_players[3] = current_player
                    blue_player_names[3] = current_player.player_name

                    if player['isBot'] == True:
                        blue_player_names[3] = blue_player_names[3] + " Bot"

                elif current_player.role == "SUPPORT":
                    blue_players[4] = current_player
                    blue_player_names[4] = current_player.player_name

                    if player['isBot'] == True:
                        blue_player_names[4] = blue_player_names[4] + " Bot"

            else:
                if current_player.role == "TOP":
                    red_players[0] = current_player
                    red_player_names[0] = current_player.player_name

                    if player['isBot'] == True:
                        red_player_names[0] = red_player_names[0] + " Bot"

                elif current_player.role == "JUNGLE":
                    red_players[1] = current_player
                    red_player_names[1] = current_player.player_name

                    if player['isBot'] == True:
                        red_player_names[1] = red_player_names[1] + " Bot"

                elif current_player.role == "MIDDLE":
                    red_players[2] = current_player
                    red_player_names[2] = current_player.player_name

                    if player['isBot'] == True:
                        red_player_names[2] = red_player_names[2] + " Bot"

                elif current_player.role == "BOTTOM":
                    red_players[3] = current_player
                    red_player_names[3] = current_player.player_name

                    if player['isBot'] == True:
                        red_player_names[3] = red_player_names[3] + " Bot"

                elif current_player.role == "SUPPORT":
                    red_players[4] = current_player
                    red_player_names[4] = current_player.player_name

                    if player['isBot'] == True:
                        red_player_names[4] = red_player_names[4] + " Bot"

        blue_towers = 0
        blue_inhibs = 0
        blue_dragons = 0
        blue_grubs = 0
        blue_riftherald = 0
        blue_atakhan = 0
        blue_baron = 0

        red_towers = 0
        red_inhibs = 0
        red_dragons = 0
        red_grubs = 0
        red_riftherald = 0
        red_atakhan = 0
        red_baron = 0

        for event in events_data:
            if event['EventID'] > 2:
                if event['EventName'] != "FirstBlood":
                    if event['EventName'] != "Ace":
                        if blue_player_names.__contains__(event['KillerName']):
                            if event['EventName'] == "HordeKill":
                                blue_grubs += 1
                            elif event['EventName'] == "DragonKill":
                                blue_dragons += 1
                            elif event['EventName'] == "HeraldKill":
                                blue_riftherald += 1
                            elif event['EventName'] == "TurretKilled":
                                blue_towers += 1
                            elif event['EventName'] == "AtakhanKilled":
                                blue_atakhan += 1
                            elif event['EventName'] == "BaronKill":
                                blue_baron += 1
                            elif event['EventName'] == "InhibKilled":
                                blue_inhibs += 1
                        elif red_player_names.__contains__(event['KillerName']):
                            if event['EventName'] == "HordeKill":
                                red_grubs += 1
                            elif event['EventName'] == "DragonKill":
                                red_dragons += 1
                            elif event['EventName'] == "HeraldKill":
                                red_riftherald += 1
                            elif event['EventName'] == "TurretKilled":
                                red_towers += 1
                            elif event['EventName'] == "BaronKill":
                                red_baron += 1
                            elif event['EventName'] == "AtakhanKilled":
                                red_atakhan += 1
                            elif event['EventName'] == "InhibKilled":
                                red_inhibs += 1

        blue_team = match_data.GameClientTeamData(blue_players, blue_towers, blue_inhibs, blue_dragons, blue_grubs, blue_riftherald, blue_atakhan, blue_baron, 0)
        red_team = match_data.GameClientTeamData(red_players, red_towers, red_inhibs, red_dragons, red_grubs, red_riftherald, red_atakhan, red_baron, 0)

        game_time:float = game_data['gameTime']

        self.game_client_data = match_data.GameClientMatchData(game_time.__round__(), blue_team, red_team)

    def match_data_to_df(self):
        data = {"GameDuration": self.game_client_data.game_duration,
                "BlueTeamKills": self.game_client_data.blue_team.team_kills,
                "BlueTeamGoldSpent": self.game_client_data.blue_team.team_gold_spent,
                "BlueTeamTowersTaken": self.game_client_data.blue_team.towers_taken,
                "BlueTeamInhibitorsTaken": self.game_client_data.blue_team.inhibitors_taken,
                "BlueTeamDragonsTaken": self.game_client_data.blue_team.dragons_taken,
                "BlueTeamGrubsTaken": self.game_client_data.blue_team.grubs_taken,
                "BlueTeamRiftheraldTaken": self.game_client_data.blue_team.riftherald_taken,
                "BlueTeamAtakhanTaken": self.game_client_data.red_team.atakhan_taken,
                "BlueTeamBaronTaken": self.game_client_data.blue_team.baron_taken,
                "BlueTeamFeats": self.game_client_data.blue_team.feats,
                "BluePlayer1Role": self.game_client_data.blue_team.players[0].role,
                "BluePlayer1ChampionId": self.game_client_data.blue_team.players[0].champ_id,
                "BluePlayer1GoldSpent": self.game_client_data.blue_team.players[0].gold_spent,
                "BluePlayer1Level": self.game_client_data.blue_team.players[0].level,
                "BluePlayer1Kills": self.game_client_data.blue_team.players[0].kills,
                "BluePlayer1Deaths": self.game_client_data.blue_team.players[0].deaths,
                "BluePlayer1Assists": self.game_client_data.blue_team.players[0].assists,
                "BluePlayer1CreepScore": self.game_client_data.blue_team.players[0].creepscore,
                "BluePlayer1WardScore": self.game_client_data.blue_team.players[0].wardscore,
                "BluePlayer2Role": self.game_client_data.blue_team.players[1].role,
                "BluePlayer2ChampionId": self.game_client_data.blue_team.players[1].champ_id,
                "BluePlayer2GoldSpent": self.game_client_data.blue_team.players[1].gold_spent,
                "BluePlayer2Level": self.game_client_data.blue_team.players[1].level,
                "BluePlayer2Kills": self.game_client_data.blue_team.players[1].kills,
                "BluePlayer2Deaths": self.game_client_data.blue_team.players[1].deaths,
                "BluePlayer2Assists": self.game_client_data.blue_team.players[1].assists,
                "BluePlayer2CreepScore": self.game_client_data.blue_team.players[1].creepscore,
                "BluePlayer2WardScore": self.game_client_data.blue_team.players[1].wardscore,
                "BluePlayer3Role": self.game_client_data.blue_team.players[2].role,
                "BluePlayer3ChampionId": self.game_client_data.blue_team.players[2].champ_id,
                "BluePlayer3GoldSpent": self.game_client_data.blue_team.players[2].gold_spent,
                "BluePlayer3Level": self.game_client_data.blue_team.players[2].level,
                "BluePlayer3Kills": self.game_client_data.blue_team.players[2].kills,
                "BluePlayer3Deaths": self.game_client_data.blue_team.players[2].deaths,
                "BluePlayer3Assists": self.game_client_data.blue_team.players[2].assists,
                "BluePlayer3CreepScore": self.game_client_data.blue_team.players[2].creepscore,
                "BluePlayer3WardScore": self.game_client_data.blue_team.players[2].wardscore,
                "BluePlayer4Role": self.game_client_data.blue_team.players[3].role,
                "BluePlayer4ChampionId": self.game_client_data.blue_team.players[3].champ_id,
                "BluePlayer4GoldSpent": self.game_client_data.blue_team.players[3].gold_spent,
                "BluePlayer4Level": self.game_client_data.blue_team.players[3].level,
                "BluePlayer4Kills": self.game_client_data.blue_team.players[3].kills,
                "BluePlayer4Deaths": self.game_client_data.blue_team.players[3].deaths,
                "BluePlayer4Assists": self.game_client_data.blue_team.players[3].assists,
                "BluePlayer4CreepScore": self.game_client_data.blue_team.players[3].creepscore,
                "BluePlayer4WardScore": self.game_client_data.blue_team.players[3].wardscore,
                "BluePlayer5Role": self.game_client_data.blue_team.players[4].role,
                "BluePlayer5ChampionId": self.game_client_data.blue_team.players[4].champ_id,
                "BluePlayer5GoldSpent": self.game_client_data.blue_team.players[4].gold_spent,
                "BluePlayer5Level": self.game_client_data.blue_team.players[4].level,
                "BluePlayer5Kills": self.game_client_data.blue_team.players[4].kills,
                "BluePlayer5Deaths": self.game_client_data.blue_team.players[4].deaths,
                "BluePlayer5Assists": self.game_client_data.blue_team.players[4].assists,
                "BluePlayer5CreepScore": self.game_client_data.blue_team.players[4].creepscore,
                "BluePlayer5WardScore": self.game_client_data.blue_team.players[4].wardscore,
                "RedTeamKills": self.game_client_data.red_team.team_kills,
                "RedTeamGoldSpent": self.game_client_data.red_team.team_gold_spent,
                "RedTeamTowersTaken": self.game_client_data.red_team.towers_taken,
                "RedTeamInhibitorsTaken": self.game_client_data.red_team.inhibitors_taken,
                "RedTeamDragonsTaken": self.game_client_data.red_team.dragons_taken,
                "RedTeamGrubsTaken": self.game_client_data.red_team.grubs_taken,
                "RedTeamRiftheraldTaken": self.game_client_data.red_team.riftherald_taken,
                "RedTeamAtakhanTaken": self.game_client_data.red_team.atakhan_taken,
                "RedTeamBaronTaken": self.game_client_data.red_team.baron_taken,
                "RedTeamFeats": self.game_client_data.red_team.feats,
                "RedPlayer1Role": self.game_client_data.red_team.players[0].role,
                "RedPlayer1ChampionId": self.game_client_data.red_team.players[0].champ_id,
                "RedPlayer1GoldSpent": self.game_client_data.red_team.players[0].gold_spent,
                "RedPlayer1Level": self.game_client_data.red_team.players[0].level,
                "RedPlayer1Kills": self.game_client_data.red_team.players[0].kills,
                "RedPlayer1Deaths": self.game_client_data.red_team.players[0].deaths,
                "RedPlayer1Assists": self.game_client_data.red_team.players[0].assists,
                "RedPlayer1CreepScore": self.game_client_data.red_team.players[0].creepscore,
                "RedPlayer1WardScore": self.game_client_data.red_team.players[0].wardscore,
                "RedPlayer2Role": self.game_client_data.red_team.players[1].role,
                "RedPlayer2ChampionId": self.game_client_data.red_team.players[1].champ_id,
                "RedPlayer2GoldSpent": self.game_client_data.red_team.players[1].gold_spent,
                "RedPlayer2Level": self.game_client_data.red_team.players[1].level,
                "RedPlayer2Kills": self.game_client_data.red_team.players[1].kills,
                "RedPlayer2Deaths": self.game_client_data.red_team.players[1].deaths,
                "RedPlayer2Assists": self.game_client_data.red_team.players[1].assists,
                "RedPlayer2CreepScore": self.game_client_data.red_team.players[1].creepscore,
                "RedPlayer2WardScore": self.game_client_data.red_team.players[1].wardscore,
                "RedPlayer3Role": self.game_client_data.red_team.players[2].role,
                "RedPlayer3ChampionId": self.game_client_data.red_team.players[2].champ_id,
                "RedPlayer3GoldSpent": self.game_client_data.red_team.players[2].gold_spent,
                "RedPlayer3Level": self.game_client_data.red_team.players[2].level,
                "RedPlayer3Kills": self.game_client_data.red_team.players[2].kills,
                "RedPlayer3Deaths": self.game_client_data.red_team.players[2].deaths,
                "RedPlayer3Assists": self.game_client_data.red_team.players[2].assists,
                "RedPlayer3CreepScore": self.game_client_data.red_team.players[2].creepscore,
                "RedPlayer3WardScore": self.game_client_data.red_team.players[2].wardscore,
                "RedPlayer4Role": self.game_client_data.red_team.players[3].role,
                "RedPlayer4ChampionId": self.game_client_data.red_team.players[3].champ_id,
                "RedPlayer4GoldSpent": self.game_client_data.red_team.players[3].gold_spent,
                "RedPlayer4Level": self.game_client_data.red_team.players[3].level,
                "RedPlayer4Kills": self.game_client_data.red_team.players[3].kills,
                "RedPlayer4Deaths": self.game_client_data.red_team.players[3].deaths,
                "RedPlayer4Assists": self.game_client_data.red_team.players[3].assists,
                "RedPlayer4CreepScore": self.game_client_data.red_team.players[3].creepscore,
                "RedPlayer4WardScore": self.game_client_data.red_team.players[3].wardscore,
                "RedPlayer5Role": self.game_client_data.red_team.players[4].role,
                "RedPlayer5ChampionId": self.game_client_data.red_team.players[4].champ_id,
                "RedPlayer5GoldSpent": self.game_client_data.red_team.players[4].gold_spent,
                "RedPlayer5Level": self.game_client_data.red_team.players[4].level,
                "RedPlayer5Kills": self.game_client_data.red_team.players[4].kills,
                "RedPlayer5Deaths": self.game_client_data.red_team.players[4].deaths,
                "RedPlayer5Assists": self.game_client_data.red_team.players[4].assists,
                "RedPlayer5CreepScore": self.game_client_data.red_team.players[4].creepscore,
                "RedPlayer5WardScore": self.game_client_data.red_team.players[4].wardscore}

        df = pd.DataFrame([data])
        return df

