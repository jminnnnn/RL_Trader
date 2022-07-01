from networks import Network
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LSTM, Conv1D\
    ,Conv2D, BatchNormalization, Dropout, MaxPooling1D, Flatten, MaxPooling2D
from tensorflow.keras.optimizers import SGD
from tensorflow.keras import backend
import numpy as np


class CNN(Network):
    def __init__(self, *args, num_steps=1, **kwargs):
        super().__init__(*args, **kwargs)
        with self.graph.as_default():
            if self.sess is not None:
                self.set_session(self.sess)
            self.num_steps = num_steps
            _input = None
            _output = None
            if self.shared_network is None:
                _input = Input((self.num_steps, self.input_dim, 1))
                _output = self.get_network_head(input).output
            else:
                _input = self.shared_network.input
                _output = self.shared_network.output
            _output = Dense(self.output_dim, activation = self.activation,
                           kernel_initializer='random_normal')(_output)
            self.model = Model(_input, _output)
            self.model.compile(optimizer=SGD(lr=self.lr), loss=self.loss)

    def get_network_head(self, _input):
        output = Conv1D(256, kernel_size=(1,5), padding_='same',
                         activation='sigmoid', kernel_initializer='random_normal')(_input)
        output = BatchNormalization()(output)
        output = MaxPooling1D(pool_size=(1, 2))(output)
        output = Dropout(0.1)(output)
        output = Conv1D(64, kernel_size=5,
                        padding='same', activation='sigmoid',
                        kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = MaxPooling1D(pool_size=2, padding='same')(output)
        output = Dropout(0.1)(output)
        output = Conv1D(32, kernel_size=5,
                        padding='same', activation='sigmoid',
                        kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = MaxPooling1D(pool_size=2, padding='same')(output)
        output = Dropout(0.1)(output)
        output = Flatten()(output)
        return Model(_input, output)

    def train_on_batch(self, x, y):
        x = np.array(x).reshape((-1, self.num_steps, self.input_dim, 1))
        return super().train_on_batch(x, y)

    def predict(self, sample):
        sample = np.array(sample).reshape(
            (-1, self.num_steps, self.input_dim, 1))
        return super().predict(sample)
