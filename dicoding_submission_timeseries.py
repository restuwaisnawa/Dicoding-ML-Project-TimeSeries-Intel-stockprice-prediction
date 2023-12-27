# -*- coding: utf-8 -*-
"""Dicoding_Submission_TimeSeries.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YruSYwNbzYV4vwiC433TAcv5UajmTDOZ

##**TIME SERIES ML SUBMISSION**

**I GEDE KADEK RESTU KARTANA WAISNAWA**

Dicoding ID: **restuwaisnawa**

Email: **restuwaisnawa@gmail.com**

Dataset link: https://www.kaggle.com/datasets/tosinabase/intel-stock-prices-historical-data-intc
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import Huber
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

#get dataset
df = pd.read_csv('INTC.csv')
df.head()

#dataset check
df.info()

#plot data time series
dates = df['Date'].values
price = df['Close'].values

plt.figure(figsize=(15,5))
plt.plot(dates, price)
plt.title('Intel Stock Prices Time Series', fontsize=20);

#data normalization
scaler = MinMaxScaler()
price = price.reshape(-1,1)
price = scaler.fit_transform(price)

#train and validation set split
X_train, X_test, y_train, y_test = train_test_split(price, dates, test_size=0.2, shuffle=False)

#change data format for model train
def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

train_set = windowed_dataset(X_train, window_size=60, batch_size=100, shuffle_buffer=1000)
test_set = windowed_dataset(X_test, window_size=60, batch_size=100, shuffle_buffer=1000)

#making model
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(64, return_sequences=True, input_shape = [None, 1]),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1)
])

#MAE Threshold Check
mae_threshold = (price.max() - price.min()) * 10/100
print(mae_threshold)

#model compile
model.compile(loss='Huber',
              optimizer=Adam(learning_rate=1.0000e-04),
              metrics=['mae'])

#callbacks
class MaeStop(tf.keras.callbacks.Callback):
    def __init__(self, threshold_mae):
        self.threshold_mae = threshold_mae

    def on_epoch_end(self, epoch, logs=None):
        mae = logs.get('mae')

        if mae is not None:
            if mae < self.threshold_mae:
                print(f"MAE < 10% data scale. Training stopped.")
                self.model.stop_training = True

mae_stop = MaeStop(threshold_mae=mae_threshold)

#model training
history = model.fit(
    train_set, epochs=100,
    validation_data=test_set,
    verbose=2,
    callbacks=[mae_stop])

#plot MAE
plt.plot(history.history['mae'], label='Training')
plt.plot(history.history['val_mae'], label='Validation')
plt.title('Plot MAE')
plt.ylabel('Value')
plt.xlabel('Epoch')
plt.legend(loc="lower right")
plt.show()

#plot loss
plt.plot(history.history['loss'], label='Training')
plt.plot(history.history['val_loss'], label='Validation')
plt.title('Plot Loss')
plt.ylabel('Value')
plt.xlabel('Epoch')
plt.legend(loc="upper right")
plt.show()