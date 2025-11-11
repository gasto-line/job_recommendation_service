# fake_model.py
import numpy as np
import random

class FakeFastTextModel:
    def __init__(self, dim=300, seed=None):
        self.dim = dim
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def get_word_vector(self, word):
        """Simulate FastText's get_word_vector() output"""
        return np.random.rand(self.dim).astype(np.float32)

    def predict(self, text):
        """Optional: simulate language prediction"""
        langs = ['__label__en', '__label__fr', '__label__es']
        probs = np.random.dirichlet(np.ones(len(langs)))
        return [langs], [probs]