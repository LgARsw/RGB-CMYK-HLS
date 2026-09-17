import math
from model.clipping import apply_clipping, apply_scaling

# --- НАСТРОЙКИ СТАНДАРТОВ ОСВЕЩЕНИЯ (ТОЧКИ БЕЛОГО И МАТРИЦЫ) ---
ILLUMINANTS = {
    "D65": {
        "white": (95.047, 100.000, 108.883),
        "rgb_to_xyz": [
            [0.412453, 0.357580, 0.180423],
            [0.212671, 0.715160, 0.072169],
            [0.019334, 0.119193, 0.950227]
        ],
        "xyz_to_rgb": [
            [3.2406, -1.5372, -0.4986],
            [-0.9689, 1.8758, 0.0415],
            [0.0557, -0.2040, 1.0570]
        ]
    },
    "D50": {
        "white": (96.422, 100.000, 82.521),
        "rgb_to_xyz": [
            [0.436074, 0.385064, 0.143080],
            [0.222504, 0.716870, 0.060626],
            [0.013932, 0.097104, 0.714173]
        ],
        "xyz_to_rgb": [
            [3.133856, -1.616867, -0.490615],
            [-0.978768, 1.916142, 0.033454],
            [0.071945, -0.228991, 1.405243]
        ]
    },
    "E": {
        "white": (100.000, 100.000, 100.000),
        "rgb_to_xyz": [
            [0.490000, 0.310000, 0.200000],
            [0.176970, 0.812400, 0.010630],
            [0.000000, 0.010000, 0.990000]
        ],
        "xyz_to_rgb": [
            [2.364614, -0.896541, -0.468073],
            [-0.515166, 1.426408, 0.088758],
            [0.005204, -0.014405, 1.009201]
        ]
    }
}


def rgb_to_cmyk(r, g, b, method='GCR'):
    """Перевод RGB -> CMYK"""
    rc, gc, bc = r / 255.0, g / 255.0, b / 255.0
    k = min(1.0 - rc, 1.0 - gc, 1.0 - bc)
    
    if k >= 1.0:
        return 0.0, 0.0, 0.0, 100.0
        
    c = (1.0 - rc - k) / (1.0 - k)
    m = (1.0 - gc - k) / (1.0 - k)
    y = (1.0 - bc - k) / (1.0 - k)
    
    return max(0.0, c) * 100.0, max(0.0, m) * 100.0, max(0.0, y) * 100.0, k * 100.0

def cmyk_to_rgb(c, m, y, k, method='GCR'):
    """Обратный перевод CMYK -> RGB"""
    c_n, m_n, y_n, k_n = c / 100.0, m / 100.0, y / 100.0, k / 100.0
    r = 255.0 * (1.0 - c_n) * (1.0 - k_n)
    g = 255.0 * (1.0 - m_n) * (1.0 - k_n)
    b = 255.0 * (1.0 - y_n) * (1.0 - k_n)
    return int(round(max(0.0, min(255.0, r)))), int(round(max(0.0, min(255.0, g)))), int(round(max(0.0, min(255.0, b))))

def rgb_to_hls(r, g, b):
    """Ручной перевод RGB -> HLS"""
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r_n, g_n, b_n)
    min_c = min(r_n, g_n, b_n)
    
    l = (max_c + min_c) / 2.0
    
    if max_c == min_c:
        h, s = 0.0, 0.0
    else:
        diff = max_c - min_c
        s = diff / (max_c + min_c) if l < 0.5 else diff / (2.0 - max_c - min_c)
            
        if max_c == r_n:
            h = (g_n - b_n) / diff + (6.0 if g_n < b_n else 0.0)
        elif max_c == g_n:
            h = (b_n - r_n) / diff + 2.0
        else:
            h = (r_n - g_n) / diff + 4.0
        h *= 60.0
        
    return h, l * 100.0, s * 100.0

def hls_to_rgb(h, l, s, strategy='Clipping'):
    """Перевод HLS -> RGB строго по градусной блок-схеме"""
    L, S = l / 100.0, s / 100.0
    M2 = L * (1.0 + S) if L < 0.5 else L + S - L * S
    M1 = 2.0 * L - M2
    
    if S == 0.0:
        r, g, b = L, L, L
    else:
        def Value(tc, m1, m2):
            if tc < 0: tc += 360.0
            elif tc >= 360.0: tc -= 360.0
            if tc < 60.0: return m1 + (m2 - m1) * tc / 60.0
            if tc < 180.0: return m2
            if tc < 240.0: return m1 + (m2 - m1) * (240.0 - tc) / 60.0
            return m1

        r = Value(h + 120.0, M1, M2)
        g = Value(h, M1, M2)
        b = Value(h - 120.0, M1, M2)
        
    r_raw, g_raw, b_raw = r * 255.0, g * 255.0, b * 255.0
    if strategy == 'Scaling':
        return apply_scaling(r_raw, g_raw, b_raw)
    else:
        return apply_clipping(r_raw, g_raw, b_raw)

def rgb_to_xyz(r, g, b, illum="D65"):
    """Перевод RGB -> XYZ """
    def F(x):
        return ((x + 0.055) / 1.055) ** 2.4 if x >= 0.04045 else x / 12.92

    rn = F(r / 255.0) * 100.0
    gn = F(g / 255.0) * 100.0
    bn = F(b / 255.0) * 100.0

    M = ILLUMINANTS[illum]["rgb_to_xyz"]
    x = M[0][0] * rn + M[0][1] * gn + M[0][2] * bn
    y = M[1][0] * rn + M[1][1] * gn + M[1][2] * bn
    z = M[2][0] * rn + M[2][1] * gn + M[2][2] * bn
    return x, y, z

def xyz_to_rgb(x, y, z, illum="D65", strategy='Clipping'):
    x_n, y_n, z_n = x / 100.0, y / 100.0, z / 100.0
    M = ILLUMINANTS[illum]["xyz_to_rgb"]
    
    rn = M[0][0] * x_n + M[0][1] * y_n + M[0][2] * z_n
    gn = M[1][0] * x_n + M[1][1] * y_n + M[1][2] * z_n
    bn = M[2][0] * x_n + M[2][1] * y_n + M[2][2] * z_n

    def F_inv(x):
        if x >= 0.0031308:
            return 1.055 * (x ** (1.0 / 2.4)) - 0.055
        return 12.92 * x

    r_out = F_inv(rn) * 255.0
    g_out = F_inv(gn) * 255.0
    b_out = F_inv(bn) * 255.0

    if strategy == 'Scaling':
        return apply_scaling(r_out, g_out, b_out)
    return apply_clipping(r_out, g_out, b_out)

def xyz_to_lab(x, y, z, illum="D65"):
    """Перевод XYZ -> Lab с динамической точкой белого"""
    Xn, Yn, Zn = ILLUMINANTS[illum]["white"]
    
    def F(t):
        return t ** (1.0 / 3.0) if t >= 0.008856 else 7.787 * t + (16.0 / 116.0)

    fx = F(x / Xn)
    fy = F(y / Yn)
    fz = F(z / Zn)

    l = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return l, a, b

def lab_to_xyz(l, a, b, illum="D65"):
    """Обратный перевод Lab -> XYZ"""
    Xn, Yn, Zn = ILLUMINANTS[illum]["white"]

    def F_inv(item):
        if (item ** 3) >= 0.008856:
            return item ** 3
        return (item - 16.0 / 116.0) / 7.787

    fy = (l + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0

    x = F_inv(fx) * Xn
    y = F_inv(fy) * Yn
    z = F_inv(fz) * Zn
    return x, y, z

# ==========================================
# 5. МОДЕЛЬ XYZ ↔ Luv (Строго по формулам)
# ==========================================

def xyz_to_luv(x, y, z, illum="D65"):
    """Перевод XYZ -> Luv"""
    Xn, Yn, Zn = ILLUMINANTS[illum]["white"]
    
    denom = (x + 15.0 * y + 3.0 * z)
    u_prime = (4.0 * x) / denom if denom != 0 else 0.0
    v_prime = (9.0 * y) / denom if denom != 0 else 0.0

    denom_n = (Xn + 15.0 * Yn + 3.0 * Zn)
    u_prime_n = (4.0 * Xn) / denom_n
    v_prime_n = (9.0 * Yn) / denom_n

    y_ratio = y / Yn
    l = 116.0 * (y_ratio ** (1.0 / 3.0)) - 16.0 if y_ratio >= 0.008856 else 903.3 * y_ratio

    u = 13.0 * l * (u_prime - u_prime_n)
    v = 13.0 * l * (v_prime - v_prime_n)
    return l, u, v

def luv_to_xyz(l, u, v, illum="D65"):
    """Обратный перевод Luv -> XYZ"""
    Xn, Yn, Zn = ILLUMINANTS[illum]["white"]
    
    denom_n = (Xn + 15.0 * Yn + 3.0 * Zn)
    u_prime_n = (4.0 * Xn) / denom_n
    v_prime_n = (9.0 * Yn) / denom_n

    if l == 0:
        return 0.0, 0.0, 0.0

    u_prime = u / (13.0 * l) + u_prime_n
    v_prime = v / (13.0 * l) + v_prime_n

    if l >= 0.008856 * 903.3:
        y = Yn * (((l + 16.0) / 116.0) ** 3)
    else:
        y = Yn * (l / 903.3)

    if v_prime == 0:
        return 0.0, 0.0, 0.0
        
    x = y * ((9.0 * u_prime) / (4.0 * v_prime))
    z = y * ((12.0 - 3.0 * u_prime - 20.0 * v_prime) / (4.0 * v_prime))
    return x, y, z
