import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def model_func(x, a, b, c):
    return a * x**2 + b * x + c


def main():
    x_data = np.linspace(-10, 10, 100)
    y_data = 2 * x_data**2 + 3 * x_data + 5 + np.random.normal(0, 10, x_data.shape)

    popt, pcov = curve_fit(model_func, x_data, y_data)
    a_opt, b_opt, c_opt = popt
    print(f"Estimated coefficients: a={a_opt:.3f}, b={b_opt:.3f}, c={c_opt:.3f}")

    y_fit = model_func(x_data, a_opt, b_opt, c_opt)

    plt.scatter(x_data, y_data, label='Data', color='blue', alpha=0.5)
    plt.plot(x_data, y_fit, label='Fitted curve', color='red', linewidth=2)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.title('Curve Fitting using scipy.optimize.curve_fit')
    plt.show()


if __name__ == "__main__":
    main()
