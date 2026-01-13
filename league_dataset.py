import torch
from torch.utils.data import Dataset
import pandas as pd
from sklearn.preprocessing import LabelEncoder

class LeagueTrainDataset(Dataset):
    def __init__(self, df:pd.DataFrame, output_feature:str):
        df = df.copy()

        self.y = torch.tensor(df[output_feature].values, dtype=torch.float32).view(-1, 1)

        df = df.drop(columns=[output_feature])

        numeric_cols = df.select_dtypes(include=["int64", "float64", "bool"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

        champ_id_cols = ["BluePlayer1ChampionId", "BluePlayer2ChampionId","BluePlayer3ChampionId","BluePlayer4ChampionId","BluePlayer5ChampionId", 
                         "RedPlayer1ChampionId", "RedPlayer2ChampionId","RedPlayer3ChampionId","RedPlayer4ChampionId","RedPlayer5ChampionId"]
        categorical_cols.extend(champ_id_cols)

        for champid in champ_id_cols:
            numeric_cols.remove(champid)

        numeric_cols = [c for c in numeric_cols if c not in categorical_cols]

        self.categorical_cols = categorical_cols
        self.numeric_cols = numeric_cols
        
        self.min_max_params = {}

        for col in self.numeric_cols:
            col_min = df[col].min()
            col_max = df[col].max()
            
            self.min_max_params[col] = (col_min, col_max)

            if col_max - col_min == 0:
                df[col] = 0.0   
            else:
                df[col] = (df[col] - col_min) / (col_max - col_min)

        self.encoders = {}

        #todo: label encoder helyett embedding

        for col in self.categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.encoders[col] = le

        self.X = torch.tensor(df.values, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

    def get_min_max_params(self):
        return self.min_max_params
    
    def get_encoders(self):
        return self.encoders
    
class LeagueTestDataset(Dataset):
    def __init__(self, df:pd.DataFrame, output_feature:str, min_max_params: dict, encoders: dict):
        df = df.copy()

        self.y = torch.tensor(df[output_feature].values, dtype=torch.float32).view(-1, 1)

        df = df.drop(columns=[output_feature])

        numeric_cols = df.select_dtypes(include=["int64", "float64", "bool"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

        champ_id_cols = ["BluePlayer1ChampionId", "BluePlayer2ChampionId","BluePlayer3ChampionId","BluePlayer4ChampionId","BluePlayer5ChampionId", 
                         "RedPlayer1ChampionId", "RedPlayer2ChampionId","RedPlayer3ChampionId","RedPlayer4ChampionId","RedPlayer5ChampionId"]
        categorical_cols.extend(champ_id_cols)

        for champid in champ_id_cols:
            numeric_cols.remove(champid)

        numeric_cols = [c for c in numeric_cols if c not in categorical_cols]

        self.categorical_cols = categorical_cols
        self.numeric_cols = numeric_cols

        for col in self.numeric_cols:
            col_min, col_max = min_max_params[col]

            if col_max - col_min == 0:
                df[col] = 0.0   
            else:
                df[col] = (df[col] - col_min) / (col_max - col_min)

        #todo: label encoder helyett embedding

        for col in self.categorical_cols:
            le: LabelEncoder = encoders[col]
            df[col] = le.transform(df[col].astype(str))

        self.X = torch.tensor(df.values, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
    
class LeagueLiveGameDataset(Dataset):
    def __init__(self, df:pd.DataFrame, min_max_params: dict, encoders: dict):
        df = df.copy()

        numeric_cols = df.select_dtypes(include=["int64", "float64", "bool"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

        champ_id_cols = ["BluePlayer1ChampionId", "BluePlayer2ChampionId","BluePlayer3ChampionId","BluePlayer4ChampionId","BluePlayer5ChampionId", 
                         "RedPlayer1ChampionId", "RedPlayer2ChampionId","RedPlayer3ChampionId","RedPlayer4ChampionId","RedPlayer5ChampionId"]
        categorical_cols.extend(champ_id_cols)

        for champid in champ_id_cols:
            numeric_cols.remove(champid)

        numeric_cols = [c for c in numeric_cols if c not in categorical_cols]

        self.categorical_cols = categorical_cols
        self.numeric_cols = numeric_cols

        for col in self.numeric_cols:
            col_min, col_max = min_max_params[col]

            if col_max - col_min == 0:
                df[col] = 0.0   
            else:
                df[col] = (df[col] - col_min) / (col_max - col_min)

        #todo: label encoder helyett embedding

        for col in self.categorical_cols:
            le: LabelEncoder = encoders[col]
            df[col] = le.transform(df[col].astype(str))

        self.X = torch.tensor(df.values, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx]

