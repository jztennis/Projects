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
import matplotlib.pyplot as plt
from network import TennisPredictor

class EarlyStopping:
    def __init__(self, patience=5, min_delta=0.0001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
    
    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0

matches = pd.read_csv('atp_utr_tennis_matches.csv')
utr_history = pd.read_csv('utr_history.csv')
history = get_player_history(utr_history)
player_profiles = get_player_profiles(matches, history)

log_model = joblib.load('log_model.sav')

X = []
for i in range(len(matches)):
    X.append(preprocess_match_data(matches.iloc[i], player_profiles)) # log_prop?
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
optimizer = optim.AdamW(model.parameters(), lr=0.00001, weight_decay=0.99999)
early_stopper = EarlyStopping(patience=20)

# Training loop
epochs = 30000
train_loss = []
val_loss_arr = []
count = 0
for epoch in range(epochs):
    count += 1
    model.train()
    total_loss = 0
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        y_pred = model(X_batch).squeeze()
        loss = criterion(y_pred, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    train_loss.append(total_loss / len(train_loader))

    model.eval()
    val_loss = 0
    with torch.no_grad():
        for X_val_batch, y_val_batch, in val_loader:
            y_val_pred = model(X_val_batch).squeeze()
            val_loss += criterion(y_val_pred, y_val_batch).item()
    val_loss_arr.append(val_loss / len(val_loader))
    
    # if epoch % 50 == 0:
    print(f"Epochs: {epoch+1} / {epochs}, Loss: {total_loss/len(train_loader):.4f}, Val Loss: {val_loss/len(val_loader):.4f}")

    early_stopper(round(val_loss / len(val_loader),4))
    if early_stopper.early_stop:
        print(f"Early Stopping Triggered. Best Loss: {early_stopper.best_loss}")
        break

joblib.dump(model, 'model.sav')

#=== Evaluate model ===#

# model.eval()
# y_test_pred = model(X_test).squeeze().detach().numpy()
# temp = y_test_pred
# y_test_pred = (y_test_pred > 0.5).astype(int)
# y_test = y_test.numpy()
# accuracy = accuracy_score(y_test, y_test_pred)
# print(f"General Accuracy: {accuracy:.4f}\n")
# acc1, acc2, acc3, acc4, acc5 = [0,0], [0,0], [0,0], [0,0], [0,0]
# for i in range(len(temp)):
#     if y_test_pred[i] == y_test[i]:
#         corr = True
#     else:
#         corr = False

#     if temp[i] < 0.1 or temp[i] >= 0.9:
#         if corr:
#             acc1[0] += 1
#             acc1[1] += 1
#         else:
#             acc1[1] += 1
#     elif (temp[i] < 0.2 and temp[i] >= 0.1) or (temp[i] >= 0.8 and temp[i] < 0.9):
#         if corr:
#             acc2[0] += 1
#             acc2[1] += 1
#         else:
#             acc2[1] += 1
#     elif (temp[i] < 0.3 and temp[i] >= 0.2) or (temp[i] >= 0.7 and temp[i] < 0.8):
#         if corr:
#             acc3[0] += 1
#             acc3[1] += 1
#         else:
#             acc3[1] += 1
#     elif (temp[i] < 0.4 and temp[i] >= 0.3) or (temp[i] >= 0.6 and temp[i] < 0.7):
#         if corr:
#             acc4[0] += 1
#             acc4[1] += 1
#         else:
#             acc4[1] += 1
#     elif temp[i] >= 0.4 and temp[i] < 0.6:
#         if corr:
#             acc5[0] += 1
#             acc5[1] += 1
#         else:
#             acc5[1] += 1

# print(f"Accuracy If Predicted Val In Range of [0, 0.1) or (0.9, 1]: {round(100*(acc1[0]/acc1[1]), 2)}% ({acc1[0]})")
# print(f"Accuracy If Predicted Val In Range of [0.1, 0.2) or (0.8, 0.9]: {round(100*(acc2[0]/acc2[1]), 2)}% ({acc2[0]})")
# print(f"Accuracy If Predicted Val In Range of [0.2, 0.3) or (0.7, 0.8]: {round(100*(acc3[0]/acc3[1]), 2)}% ({acc3[0]})")
# print(f"Accuracy If Predicted Val In Range of [0.3, 0.4) or (0.6, 0.7]: {round(100*(acc4[0]/acc4[1]), 2)}% ({acc4[0]})")
# print(f"Accuracy If Predicted Val In Range of [0.4, 0.6]: {round(100*(acc5[0]/acc5[1]), 2)}% ({acc5[0]})")

# plt.figure()
# plt.plot(range(1, count + 1), train_loss, label="Training Loss")
# plt.plot(range(1, count + 1), val_loss_arr, label="Validation Loss")
# plt.xlabel("Epochs")
# plt.ylabel("Loss")
# plt.title("Training vs. Validation Loss")
# plt.legend()
# # plt.grid(True)
# plt.show()

'''
CURRENT VERSION (Match Outcome):
    ~ 86.8% Mean Accuracy
    ~ 0.35% Variance in Accuracy
'''