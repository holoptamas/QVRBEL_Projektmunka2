import pandas as pd
from league_dataset import LeagueTrainDataset, LeagueTestDataset, LeagueLiveGameDataset
from LeagueNeuralNetwork import LeagueNN
from torch.utils.data import DataLoader

dataset1 = pd.read_csv("D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\League_Match_Data\\DS_2025_12_2.csv")
dataset2 = dataset1[~dataset1.eq("Invalid").any(axis=1)]
#dataset2 = dataset1.drop(["BlueTeamKills", "BlueTeamGoldSpent", "RedTeamKills", "RedTeamGoldSpent"], axis=1)

shuffled_df = dataset2.sample(frac=1).reset_index(drop=True)
split_index = int(len(shuffled_df) * 0.8)
traindf = shuffled_df.iloc[:split_index]
testdf = shuffled_df.iloc[split_index:]

singledf = testdf.sample(n=1).reset_index(drop=True)
blue_win = singledf['BlueTeamWin'].values[0]
game_duration = singledf['GameDuration'].values[0]
blue_kills = singledf['BlueTeamKills'].values[0]
red_kills = singledf['RedTeamKills'].values[0]
test_singledf = singledf.drop(['BlueTeamWin'], axis=1)

train_dataset = LeagueTrainDataset(shuffled_df, "BlueTeamWin")
test_dataset = LeagueTestDataset(testdf, "BlueTeamWin", train_dataset.min_max_params, train_dataset.encoders)
test_singledata = LeagueLiveGameDataset(test_singledf, train_dataset.min_max_params, train_dataset.encoders)

my_neural_network = LeagueNN.load_model("D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\League_Neural_Networks\\league_model2.pth")

my_neural_network.evaluate_model(test_dataset)
data_dict = my_neural_network.evaluate_single(test_singledata[0])

for key, item in data_dict.items():
    print(f"{key}: {item}")
if blue_win == 1:
    print("Blue Wins")
else:
    print("Red Wins")
print(f"{int(game_duration / 60)}:{game_duration % 60}")
print(f"Blue kills: {blue_kills}, Red kills: {red_kills}")
