import time
import numpy as np
import matplotlib.pyplot as plt
from gplearn.genetic import SymbolicRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


def time_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} execution time: {end - start:.6f} seconds")
        return result
    return wrapper


@time_decorator
def symbolic_processing(X_train, X_test, y_train, y_test):
    model = SymbolicRegressor(
        population_size=5000,
        generations=3000,
        function_set=(
            'add', 'sub', 'mul', 'div',
            'sqrt', 'log', 'abs', 'neg', 'inv',
            'max', 'min', 'sin', 'cos', 'tan'
        ),
        max_samples=0.9,
        n_jobs=1,
        verbose=1,
        random_state=42,
        parsimony_coefficient=0.001,
        tournament_size=20,
        stopping_criteria=0.0,
        const_range=(-1., 1.),
        init_depth=(2, 6),
        init_method='half and half',
        metric='mean absolute error',
        p_crossover=0.9,
        p_subtree_mutation=0.01,
        p_hoist_mutation=0.01,
        p_point_mutation=0.01,
        p_point_replace=0.05,
        feature_names=None,
        warm_start=False,
        low_memory=False,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("MSE:", mean_squared_error(y_test, y_pred))
    print("Best expression:", model._program)

    X_plot = np.linspace(-10, 10, 200).reshape(-1, 1)
    y_true = (
        np.sin(X_plot[:, 0])
        * np.log(np.abs(X_plot[:, 0]) + 1)
        + np.tanh(X_plot[:, 0] ** 2 - 3)
    )
    y_model = model.predict(X_plot)

    return X_plot, y_true, y_model


if __name__ == "__main__":
    np.random.seed(42)
    X = np.linspace(-10, 10, 200).reshape(-1, 1)
    y = (
        np.sin(X[:, 0])
        * np.log(np.abs(X[:, 0]) + 1)
        + np.tanh(X[:, 0] ** 2 - 3)
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    X_plot, y_true, y_model = symbolic_processing(X_train, X_test, y_train, y_test)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(X_plot, y_true, label="True Function", color="blue")
    ax.plot(X_plot, y_model, label="Predicted Expression", color="red", linestyle="--")
    ax.scatter(X_train, y_train, label="Training Data", alpha=0.6, s=10)
    ax.legend()
    ax.set_title("Symbolic Regression — gplearn")
    ax.set_xlabel("X")
    ax.set_ylabel("y")
    ax.grid(True)
    plt.tight_layout()
    plt.show()
