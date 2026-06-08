from pathlib import Path
import pandas as pd
import torch
from torch.utils.data import DataLoader

from LoL_live_game_prediction.Neural_Network.league_dataset import LeagueTrainDataset, LeagueTestDataset
from LoL_live_game_prediction.Neural_Network.LeagueNeuralNetwork import LeagueNN

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DATASET_PATH = (BASE_DIR.parent/"League_Match_Data"/"2026_06_02_20_00.csv")
MODEL_PATH = (BASE_DIR.parent/"League_Neural_Networks"/"league_model.pth")
TRAIN_CSV_PATH = (BASE_DIR.parent/"League_Match_Data"/"DS_2026_06_02_20_00_train.csv")
TEST_CSV_PATH = (BASE_DIR.parent/"League_Match_Data"/"DS_2026_06_02_20_00_test.csv")
CHAMP_CSV_PATH = (BASE_DIR.parent/"LeagueAssets"/"ChampIdAndName.csv")

dataset1 = pd.read_csv(BASE_DATASET_PATH)
dataset1 = dataset1.drop(["GameVersion", "BlueTeamKills", "BlueTeamGoldSpent", "RedTeamKills", "RedTeamGoldSpent", "RedTeamWin", "BluePlayer1ChampionName", "BluePlayer2ChampionName",  "BluePlayer3ChampionName",  "BluePlayer4ChampionName", "BluePlayer5ChampionName", "RedPlayer1ChampionName", "RedPlayer2ChampionName", "RedPlayer3ChampionName", "RedPlayer4ChampionName", "RedPlayer5ChampionName"], axis=1)
dataset1 = dataset1[~dataset1.eq("Invalid").any(axis=1)]
dataset1 = dataset1.iloc[:,:-1]
shuffled_df = dataset1.sample(frac=1).reset_index(drop=True)
split_index = int(len(shuffled_df) * 0.8)
traindf = shuffled_df.iloc[:split_index]
traindf.to_csv(TRAIN_CSV_PATH, index=False)
testdf = shuffled_df.iloc[split_index:]
testdf.to_csv(TEST_CSV_PATH, index=False)

train_dataset = LeagueTrainDataset(traindf, "BlueTeamWin")
train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True)

test_dataset = LeagueTestDataset(testdf, "BlueTeamWin", train_dataset.get_min_max_params(), train_dataset.get_role_mapping())
test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)

champs = pd.read_csv(CHAMP_CSV_PATH)
max_champ_id = int(champs["ID"].max())

my_neural_network = LeagueNN(num_numeric_features=train_dataset.get_num_numeric_features(),
                             max_champion_id=max_champ_id,
                             num_roles=train_dataset.get_num_roles(),
                             hidden_size=128,
                             num_layers=4,
                             dropout_rate=0.4,
                             champion_embedding_dim=4,
                             role_embedding_dim=2)


my_neural_network.train_model(train_loader=train_loader, num_epochs=100, lr=0.001)

my_neural_network.evaluate_model(test_loader=test_loader)

my_neural_network.save_model(MODEL_PATH)