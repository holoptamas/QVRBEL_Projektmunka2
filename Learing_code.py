import pandas as pd
from league_dataset import LeagueTrainDataset, LeagueTestDataset
from LeagueNeuralNetwork import LeagueNN
from torch.utils.data import DataLoader

dataset1 = pd.read_csv("D:\AA Egyetem stuff\Projektmunka\ProjektmunkaCode\PythonStuff\League_Match_Data\\DS_2025_12_2.csv")
#dataset2 = dataset1.drop(["BlueTeamKills", "BlueTeamGoldSpent", "RedTeamKills", "RedTeamGoldSpent"], axis=1)
dataset2 = dataset1[~dataset1.eq("Invalid").any(axis=1)]
shuffled_df = dataset2.sample(frac=1).reset_index(drop=True)
split_index = int(len(shuffled_df) * 0.8)
traindf = shuffled_df.iloc[:split_index]
testdf = shuffled_df.iloc[split_index:]

train_dataset = LeagueTrainDataset(traindf, "BlueTeamWin")
test_dataset = LeagueTestDataset(testdf, "BlueTeamWin", train_dataset.min_max_params, train_dataset.encoders)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

train_input_size = train_dataset.X.shape[1]
my_neural_network = LeagueNN(input_size=train_input_size, hidden_size=16, num_layers=3)

my_neural_network.train_model(train_loader=train_loader, num_epochs=2000, lr=0.01)

my_neural_network.evaluate_model(test_dataset)

my_neural_network.save_model("D:\\AA Egyetem stuff\\Projektmunka\\ProjektmunkaCode\\PythonStuff\\League_Neural_Networks\\league_model2.pth")