def apply_clipping(r, g, b):
    
    r_out = max(0.0, min(255.0, r))
    g_out = max(0.0, min(255.0, g))
    b_out = max(0.0, min(255.0, b))
    was_out = (r != r_out) or (g != g_out) or (b != b_out)
    return int(round(r_out)), int(round(g_out)), int(round(b_out)), was_out

def apply_scaling(r, g, b):
    vals = [r, g, b]
    min_v = min(vals)
    max_v = max(vals)
    
    was_out = (min_v < 0.0) or (max_v > 255.0)
    if not was_out:
        return int(round(r)), int(round(g)), int(round(b)), False
        
    shift = 0.0 if min_v >= 0.0 else -min_v
    r += shift; g += shift; b += shift
    
    max_v += shift
    if max_v > 255.0:
        scale = 255.0 / max_v
        r *= scale; g *= scale; b *= scale
        
    return int(round(r)), int(round(g)), int(round(b)), True
