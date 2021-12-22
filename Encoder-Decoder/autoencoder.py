import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

import tensorflow as tf

import matplotlib.pyplot as plt

def Encoder_Decoder(shape):
    input = tf.keras.Input(shape=(shape,))

    encoded = tf.keras.layers.Dense(16, activation='sigmoid')(input)

    encoded = tf.keras.layers.Dense(8, activation='relu')(encoded)

    encoded = tf.keras.layers.Dense(2, activation='relu')(encoded)

    decoded = tf.keras.layers.Dense(8, activation='relu')(encoded)

    decoded = tf.keras.layers.Dense(16, activation='relu')(decoded)
    decoded = tf.keras.layers.Dense(x_train.shape[1], activation='linear')(decoded)

    autoencoder = tf.keras.Model(input, decoded)
    autoencoder.summary()
    autoencoder.compile(optimizer='adam', loss='mse', metrics=[])

    callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=5, verbose=1,  restore_best_weights=True)
    return autoencoder, callback

def calculate_mses(model, x):
    return mean_squared_error(np.transpose(model(x).numpy()), np.transpose(x), multioutput='raw_values')


def calculate_mse_limit(model, x):
    mse = calculate_mses(model, x)
    counts, bins = np.histogram(mse, bins=30)
    print(counts)
    plt.hist(mse, bins=30)
    plt.grid()
    plt.title('Distribución error decodificator')
    plt.savefig('density_estimation.png')

    return bins[1], mse



if __name__ == '__main__':

    df = pd.read_csv('./train.csv')
    df.drop(columns=['Id'],inplace=True)
    numeric_columns = df.dtypes[(df.dtypes == 'float') | (df.dtypes == 'int')].index
    df = df[numeric_columns]
    df.fillna(df.mean(), inplace=True)
    x = df.values
    scaler = StandardScaler()
    x = scaler.fit_transform(x)
    print('### DATA SCALED ###')
    x_train = x
    print('### TRAIN TEST SPLITED ###')


    print('### TRAINNING AUTOENCODER ###')
    autoencoder, callback = Encoder_Decoder(x.shape[1])
    history = autoencoder.fit(x_train, x_train, epochs=30, batch_size=64,
                                  shuffle=True, verbose=1, callbacks=[callback])

    limit, mse = calculate_mse_limit(autoencoder, x_train)

    indexes = mse > limit

    print('Indices casos anomalos')
    print(indexes)

