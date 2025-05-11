import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Function to simulate pi using Monte Carlo method
def monte_carlo_pi(n):
    x = np.random.uniform(0, 1, n)
    y = np.random.uniform(0, 1, n)
    inside_circle = (x**2 + y**2) <= 1
    pi_estimate = 4 * np.sum(inside_circle) / n
    return pi_estimate, x, y, inside_circle

# Function to animate the Monte Carlo simulation
def animate_monte_carlo(n_points=1000, interval=10):
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Monte Carlo Simulation for Pi')
    
    # Add a quarter circle to the plot
    theta = np.linspace(0, np.pi/2, 100)
    x_circle = np.cos(theta)
    y_circle = np.sin(theta)
    ax.plot(x_circle, y_circle, color='green')
    
    # Create empty scatter plots for points inside and outside the circle
    scatter_inside = ax.scatter([], [], color='blue', s=1, label='Inside')
    scatter_outside = ax.scatter([], [], color='red', s=1, label='Outside')
    
    # Text to display current pi estimate
    pi_text = ax.text(0.02, 0.80, '', transform=ax.transAxes)
    
    # Generate all random points in advance
    x = np.random.uniform(0, 1, n_points)
    y = np.random.uniform(0, 1, n_points)
    inside_circle = (x**2 + y**2) <= 1
    
    def update(frame):
        # Update points displayed based on current frame
        current_x_inside = x[:frame][inside_circle[:frame]]
        current_y_inside = y[:frame][inside_circle[:frame]]
        current_x_outside = x[:frame][~inside_circle[:frame]]
        current_y_outside = y[:frame][~inside_circle[:frame]]
        
        scatter_inside.set_offsets(np.c_[current_x_inside, current_y_inside])
        scatter_outside.set_offsets(np.c_[current_x_outside, current_y_outside])
        
        # Update pi estimate text
        if frame > 0:
            current_pi = 4 * np.sum(inside_circle[:frame]) / frame
            pi_text.set_text(f'Points: {frame}\nπ estimate: {current_pi:.6f}')
        
        return scatter_inside, scatter_outside, pi_text
    
    ax.legend()
    ani = animation.FuncAnimation(fig, update, frames=n_points, interval=interval, blit=True, repeat=False)
    plt.show()
    
# Run the animation with 2000 points, updating every 20ms
animate_monte_carlo(2000, 20)