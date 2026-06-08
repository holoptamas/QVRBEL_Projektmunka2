import torch
from torch.utils.data import Dataset
import pandas as pd


CHAMPION_COLS = [
    "BluePlayer1ChampionId", "BluePlayer2ChampionId", "BluePlayer3ChampionId",
    "BluePlayer4ChampionId", "BluePlayer5ChampionId",
    "RedPlayer1ChampionId", "RedPlayer2ChampionId", "RedPlayer3ChampionId",
    "RedPlayer4ChampionId", "RedPlayer5ChampionId"
]

ROLE_COLS = [
    "BluePlayer1Role", "BluePlayer2Role", "BluePlayer3Role",
    "BluePlayer4Role", "BluePlayer5Role",
    "RedPlayer1Role", "RedPlayer2Role", "RedPlayer3Role",
    "RedPlayer4Role", "RedPlayer5Role"
]


class LeagueTrainDataset(Dataset):
    def __init__(self, df: pd.DataFrame, output_feature: str):
        df = df.copy()

        self.y = torch.tensor(df[output_feature].values, dtype=torch.float32).view(-1, 1)
        df = df.drop(columns=[output_feature])

        numeric_cols = df.select_dtypes(include=["int64", "float64", "bool"]).columns.tolist()
        numeric_cols = [
            c for c in numeric_cols
            if c not in CHAMPION_COLS and c not in ROLE_COLS
        ]

        self.numeric_cols = numeric_cols
        self.champion_cols = CHAMPION_COLS
        self.role_cols = ROLE_COLS

        self.min_max_params = {}

        for col in self.numeric_cols:
            col_min = df[col].min()
            col_max = df[col].max()

            self.min_max_params[col] = (col_min, col_max)

            df[col] = pd.to_numeric(df[col], errors="coerce")

            col_min = df[col].min()
            col_max = df[col].max()

            if pd.isna(col_min) or pd.isna(col_max) or col_max - col_min == 0:
                df[col] = 0.0
            else:
                df[col] = (df[col] - col_min) / (col_max - col_min)

            df[col] = df[col].fillna(0.0)

        self.role_mapping = {"<UNK>": 0}

        unique_roles = pd.unique(df[self.role_cols].astype(str).values.ravel())

        for i, role in enumerate(unique_roles, start=1):
            self.role_mapping[role] = i

        for col in self.role_cols:
            df[col] = (
                df[col]
                .astype(str)
                .map(self.role_mapping)
                .fillna(0)
                .astype(int)
            )

        df[self.champion_cols] = df[self.champion_cols].fillna(0).astype(int)

        self.numeric_X = torch.tensor(df[self.numeric_cols].values, dtype=torch.float32)
        self.champion_X = torch.tensor(df[self.champion_cols].values, dtype=torch.long)
        self.role_X = torch.tensor(df[self.role_cols].values, dtype=torch.long)

    def __len__(self):
        return len(self.numeric_X)

    def __getitem__(self, idx):
        return (self.numeric_X[idx], self.champion_X[idx], self.role_X[idx], self.y[idx])

    def get_min_max_params(self):
        return self.min_max_params

    def get_role_mapping(self):
        return self.role_mapping

    def get_num_numeric_features(self):
        return len(self.numeric_cols)

    def get_num_roles(self):
        return len(self.role_mapping)
    
class LeagueTestDataset(Dataset):
    def __init__(self, df: pd.DataFrame, output_feature: str, min_max_params: dict, role_mapping: dict):
        df = df.copy()

        self.y = torch.tensor(df[output_feature].values, dtype=torch.float32).view(-1, 1)
        df = df.drop(columns=[output_feature])

        numeric_cols = df.select_dtypes(include=["int64", "float64", "bool"]).columns.tolist()
        numeric_cols = [
            c for c in numeric_cols
            if c not in CHAMPION_COLS and c not in ROLE_COLS
        ]

        self.numeric_cols = numeric_cols
        self.champion_cols = CHAMPION_COLS
        self.role_cols = ROLE_COLS

        for col in self.numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
            col_min, col_max = min_max_params[col]
        
            if pd.isna(col_min) or pd.isna(col_max) or col_max - col_min == 0:
                df[col] = 0.0
            else:
                df[col] = (df[col] - col_min) / (col_max - col_min)
        
            df[col] = df[col].fillna(0.0)

        for col in self.role_cols:
            df[col] = (
                df[col]
                .astype(str)
                .map(role_mapping)
                .fillna(0)
                .astype(int)
            )

        df[self.champion_cols] = df[self.champion_cols].fillna(0).astype(int)

        self.numeric_X = torch.tensor(df[self.numeric_cols].values, dtype=torch.float32)
        self.champion_X = torch.tensor(df[self.champion_cols].values, dtype=torch.long)
        self.role_X = torch.tensor(df[self.role_cols].values, dtype=torch.long)

    def __len__(self):
        return len(self.numeric_X)

    def __getitem__(self, idx):
        return (self.numeric_X[idx], self.champion_X[idx], self.role_X[idx], self.y[idx])
    
class LeagueLiveGameDataset(Dataset):
    def __init__(self, df: pd.DataFrame, min_max_params: dict, role_mapping: dict):
        df = df.copy()

        numeric_cols = df.select_dtypes(include=["int64", "float64", "bool"]).columns.tolist()
        numeric_cols = [
            c for c in numeric_cols
            if c not in CHAMPION_COLS and c not in ROLE_COLS
        ]

        self.numeric_cols = numeric_cols
        self.champion_cols = CHAMPION_COLS
        self.role_cols = ROLE_COLS

        for col in self.numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
            col_min, col_max = min_max_params[col]
        
            if pd.isna(col_min) or pd.isna(col_max) or col_max - col_min == 0:
                df[col] = 0.0
            else:
                df[col] = (df[col] - col_min) / (col_max - col_min)
        
            df[col] = df[col].fillna(0.0)

        for col in self.role_cols:
            df[col] = (
                df[col]
                .astype(str)
                .map(role_mapping)
                .fillna(0)
                .astype(int)
            )

        df[self.champion_cols] = df[self.champion_cols].fillna(0).astype(int)

        self.numeric_X = torch.tensor(df[self.numeric_cols].values, dtype=torch.float32)
        self.champion_X = torch.tensor(df[self.champion_cols].values, dtype=torch.long)
        self.role_X = torch.tensor(df[self.role_cols].values, dtype=torch.long)

    def __len__(self):
        return len(self.numeric_X)

    def __getitem__(self, idx):
        return (self.numeric_X[idx], self.champion_X[idx], self.role_X[idx])