import torch
import torch.nn as nn
import torch.optim as optim


class LeagueNN(nn.Module):
    def __init__(self, num_numeric_features, max_champion_id, num_roles, hidden_size, num_layers, dropout_rate, champion_embedding_dim, role_embedding_dim):
        super().__init__()

        self.num_numeric_features = num_numeric_features
        self.max_champion_id = max_champion_id
        self.num_roles = num_roles
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_rate = dropout_rate
        self.champion_embedding_dim = champion_embedding_dim
        self.role_embedding_dim = role_embedding_dim

        self.champion_embedding = nn.Embedding(
            num_embeddings=max_champion_id + 1,
            embedding_dim=champion_embedding_dim,
            padding_idx=0
        )

        self.role_embedding = nn.Embedding(
            num_embeddings=num_roles,
            embedding_dim=role_embedding_dim,
            padding_idx=0
        )

        input_size = (
            num_numeric_features
            + 10 * champion_embedding_dim
            + 10 * role_embedding_dim
        )

        layers = []

        layers.append(nn.Linear(input_size, hidden_size))
        layers.append(nn.LeakyReLU(negative_slope=0.01))
        layers.append(nn.Dropout(dropout_rate))

        for _ in range(num_layers - 1):
            layers.append(nn.Linear(hidden_size, hidden_size))
            layers.append(nn.LeakyReLU(negative_slope=0.01))
            layers.append(nn.Dropout(dropout_rate))

        layers.append(nn.Linear(hidden_size, 1))

        self.model = nn.Sequential(*layers)

    def forward(self, numeric_x, champion_x, role_x):
        champion_embedded = self.champion_embedding(champion_x)
        role_embedded = self.role_embedding(role_x)

        champion_embedded = champion_embedded.view(champion_embedded.size(0), -1)
        role_embedded = role_embedded.view(role_embedded.size(0), -1)

        x = torch.cat(
            [numeric_x, champion_embedded, role_embedded],
            dim=1
        )

        return self.model(x)

    def train_model(self, train_loader, num_epochs, lr):
        device = "cuda" if torch.cuda.is_available() else "cpu"

        self.to(device)
        self.train()

        loss_function = nn.BCEWithLogitsLoss()
        optimizer = optim.Adam(self.parameters(), lr=lr)

        for epoch in range(num_epochs):
            total_loss = 0.0

            for numeric_x, champion_x, role_x, y_batch in train_loader:
                numeric_x = numeric_x.float().to(device)
                champion_x = champion_x.long().to(device)
                role_x = role_x.long().to(device)
                y_batch = y_batch.float().to(device)

                if y_batch.dim() == 1:
                    y_batch = y_batch.unsqueeze(1)

                optimizer.zero_grad()

                outputs = self(numeric_x, champion_x, role_x)
                loss = loss_function(outputs, y_batch)

                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            print(f"Epoch [{epoch + 1}/{num_epochs}] - Loss: {total_loss:.4f}")

    def evaluate_model(self, test_loader):
        device = "cuda" if torch.cuda.is_available() else "cpu"

        self.to(device)
        self.eval()

        TP = TN = FP = FN = 0

        with torch.no_grad():
            for numeric_x, champion_x, role_x, y_batch in test_loader:
                numeric_x = numeric_x.float().to(device)
                champion_x = champion_x.long().to(device)
                role_x = role_x.long().to(device)
                y_batch = y_batch.float().to(device)

                if y_batch.dim() == 1:
                    y_batch = y_batch.unsqueeze(1)

                output = torch.sigmoid(self(numeric_x, champion_x, role_x))
                pred = (output >= 0.5).float()

                TP += ((pred == 1) & (y_batch == 1)).sum().item()
                TN += ((pred == 0) & (y_batch == 0)).sum().item()
                FP += ((pred == 1) & (y_batch == 0)).sum().item()
                FN += ((pred == 0) & (y_batch == 1)).sum().item()

        TP = float(TP)
        TN = float(TN)
        FP = float(FP)
        FN = float(FN)

        accuracy = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) else 0
        precision = TP / (TP + FP) if (TP + FP) else 0
        sensitivity = TP / (TP + FN) if (TP + FN) else 0
        specificity = TN / (TN + FP) if (TN + FP) else 0
        f1 = (2 * precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) else 0

        print("---- Evaluation Metrics ----")
        print(f"TP: {TP:.0f} | TN: {TN:.0f} | FP: {FP:.0f} | FN: {FN:.0f}")
        print(f"Accuracy:    {accuracy * 100:.2f}%")
        print(f"Precision:   {precision * 100:.2f}%")
        print(f"Sensitivity: {sensitivity * 100:.2f}%")
        print(f"Specificity: {specificity * 100:.2f}%")
        print(f"F1 Score:    {f1:.4f}")

        return {
            "TP": TP,
            "TN": TN,
            "FP": FP,
            "FN": FN,
            "accuracy": accuracy,
            "precision": precision,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "f1": f1
        }

    def evaluate_single(self, numeric_x, champion_x, role_x):
        device = "cpu"

        self.to(device)
        self.eval()

        with torch.no_grad():
            if numeric_x.dim() == 1:
                numeric_x = numeric_x.unsqueeze(0)

            if champion_x.dim() == 1:
                champion_x = champion_x.unsqueeze(0)

            if role_x.dim() == 1:
                role_x = role_x.unsqueeze(0)

            numeric_x = numeric_x.float().to(device)
            champion_x = champion_x.long().to(device)
            role_x = role_x.long().to(device)

            output = torch.sigmoid(self(numeric_x, champion_x, role_x))
            
            blue_prob = output.item()
            red_prob = 1.0 - blue_prob

        return {
            "blue_win_probability": blue_prob,
            "red_win_probability": red_prob,
            "confidence": abs(blue_prob - 0.5) * 2,
            "predicted_winner": "Blue" if blue_prob >= 0.5 else "Red"
        }

    def save_model(self, path):
        checkpoint = {
            "num_numeric_features": self.num_numeric_features,
            "max_champion_id": self.max_champion_id,
            "num_roles": self.num_roles,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "dropout_rate": self.dropout_rate,
            "champion_embedding_dim": self.champion_embedding_dim,
            "role_embedding_dim": self.role_embedding_dim,
            "state_dict": self.state_dict()
        }

        torch.save(checkpoint, path)
        print(f"Model saved to {path}")

    def load_model(path, device=None):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        checkpoint = torch.load(path, map_location=device)

        model = LeagueNN(
            num_numeric_features=checkpoint["num_numeric_features"],
            max_champion_id=checkpoint["max_champion_id"],
            num_roles=checkpoint["num_roles"],
            hidden_size=checkpoint["hidden_size"],
            num_layers=checkpoint["num_layers"],
            dropout_rate=checkpoint["dropout_rate"],
            champion_embedding_dim=checkpoint["champion_embedding_dim"],
            role_embedding_dim=checkpoint["role_embedding_dim"]
        )

        model.load_state_dict(checkpoint["state_dict"])
        model.to(device)
        model.eval()

        print(f"Model loaded from {path} on device {device}")
        return model