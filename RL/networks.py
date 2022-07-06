import os
import threading
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LSTM, Conv1D,BatchNormalization, Dropout, MaxPooling1D, Flatten
from tensorflow.keras.optimizers import SGD
from tensorflow.keras import backend


class Network:
    lock = threading.Lock()


    def __init__(self, input_dim=0, output_dim=0, lr=0.01, shared_network=None, activation='sigmoid', loss='mse'):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.lr = lr
        self.shared_network = shared_network
        self.activation = activation
        self.loss = loss
        self.model = None
        self.graph = self.DummyGraph()
        self.sess = None

    class DummyGraph:
        def as_default(self):
            return self

        def __enter__(self):
            pass

        def __exit__(self, type, value, traceback):
            pass

    def set_session(self, sess):
        pass

    def predict(self, sample):
        with self.lock:
            with self.graph.as_default():
                if self.sess is not None:
                    self.set_session(self.sess)
                return self.model.predict(sample).flatten()

    def train_on_batch(self,x, y):
        loss = 0.
        with self.lock:
            with self.graph.as_default():
                if self.sess is not None:
                    self.set_session(self.sess)
                loss = self.model.train_on_batch(x,y)
        return loss

    def save_model(self, model_path):
        if model_path is not None and self.model is not None:
            self.model.save_weights(model_path, overwrite=True)

    def load_model(self, model_path):
        if model_path is not None:
            self.model.load_weights(model_path)

