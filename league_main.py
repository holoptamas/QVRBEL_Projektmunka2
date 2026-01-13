import league_gameclient_api_handler as game_client_controller
from league_dataset import LeagueTrainDataset, LeagueLiveGameDataset
from LeagueNeuralNetwork import LeagueNN
import time
import requests
import pandas as pd

def match_controller():
    base_url = "https://127.0.0.1:2999/liveclientdata/allgamedata"
    response = requests.get(base_url, verify=False)
    end_of_game = False
    if response.status_code == 200:
        #for minmax params
        dataset1 = pd.read_csv("D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\League_Match_Data\\DS_2025_12_2.csv")
        dataset2 = dataset1[~dataset1.eq("Invalid").any(axis=1)]
        train_dataset = LeagueTrainDataset(dataset2, "BlueTeamWin")

        lol_data = response.json()
        current_time = lol_data["gameData"]["gameTime"]
        if(current_time < 900):
            print("Waiting for the 15 minute game time!")
            time.sleep((900 - current_time))

        game_client = game_client_controller.GameClientApiDataRetriever()

        network = LeagueNN.load_model("D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\League_Neural_Networks\\league_model2.pth")

        while(not end_of_game):
            response = requests.get(base_url, verify=False)
            if(response.status_code != 200):
                end_of_game = True
            else:
                raw_game_data = response.json()
                game_client.raw_match_data(raw_game_data)
                game_client.write_match_data()

                game_data_df = game_client.match_data_to_df()
                game_dataset = LeagueLiveGameDataset(game_data_df, train_dataset.min_max_params, train_dataset.encoders)

                data_dict = network.evaluate_single(game_dataset[0])
                for key, item in data_dict.items():
                    print(f"{key}: {item}")
                
                time.sleep(30)


    else:
        print("Could not get the data!")

match_controller()