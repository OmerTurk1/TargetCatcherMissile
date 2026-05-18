import numpy as np

def calc_collision(P, V, L, M):
    """
    P : target location vector
    L : target speed vector
    V : launcher location vector
    M : launcher speed magnitude
    """
    D = P - L
    a = np.dot(V, V) - M**2
    b = 2 * np.dot(V, D)
    c = np.dot(D, D)

    delta = b**2 - 4 * a * c
    if delta < 0:
        return fallback_direct_aim(D,P,M)
    
    t1 = (-b + np.sqrt(delta)) / (2 * a)
    t2 = (-b - np.sqrt(delta)) / (2 * a)
    
    valid_times = [t for t in [t1, t2] if t > 0]
    if not valid_times:
        return fallback_direct_aim(D,P,M)
    
    t_st = min(valid_times)
    B = P + t_st * V
    M_d = (B - L) / t_st

    return B, M_d, t_st

def fallback_direct_aim(D,P,M):
    distance = np.linalg.norm(D)
    if distance < 1e-8:
        return P, np.zeros_like(P), 0.0
    
    M_d = (D / distance) * M 
    t_st = distance / M
    return P, M_d, t_st