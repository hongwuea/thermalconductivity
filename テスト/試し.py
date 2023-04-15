import numpy as np
from scipy.optimize import root, brentq

print(brentq(lambda ρ: np.exp(-1 / ρ) + np.exp(-2 / ρ) - 1, 0.001, 100))
print(brentq(lambda ρ: np.exp(-1 / ρ) + np.exp(-2 / ρ) - 1, 0.001, 100))
print('xxx')
print('xxx')
