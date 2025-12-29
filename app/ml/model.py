class DummyModel:
    def predict(self, X):
        return [sum(X[0])]


def load_model():
    return DummyModel()
