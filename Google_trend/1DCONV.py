from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Conv1D, GlobalMaxPooling1D, Embedding
from keras import optimizers


class Model:
    def __init__(self):
        pass

    def _build_model(self):
        model = Sequential()
        model.add(Conv1D(filters=250,
                         kernel_size=3,
                         padding='valid',
                         activation='relu',
                         strides=1))
        model.add(GlobalMaxPooling1D())
        model.add(Dense(250))
        model.add(Activation('relu'))