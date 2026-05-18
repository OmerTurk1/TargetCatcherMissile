import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from calculations import calc_collision

# --- SIMULATION PARAMETERS ---
dt = 0.005                # Time step between each frame (seconds)
max_steps = 5000         # Maximum number of simulation steps
collision_threshold = 0.5 # Maximum distance to consider a successful intercept

# Target Parameters
P = np.array([0.0, 0.0])
target_speed = 10.0
angle = np.radians(np.random.uniform(0, 360))
V = np.array([np.cos(angle), np.sin(angle)]) * target_speed
max_turn_angle = np.radians(5)

# Bullet (Interceptor) Parameters
L = np.array([20.0, 30.0])
bullet_speed = 11.0
bullet_pos = L.copy()

# --- DATA COLLECTION (ALGORITHM RUNS FIRST) ---
target_history = [P.copy()]
bullet_history = [bullet_pos.copy()]
prediction_history = []  # Instantaneous predicted impact points

is_intercepted = False

for step in range(max_steps):
    # 1. TARGET MOVEMENT: Add a small random deviation to the current angle
    turn = np.random.uniform(-max_turn_angle, max_turn_angle)
    angle += turn
    V = np.array([np.cos(angle), np.sin(angle)]) * target_speed
    P += V * dt
    target_history.append(P.copy())
    
    # 2. INSTANTANEOUS COLLISION PREDICTION (Guidance System)
    B, M_d, t_st = calc_collision(P, V, bullet_pos, bullet_speed)
        
    prediction_history.append(B.copy())
    
    # 3. BULLET MOVEMENT: Advance towards the calculated direction
    bullet_pos += M_d * dt
    bullet_history.append(bullet_pos.copy())
    
    # 4. COLLISION CHECK
    distance = np.linalg.norm(P - bullet_pos)
    if distance < collision_threshold:
        is_intercepted = True
        break

# Convert lists to NumPy arrays for easier plotting
target_history = np.array(target_history)
bullet_history = np.array(bullet_history)
prediction_history = np.array(prediction_history)
total_frames = len(prediction_history)

print(f"Simulation finished. Took {total_frames} steps. Interception status: {is_intercepted}")

# --- MATPLOTLIB VISUALIZATION PHASE ---
fig, ax = plt.subplots(figsize=(9, 9))
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)

# Set plot limits dynamically
all_pts = np.vstack([target_history, bullet_history])
ax.set_xlim(np.min(all_pts[:, 0]) - 5, np.max(all_pts[:, 0]) + 5)
ax.set_ylim(np.min(all_pts[:, 1]) - 5, np.max(all_pts[:, 1]) + 5)

# Static Elements
ax.plot(L[0], L[1], marker='^', color='red', markersize=10)

# Dynamic Elements
target_trail, = ax.plot([], [], linestyle='-', color='blue', alpha=0.4, linewidth=2, label='Target Actual Path')
bullet_trail, = ax.plot([], [], linestyle='-', color='red', alpha=0.4, linewidth=2, label='Bullet Actual Path')
pred_line, = ax.plot([], [], linestyle='--', color='green', alpha=0.3, label='Instantaneous Prediction Line')

target_dot, = ax.plot([], [], marker='o', color='blue', markersize=8, label='Target')
bullet_dot, = ax.plot([], [], marker='*', color='red', markersize=8, label='Bullet')
pred_dot, = ax.plot([], [], marker='X', color='green', markersize=10, label='Predicted Impact Point')

ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), shadow=True)
ax.set_title("Dynamic Target Tracking and Interception Simulation", fontsize=12, weight='bold')

def init():
    target_trail.set_data([], [])
    bullet_trail.set_data([], [])
    pred_line.set_data([], [])
    target_dot.set_data([], [])
    bullet_dot.set_data([], [])
    pred_dot.set_data([], [])
    return target_dot, bullet_dot, pred_dot, target_trail, bullet_trail, pred_line

def update(frame):
    # Freeze the animation after the interception point
    f = min(frame, total_frames - 1)
    
    # Update trails
    target_trail.set_data(target_history[:f+1, 0], target_history[:f+1, 1])
    bullet_trail.set_data(bullet_history[:f+1, 0], bullet_history[:f+1, 1])
    
    # Dashed green line from current bullet position to predicted impact point
    pred_line.set_data([bullet_history[f, 0], prediction_history[f, 0]], 
                       [bullet_history[f, 1], prediction_history[f, 1]])
    
    # Update object positions
    target_dot.set_data([target_history[f, 0]], [target_history[f, 1]])
    bullet_dot.set_data([bullet_history[f, 0]], [bullet_history[f, 1]])
    pred_dot.set_data([prediction_history[f, 0]], [prediction_history[f, 1]])
        
    return target_dot, bullet_dot, pred_dot, target_trail, bullet_trail, pred_line

# Run and save the animation
ani_live = FuncAnimation(
    fig, update, 
    frames=total_frames + 20, 
    init_func=init, 
    blit=True, 
    interval=dt*1000, 
    repeat=True
)

gif_frames = list(range(0, total_frames, 5))

last_frame = total_frames - 1
gif_frames.extend([last_frame] * 4) # 20 / 5 = 4 kare donma yeterli olacaktır

ani_gif = FuncAnimation(
    fig, update, 
    frames=gif_frames, 
    init_func=init, 
    blit=True
)

print("GIF is saving, please wait...")
ani_gif.save('hit_animation.gif', writer='pillow', fps=35)
print("GIF saved successfully!")

plt.show()