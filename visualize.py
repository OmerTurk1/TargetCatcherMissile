import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from calculations import calc_collision

# --- SİMÜLASYON PARAMETRELERİ ---
dt = 0.005               # Her adım arasındaki zaman (saniye)
max_steps = 5000        # Maksimum simülasyon adım sayısı
collision_threshold = 0.5 # Çarpışma sayılması için gereken maksimum mesafe

# Hedef Parametreleri
P = np.array([0.0, 0.0])
target_speed = 10.0
angle = np.radians(np.random.uniform(0,360))
V = np.array([np.cos(angle), np.sin(angle)]) * target_speed
max_turn_angle = np.radians(5)

L = np.array([20.0, 30.0])
bullet_speed = 11.0
bullet_pos = L.copy()

# --- VERİ TOPLAMA (ÖNCE ALGORİTMA ÇALIŞIYOR) ---
target_history = [P.copy()]
bullet_history = [bullet_pos.copy()]
prediction_history = [] # Anlık tahmin noktaları

is_intercepted = False

for step in range(max_steps):
    # 1. HEDEF HAREKETİ: Mevcut açıya rastgele küçük bir sapma ekle
    turn = np.random.uniform(-max_turn_angle, max_turn_angle)
    angle += turn
    V = np.array([np.cos(angle), np.sin(angle)]) * target_speed
    P += V * dt
    target_history.append(P.copy())
    
    # 2. ANLIK ÇARPIŞMA TAHMİNİ (Güdüm Sistemi)
    B, M_d, t_st = calc_collision(P, V, bullet_pos, bullet_speed)
        
    prediction_history.append(B.copy())
    
    # 3. MERMİ HAREKETİ: Hesaplanan yöne doğru ilerle
    bullet_pos += M_d * dt
    bullet_history.append(bullet_pos.copy())
    
    # 4. ÇARPIŞMA KONTROLÜ
    distance = np.linalg.norm(P - bullet_pos)
    if distance < collision_threshold:
        is_intercepted = True
        break

# Listeleri NumPy array'e çevirelim (Kolay çizim için)
target_history = np.array(target_history)
bullet_history = np.array(bullet_history)
prediction_history = np.array(prediction_history)
total_frames = len(prediction_history)

print(f"Simülasyon bitti. {total_frames} adım sürdü. Çarpışma durumu: {is_intercepted}")

# --- MATPLOTLIB GÖRSELLEŞTİRME AŞAMASI ---
fig, ax = plt.subplots(figsize=(9, 9))
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)

# Grafik sınırlarını belirle
all_pts = np.vstack([target_history, bullet_history])
ax.set_xlim(np.min(all_pts[:,0]) - 5, np.max(all_pts[:,0]) + 5)
ax.set_ylim(np.min(all_pts[:,1]) - 5, np.max(all_pts[:,1]) + 5)

# Sabit Elemanlar
ax.plot(L[0], L[1], marker='^', color='red', markersize=10)

# Dinamik Elemanlar
target_trail, = ax.plot([], [], linestyle='-', color='blue', alpha=0.4, linewidth=2, label='Hedef Gerçek Rotası')
bullet_trail, = ax.plot([], [], linestyle='-', color='red', alpha=0.4, linewidth=2, label='Mermi Gerçek Rotası')
pred_line, = ax.plot([], [], linestyle='--', color='green', alpha=0.3, label='Anlık Tahmin Hattı')

target_dot, = ax.plot([], [], marker='o', color='blue', markersize=8, label='Hedef')
bullet_dot, = ax.plot([], [], marker='*', color='red', markersize=8, label='Mermi')
pred_dot, = ax.plot([], [], marker='X', color='green', markersize=10, label='Anlık Tahmini Vuruş Noktası')

ax.legend(loc='upper right', shadow=True)
ax.set_title("Dinamik Hedef Takip ve Vuruş Simülasyonu", fontsize=12, weight='bold')

def init():
    target_trail.set_data([], [])
    bullet_trail.set_data([], [])
    pred_line.set_data([], [])
    target_dot.set_data([], [])
    bullet_dot.set_data([], [])
    pred_dot.set_data([], [])
    return target_dot, bullet_dot, pred_dot, target_trail, bullet_trail, pred_line

def update(frame):
    # Çarpışma anından sonra dondur
    f = min(frame, total_frames - 1)
    
    # İzleri güncelle
    target_trail.set_data(target_history[:f+1, 0], target_history[:f+1, 1])
    bullet_trail.set_data(bullet_history[:f+1, 0], bullet_history[:f+1, 1])
    
    # Anlık mermi konumundan anlık tahmini noktaya kesikli yeşil çizgi
    pred_line.set_data([bullet_history[f, 0], prediction_history[f, 0]], 
                       [bullet_history[f, 1], prediction_history[f, 1]])
    
    # Nesne konumlarını güncelle
    target_dot.set_data([target_history[f, 0]], [target_history[f, 1]])
    bullet_dot.set_data([bullet_history[f, 0]], [bullet_history[f, 1]])
    pred_dot.set_data([prediction_history[f, 0]], [prediction_history[f, 1]])
        
    return target_dot, bullet_dot, pred_dot, target_trail, bullet_trail, pred_line

# Animasyonu oynat
ani = FuncAnimation(fig, update, frames=total_frames + 20, init_func=init, blit=True, interval=dt*1000, repeat=True)
plt.show()