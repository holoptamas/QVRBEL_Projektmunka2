import torch
import torch.nn as nn
import torch.optim as optim

class LeagueNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        layers = []

        layers.append(nn.Linear(input_size, hidden_size))
        layers.append(nn.ReLU())
        for _ in range(num_layers - 1):
            layers.append(nn.Linear(hidden_size, hidden_size))
            layers.append(nn.ReLU())

        layers.append(nn.Linear(hidden_size, 1))
        layers.append(nn.Sigmoid())

        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)

    def train_model(self, train_loader, num_epochs, lr):
        device = (
            "cuda" if torch.cuda.is_available() else
            "cpu"
        )
        print(f"Training on device: {device}")

        self.to(device)

        loss_function = nn.BCELoss()
        optimizer = optim.SGD(self.parameters(), lr=lr)

        self.train()

        for epoch in range(num_epochs):
            total_loss = 0.0
            for X_batch, y_batch in train_loader:
                X_batch = X_batch.float().to(device)
                y_batch = y_batch.float().to(device)

                if y_batch.dim() == 1:
                    y_batch.unsqueeze(1)

                outputs = self(X_batch)
                loss = loss_function(outputs, y_batch)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            print(f"Epoch [{epoch+1}/{num_epochs}] - Loss: {total_loss:.4f}")

    def evaluate_model(self, test_loader):
        device = (
            "cuda" if torch.cuda.is_available() else
            "cpu"
        )
        print(f"Evaluating on device: {device}")

        self.to(device)
        self.eval()

        TP = TN = FP = FN = 0

        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                X_batch = X_batch.float().to(device)
                y_batch = y_batch.float().to(device)

                if y_batch.dim() == 1:
                    y_batch = y_batch.unsqueeze(1)

                output = self(X_batch)
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

    def evaluate_single(self, x):
        device = (
            "cpu"
        )
        print(f"Evaluating on device: {device}")

        self.to(device)
        self.eval()

        with torch.no_grad():
            x = x.float().to(device)

            output = self(x)
            blue_prob = output.item()
            red_prob = 1.0 - blue_prob

        return {
        "blue_win_probability": blue_prob,
        "red_win_probability": red_prob,
        "predicted_winner": "Blue" if blue_prob >= 0.5 else "Red",
        "confidence": abs(blue_prob - 0.5) * 2
        }
    
    def save_model(self, path):
        checkpoint = {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "state_dict": self.state_dict()
        }
        torch.save(checkpoint, path)
        print(f"Model saved to {path}")
    
    def load_model(path, device=None):
   
        checkpoint = torch.load(path, map_location=device)

        model = LeagueNN(
        input_size=checkpoint["input_size"],
        hidden_size=checkpoint["hidden_size"],
        num_layers=checkpoint["num_layers"]
        )

        model.load_state_dict(checkpoint["state_dict"])

        if device:
            model.to(device)

        model.eval()
        print(f"Model loaded from {path} on device {device}")
        return model


