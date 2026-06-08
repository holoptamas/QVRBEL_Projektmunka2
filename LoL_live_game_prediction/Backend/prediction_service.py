import time
import threading
import requests
import pandas as pd

from LoL_live_game_prediction.Neural_Network.league_dataset import LeagueTrainDataset, LeagueLiveGameDataset
from LoL_live_game_prediction.Neural_Network.LeagueNeuralNetwork import LeagueNN
from LoL_live_game_prediction.Backend.league_gameclient_api_handler import GameClientApiDataRetriever


class PredictionService:
    def __init__(self, game_client:GameClientApiDataRetriever, model_path, train_csv_path):
        self.base_url = "https://127.0.0.1:2999/liveclientdata/allgamedata"

        self.game_client:GameClientApiDataRetriever = game_client

        dataset1 = pd.read_csv(train_csv_path)
        dataset1 = dataset1[~dataset1.eq("Invalid").any(axis=1)]
        self.train_dataset = LeagueTrainDataset(dataset1, "BlueTeamWin")

        self.network = LeagueNN.load_model(model_path)

        self.latest_prediction = None
        self.latest_game_state = None
        self.is_running = False

    def start_prediction_loop(self):
        if self.is_running:
            return

        self.is_running = True

        thread = threading.Thread(target=self.prediction_loop, daemon=True)
        thread.start()

    def prediction_loop(self):
        while self.is_running:
            try:
                response = requests.get(self.base_url, verify=False)

                if response.status_code != 200:
                    self.latest_prediction = {
                        "status": "not_in_game",
                        "message": "Could not get live game data."
                    }

                    self.latest_game_state = {
                        "status": "not_in_game",
                        "message": "Could not get live game data."
                    }

                    time.sleep(5)
                    continue

                raw_game_data = response.json()
                current_time = raw_game_data["gameData"]["gameTime"]

                self.game_client.raw_match_data(raw_game_data)
                self.latest_game_state = self.match_data_to_dict()

                if current_time < 900:
                    self.latest_prediction = {
                        "status": "waiting",
                        "message": "Waiting for 15 minute game time.",
                        "game_time": current_time
                    }

                    time.sleep(5)
                    continue

                game_data_df = self.game_client.match_data_to_df()

                game_dataset = LeagueLiveGameDataset(
                    game_data_df,
                    self.train_dataset.get_min_max_params(),
                    self.train_dataset.get_role_mapping()
                )

                numeric_x, champion_x, role_x = game_dataset[0]

                prediction_dict = self.network.evaluate_single(
                    numeric_x,
                    champion_x,
                    role_x
                )

                prediction_dict["status"] = "success"
                prediction_dict["message"] = ""
                prediction_dict["game_time"] = current_time

                self.latest_prediction = prediction_dict

                time.sleep(10)

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.latest_prediction = {
                    "status": "error",
                    "message": str(e)
                }

                self.latest_game_state = {
                    "status": "error",
                    "message": str(e)
                }

                time.sleep(5)

    def get_latest_prediction(self):
        if self.latest_prediction is None:
            return { 
                "status": "starting",
                "message": "Prediction service has not produced a prediction yet."
            }

        return self.latest_prediction
    
    def get_latest_game_state(self):
        if self.latest_game_state is None:
            return {
                "status": "starting",
                "message": "No game state available yet."
            }

        return self.latest_game_state


    def match_data_to_dict(self):
        game_data = self.game_client.get_game_cliend_data()

        return {
            "status": "success",
            "message": "",
            "game_duration": game_data.game_duration,

            "blue_team": self.team_to_dict(game_data.blue_team),
            "red_team": self.team_to_dict(game_data.red_team)
        }
    
    def team_to_dict(self, team):
        return {
            "team_kills": team.team_kills,
            "team_gold_spent": team.team_gold_spent,
            "towers_taken": team.towers_taken,
            "inhibitors_taken": team.inhibitors_taken,
            "dragons_taken": team.dragons_taken,
            "grubs_taken": team.grubs_taken,
            "riftherald_taken": team.riftherald_taken,
            "baron_taken": team.baron_taken,
            "players": [
                self.player_to_dict(player) for player in team.players
            ]
        }


    def player_to_dict(self, player):
        return {
            "player_name": player.player_name,
            "role": player.role,
            "champion_id": player.champ_id,
            "champion_name": player.champ_name,
            "gold_spent": player.gold_spent,
            "level": player.level,
            "kills": player.kills,
            "deaths": player.deaths,
            "assists": player.assists,
            "creep_score": player.creepscore,
            "ward_score": player.wardscore
        }