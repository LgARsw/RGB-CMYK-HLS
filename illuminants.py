import numpy as np

# Координаты белых точек (X, Y, Z) для sRGB / CIE стандартов
WHITE_POINTS = {
    'D65': np.array([0.95047, 1.00000, 1.08883]),
    'D50': np.array([0.96422, 1.00000, 0.82521]),
    'E':   np.array([1.00000, 1.00000, 1.00000])
}

# Эталонная матрица перехода sRGB -> XYZ для базового осветителя D65
PRIMARY_SRGB_TO_XYZ_D65 = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041]
])

# Коническая матрица преобразования Брэдфорда (Bradford Transformation Matrix)
M_B = np.array([
    [ 0.8951,  0.2664, -0.1614],
    [-0.7502,  1.7135,  0.0367],
    [ 0.0389, -0.0685,  1.0296]
])

M_B_INV = np.linalg.inv(M_B)

def get_chromatic_adaptation_matrix(source_wp, target_wp):
    # Перевод белых точек в коническое пространство ответов (L, M, S)
    src_lms = np.dot(M_B, source_wp)
    tgt_lms = np.dot(M_B, target_wp)
    
    # Диагональная матрица масштабирования
    M_scale = np.diag(tgt_lms / src_lms)
    
    # Итоговая матрица адаптации
    return np.dot(M_B_INV, np.dot(M_scale, M_B))

def get_rgb_to_xyz_matrix(std_name='D65'):
    """
    Динамически рассчитывает и возвращает матрицу sRGB -> XYZ 
    для выбранного стандарта освещения (D65, D50, E) на лету.
    """
    if std_name == 'D65':
        return PRIMARY_SRGB_TO_XYZ_D65
    
    # Если выбран D50 или E, на лету вычисляем матрицу адаптации Брэдфорда
    src_wp = WHITE_POINTS['D65']
    tgt_wp = WHITE_POINTS.get(std_name, src_wp)
    
    m_adapt = get_chromatic_adaptation_matrix(src_wp, tgt_wp)
    
    # Трансформируем базовую матрицу D65 под новый целевой источник освещения
    return np.dot(m_adapt, PRIMARY_SRGB_TO_XYZ_D65)

def get_xyz_to_rgb_matrix(std_name='D65'):
    """
    Динамически рассчитывает и возвращает обратную матрицу XYZ -> sRGB
    для выбранного стандарта освещения.
    """
    mat = get_rgb_to_xyz_matrix(std_name)
    return np.linalg.inv(mat)
