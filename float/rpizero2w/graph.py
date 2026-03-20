import matplotlib.pyplot as plt
import numpy as np

# x is time is seconds
# y is depth in meterss

xpoints = np.array([1, 8])
ypoints = np.array([3, 10])

plt.plot(xpoints, ypoints, '*')
plt.show()