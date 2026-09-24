import math

def rgb_to_cmyk(r, g, b):
    """Прямой перевод RGB -> CMYK"""
    rc, gc, bc = r / 255.0, g / 255.0, b / 255.0
    k = min(1.0 - rc, 1.0 - gc, 1.0 - bc)
    
    if k >= 1.0:
        return 0.0, 0.0, 0.0, 100.0
        
    c = (1.0 - rc - k) / (1.0 - k)
    m = (1.0 - gc - k) / (1.0 - k)
    y = (1.0 - bc - k) / (1.0 - k)
    
    return max(0.0, c) * 100.0, max(0.0, m) * 100.0, max(0.0, y) * 100.0, k * 100.0

def cmyk_to_rgb(c, m, y, k):
    """Прямой перевод CMYK -> RGB"""
    c_n, m_n, y_n, k_n = c / 100.0, m / 100.0, y / 100.0, k / 100.0
    r = 255.0 * (1.0 - c_n) * (1.0 - k_n)
    g = 255.0 * (1.0 - m_n) * (1.0 - k_n)
    b = 255.0 * (1.0 - y_n) * (1.0 - k_n)
    return int(round(max(0.0, min(255.0, r)))), int(round(max(0.0, min(255.0, g)))), int(round(max(0.0, min(255.0, b))))

def rgb_to_hls(r, g, b):
    """Прямой перевод RGB -> HLS"""
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

def hls_to_rgb(h, l, s):
    """Прямой перевод HLS -> RGB по тригонометрической блок-схеме"""
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
    return int(round(max(0.0, min(255.0, r_raw)))), int(round(max(0.0, min(255.0, g_raw)))), int(round(max(0.0, min(255.0, b_raw))))
