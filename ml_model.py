import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

#Step 3

train = pd.read_excel(r"Output_crypto.xlsx ")
print(train.shape)

print(train.head(5))

#Checking for null values in every column
Nulls = pd.concat([train.isnull().sum()],axis = 1,keys='Train')
print(Nulls)

# Features and targets
#Days_Since_High_Last_7_Days = High_Last_7_Days and Days_Since_Low_Last_7_Days = Low_Last_7_Days
X = train[['High_Last_7_Days', '%_Diff_From_High_Last_7_Days', 'Low_Last_7_Days', '%_Diff_From_Low_Last_7_Days']]
y_high = train['%_Diff_From_High_Next_5_Days']
y_low = train['%_Diff_From_Low_Next_5_Days']

# Split data into training and testing sets
X_train, X_test, y_high_train, y_high_test, y_low_train, y_low_test = train_test_split(X, y_high, y_low, test_size=0.2, random_state=42)

# Train the Random Forest model
model_high = RandomForestRegressor(n_estimators=100, random_state=42)
model_high.fit(X_train, y_high_train)

model_low = RandomForestRegressor(n_estimators=100, random_state=42)
model_low.fit(X_train, y_low_train)

# Predict and evaluate
y_high_pred = model_high.predict(X_test)
y_low_pred = model_low.predict(X_test)

print("High Prediction MSE:", mean_squared_error(y_high_test, y_high_pred))
print("High Prediction R2:", r2_score(y_high_test, y_high_pred))

print("Low Prediction MSE:", mean_squared_error(y_low_test, y_low_pred))
print("Low Prediction R2:", r2_score(y_low_test, y_low_pred))

'''Results : High Prediction MSE: 2.0770569037427093
High Prediction R2: 0.8520673740582533
Low Prediction MSE: 1.2233847776738007
Low Prediction R2: 0.9425372798847088 '''




