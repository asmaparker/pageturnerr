import numpy as np
import matplotlib.pyplot as plt

# Create a figure and axis
plt.figure(figsize=(10, 10))

# Parameters for sine and cosine functions
A = 1
B = 2
C = 0
D = 0
t = np.linspace(0, 2*np.pi, 1000)

# Sine and Cosine Waves
x_sin = A * np.sin(B * t + C) + D
y_cos = A * np.cos(B * t + C) + D

# Plotting Sine and Cosine
plt.plot(t, x_sin, label='Sine Wave', color='blue')
plt.plot(t, y_cos, label='Cosine Wave', color='red')

# Lissajous Curve Parameters
a = 3
b = 2
delta = np.pi / 2

# Lissajous Curve
x_lissajous = A * np.sin(a * t + delta)
y_lissajous = B * np.sin(b * t)

# Plotting Lissajous Curve
plt.plot(x_lissajous, y_lissajous, label='Lissajous Curve', color='green')

# Labels and Title
plt.title('Trigonometric Art')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.legend()

# Show Plot
plt.grid(True)
plt.show()
