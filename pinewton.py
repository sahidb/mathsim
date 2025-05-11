import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Define the function and its derivative
def f(x):
    return np.tan(x / 4) - 1

def df(x):
    return 0.25 / np.cos(x / 4) ** 2

# Newton-Raphson iteration
def newton_raphson(x0, tol=1e-10, max_iter=10):
    xs = [x0]
    for _ in range(max_iter):
        x1 = x0 - f(x0) / df(x0)
        xs.append(x1)
        if abs(x1 - x0) < tol:
            break
        x0 = x1
    return xs

# Initial guess and run Newton-Raphson
x0 = 3.0
xs = newton_raphson(x0, max_iter=8)

# Prepare for animation
x_vals = np.linspace(2.5, 4.5, 400)
y_vals = f(x_vals)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x_vals, y_vals, label='f(x) = tan(x/4) - 1')
ax.axhline(0, color='gray', lw=1)
ax.set_ylim(-2, 2)
ax.set_xlabel('x')
ax.set_ylabel('f(x)')
ax.set_title("Newton's Method to Approximate π")

point, = ax.plot([], [], 'ro', label='Current Estimate')
lines = []

def init():
    point.set_data([], [])
    for line in lines:
        line.remove()
    lines.clear()
    return [point]

def animate(i):
    if i == 0:
        return init()
    x_curr = xs[i-1]
    y_curr = f(x_curr)
    point.set_data([x_curr], [y_curr])
    # Draw tangent line
    slope = df(x_curr)
    x_tan = np.linspace(x_curr-0.5, x_curr+0.5, 10)
    y_tan = slope * (x_tan - x_curr) + y_curr
    line, = ax.plot(x_tan, y_tan, 'g--', alpha=0.5)
    lines.append(line)
    return [point, line]

ani = animation.FuncAnimation(fig, animate, frames=len(xs), init_func=init, blit=True, repeat=False, interval=1200)

# Show legend and π value
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
fig.text(0.5, 0.95, f"Final π estimate: {xs[-1]:.10f}", ha='center', va='top', fontsize=12)
plt.tight_layout(rect=[0, 0, 0.85, 0.92])
plt.show()
