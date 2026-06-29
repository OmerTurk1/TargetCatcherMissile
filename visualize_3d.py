import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from calculations import calc_collision

# Time step between simulation frames in seconds.
dt = 0.01
# Maximum number of simulation steps.
max_steps = 3000
# Maximum allowed distance for a successful interception.
collision_threshold = 0.6

# Initial target position in 3D space.
P = np.array([0.0, 0.0, 10.0])
# Constant target speed.
target_speed = 10.0

# Initial heading direction defined by azimuth and elevation angles.
azimuth = np.radians(np.random.uniform(0, 360))
# Initial elevation angle for the target trajectory.
elevation = np.radians(np.random.uniform(10, 40))
V = np.array([
    np.cos(elevation) * np.cos(azimuth),
    np.cos(elevation) * np.sin(azimuth),
    np.sin(elevation)
]) * target_speed
# Maximum random turn angle applied at each simulation step.
max_turn_angle = np.radians(4)

# Initial missile position in 3D space.
L = np.array([40.0, 50.0, 0.0])
# Missile speed.
bullet_speed = 14.0
# Current missile position.
bullet_pos = L.copy()

target_history = [P.copy()]
bullet_history = [bullet_pos.copy()]
prediction_history = []

is_intercepted = False

for step in range(max_steps):
    azimuth += np.random.uniform(-max_turn_angle, max_turn_angle)
    elevation += np.random.uniform(-max_turn_angle, max_turn_angle)
    elevation = np.clip(elevation, np.radians(-60), np.radians(60))

    V = np.array([
        np.cos(elevation) * np.cos(azimuth),
        np.cos(elevation) * np.sin(azimuth),
        np.sin(elevation)
    ]) * target_speed

    P += V * dt
    target_history.append(P.copy())

    B, M_d, t_st = calc_collision(P, V, bullet_pos, bullet_speed)
    prediction_history.append(B.copy())

    bullet_pos += M_d * bullet_speed * dt
    bullet_history.append(bullet_pos.copy())

    distance = np.linalg.norm(P - bullet_pos)
    if distance < collision_threshold:
        is_intercepted = True
        break

target_history = np.array(target_history)
bullet_history = np.array(bullet_history)
prediction_history = np.array(prediction_history)
total_frames = len(prediction_history)

print(f"Simulation finished. Step count: {total_frames}. Interception status: {is_intercepted}")

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.grid(True, linestyle='--', alpha=0.5)

# Dynamic bounds for the 3D plot based on the recorded trajectories.
all_pts = np.vstack([target_history, bullet_history])
ax.set_xlim(np.min(all_pts[:, 0]) - 5, np.max(all_pts[:, 0]) + 5)
ax.set_ylim(np.min(all_pts[:, 1]) - 5, np.max(all_pts[:, 1]) + 5)
ax.set_zlim(np.min(all_pts[:, 2]) - 5, np.max(all_pts[:, 2]) + 5)

# Static launch point for the missile.
ax.plot([L[0]], [L[1]], [L[2]], marker='^', color='red', markersize=10, label='Missile Ramp')

# Dynamic animated elements for the target, missile, and prediction line.
target_trail, = ax.plot([], [], [], linestyle='-', color='blue', alpha=0.4, linewidth=2, label='Target Path')
bullet_trail, = ax.plot([], [], [], linestyle='-', color='red', alpha=0.4, linewidth=2, label='Missile Path')
pred_line, = ax.plot([], [], [], linestyle='--', color='green', alpha=0.3, label='Instant Prediction')

target_dot, = ax.plot([], [], [], marker='o', color='blue', markersize=8, label='Target')
bullet_dot, = ax.plot([], [], [], marker='*', color='red', markersize=8, label='Missile')
pred_dot, = ax.plot([], [], [], marker='X', color='green', markersize=10, label='Predicted Impact Point')

ax.set_xlabel('X Axis (m)')
ax.set_ylabel('Y Axis (m)')
ax.set_zlabel('Z Axis (Height - m)')
ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
ax.set_title('3D Rotating Target Tracking and Interception Simulation', fontsize=12, weight='bold')

def init():
    """Reset the animated artists to their initial empty state."""
    target_trail.set_data([], [])
    target_trail.set_3d_properties([])
    bullet_trail.set_data([], [])
    bullet_trail.set_3d_properties([])
    pred_line.set_data([], [])
    pred_line.set_3d_properties([])
    
    target_dot.set_data([], [])
    target_dot.set_3d_properties([])
    bullet_dot.set_data([], [])
    bullet_dot.set_3d_properties([])
    pred_dot.set_data([], [])
    pred_dot.set_3d_properties([])
    return target_dot, bullet_dot, pred_dot, target_trail, bullet_trail, pred_line

def update(frame):
    """Advance the animation to the requested frame and rotate the camera."""
    f = min(frame, total_frames - 1)
    target_trail.set_data(target_history[:f+1, 0], target_history[:f+1, 1])
    target_trail.set_3d_properties(target_history[:f+1, 2])
    
    bullet_trail.set_data(bullet_history[:f+1, 0], bullet_history[:f+1, 1])
    bullet_trail.set_3d_properties(bullet_history[:f+1, 2])
    
    pred_line.set_data([bullet_history[f, 0], prediction_history[f, 0]], 
                       [bullet_history[f, 1], prediction_history[f, 1]])
    pred_line.set_3d_properties([bullet_history[f, 2], prediction_history[f, 2]])
    
    target_dot.set_data([target_history[f, 0]], [target_history[f, 1]])
    target_dot.set_3d_properties([target_history[f, 2]])
    
    bullet_dot.set_data([bullet_history[f, 0]], [bullet_history[f, 1]])
    bullet_dot.set_3d_properties([bullet_history[f, 2]])
    
    pred_dot.set_data([prediction_history[f, 0]], [prediction_history[f, 1]])
    pred_dot.set_3d_properties([prediction_history[f, 2]])
    
    cam_elevation = 25
    cam_azimuth = -45 + (frame * 0.4)
    
    ax.view_init(elev=cam_elevation, azim=cam_azimuth)
    
    return target_dot, bullet_dot, pred_dot, target_trail, bullet_trail, pred_line

step_size = max(1, total_frames // 80)
base_frames = list(range(0, total_frames, step_size))

last_frame = total_frames - 1
extended_frames = base_frames + [last_frame] * 20

ani_gif = FuncAnimation(
    fig, update, 
    frames=extended_frames, 
    init_func=init, 
    blit=False
)

print("Camera rotated 3D GIF is saving, please wait...")
ani_gif.save('hit_animation_3d_rotated.gif', writer='pillow', fps=15)
print("'hit_animation_3d_rotated.gif' successfully saved!")

plt.show()