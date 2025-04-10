import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset
import joblib
from network import get_player_profiles, get_player_history, preprocess_match_data
from sklearn.metrics import accuracy_score

# Define the neural network architecture
class TennisPredictor(nn.Module):
    def __init__(self, input_size):
        super(TennisPredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

matches = pd.read_csv('atp_utr_tennis_matches.csv')
utr_history = pd.read_csv('utr_history.csv')
history = get_player_history(utr_history)
player_profiles = get_player_profiles(matches, history)

X = []
for i in range(len(matches)):
    X.append(preprocess_match_data(matches.iloc[i], player_profiles))
vector = np.array(X)

# Extract target variable (e.g., match result, assuming `p_win` indicates win/loss)
y = matches['p_win'].values  # 1 for win, 0 for loss (or whatever your target variable is)

# Normalize features (important for neural networks)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Convert the numpy arrays to PyTorch tensors
X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32)

# Split the data into training and testing sets
X_train, X_temp, y_train, y_temp = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Create DataLoader for training
train_dataset = TensorDataset(X_train, y_train)
val_dataset = TensorDataset(X_val, y_val)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

# Initialize model, loss function, and optimizer
input_size = X_train.shape[1]
model = TennisPredictor(input_size)
criterion = nn.BCELoss()  # Binary cross-entropy loss for classification
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
epochs = 20
for epoch in range(epochs):
    model.train()
    total_loss = 0
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        y_pred = model(X_batch).squeeze()
        loss = criterion(y_pred, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    model.eval()
    val_loss = 0
    with torch.no_grad():
        for X_val_batch, y_val_batch, in val_loader:
            y_val_pred = model(X_val_batch).squeeze()
            val_loss += criterion(y_val_pred, y_val_batch).item()

    print(f"Epochs: {epoch+1} / {epochs}, Loss: {total_loss/len(train_loader):.4f}, Val Loss: {val_loss/len(val_loader):.4f}")
print(f"Epochs: {epoch+1} / {epochs}, Loss: {total_loss/len(train_loader):.4f}, Val Loss: {val_loss/len(val_loader):.4f}")

joblib.dump(model, 'nn_model.sav')

#=== Evaluate model ===#

# model.eval()
# y_test_pred = model(X_test).squeeze().detach().numpy()
# y_test_pred = (y_test_pred > 0.5).astype(int)
# accuracy = accuracy_score(y_test.numpy(), y_test_pred)
# print(f"Accuracy: {accuracy:.4f}\n")

'''
CURRENT VERSION (Match Outcome):
    86.5% - 85.5% Accuracy
'''