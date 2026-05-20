import numpy as np
import matplotlib.pyplot as plt

def spherical_to_cartesian(ra, dec):
    """Конвертация RA/Dec (градусы) в 3D единичные векторы."""
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)
    x = np.cos(dec_rad) * np.cos(ra_rad)
    y = np.cos(dec_rad) * np.sin(ra_rad)
    z = np.sin(dec_rad)
    return np.column_stack((x, y, z))

def angular_distance(vec1, vec2):
    """Вычисление углового расстояния в градусах между массивами векторов."""
    # Dot product всех векторов выборки со всеми узлами
    # vec1 shape: (N, 3), vec2 shape: (M, 3) -> result shape: (N, M)
    dot_product = np.dot(vec1, vec2.T)
    # Ограничиваем в [-1, 1] для стабильности arccos из-за ошибок округления
    dot_product = np.clip(dot_product, -1.0, 1.0)
    return np.degrees(np.arccos(dot_product))

# =============================================================================
# 1. ЗАГРУЗКА КООРДИНАТ УЗЛОВ IT3 (Извлечено из ADQL запроса)
# =============================================================================
it3_nodes_ra_dec = np.array([
    # Экваториальные узлы (Dec = 0)
    [45.0,  0.0],
    [135.0, 0.0],
    [225.0, 0.0],
    [315.0, 0.0],
    # Северные узлы (Dec = +45)
    [0.0,   45.0],
    [90.0,  45.0],
    [180.0, 45.0],
    [270.0, 45.0],
    # Южные узлы (Dec = -45)
    [0.0,  -45.0],
    [90.0, -45.0],
    [180.0,-45.0],
    [270.0,-45.0]
])
nodes_vec = spherical_to_cartesian(it3_nodes_ra_dec[:, 0], it3_nodes_ra_dec[:, 1])

# =============================================================================
# 2. ЗАГРУЗКА РЕАЛЬНЫХ ETNO (Эмпирические данные)
# =============================================================================
# ЗАМЕНИ ЭТИ ДАННЫЕ на реальные RA/Dec афелиев твоей выборки ETNO.
# Сейчас здесь загружен демонстрационный сет, сгруппированный вблизи узлов
# для проверки работоспособности математики.
real_etno_ra_dec = np.array([
    [46.5,  1.2], [133.2, -0.5], [226.1, 2.0], [314.8, -1.1],
    [2.1,  44.5], [88.7,  46.1], [181.5, 43.8], [269.9, 45.0],
    [1.5, -46.0], [91.2, -44.5], [178.9,-45.2], [271.1,-43.9],
    [44.1, -1.5], [270.5, 46.2]
])

print("Анализ эмпирической выборки...")
n_etnos = len(real_etno_ra_dec)
real_etno_vec = spherical_to_cartesian(real_etno_ra_dec[:, 0], real_etno_ra_dec[:, 1])

# Считаем минимальное расстояние каждого реального ETNO до ближайшего узла IT3
dist_matrix_real = angular_distance(real_etno_vec, nodes_vec)
min_dists_real = np.min(dist_matrix_real, axis=1)
empirical_statistic = np.mean(min_dists_real)

print(f"Количество анализируемых ETNO: {n_etnos}")
print(f"Эмпирическое среднее отклонение: {empirical_statistic:.3f} градусов\n")

# =============================================================================
# 3. МОДЕЛИРОВАНИЕ MONTE CARLO С УЧЕТОМ SURVEY BIAS
# =============================================================================
n_simulations = 100_000
simulated_statistics = np.zeros(n_simulations)

print(f"Запуск {n_simulations} симуляций Monte Carlo (учет Ecliptic Bias)...")

# Генерируем сразу всю матрицу для ускорения (Векторизация)
# RA: равномерное распределение [0, 360]
rand_ra = np.random.uniform(0, 360, (n_simulations, n_etnos))

# Dec: нормальное распределение вокруг эклиптики (sigma = 15 градусов)
# Это симулирует "ошибку выжившего" - телескопы чаще находят объекты около эклиптики
rand_dec = np.random.normal(loc=0.0, scale=15.0, size=(n_simulations, n_etnos))
rand_dec = np.clip(rand_dec, -90, 90)

for i in range(n_simulations):
    # Берем срез сгенерированных координат для i-той симуляции
    sim_ra = rand_ra[i]
    sim_dec = rand_dec[i]
    
    sim_vec = spherical_to_cartesian(sim_ra, sim_dec)
    
    # Считаем дистанции для фейковой выборки
    dist_matrix = angular_distance(sim_vec, nodes_vec)
    min_dists = np.min(dist_matrix, axis=1)
    
    # Сохраняем среднее отклонение для этой симуляции
    simulated_statistics[i] = np.mean(min_dists)

# =============================================================================
# 4. РАСЧЕТ P-VALUE И ВЫВОД РЕЗУЛЬТАТОВ
# =============================================================================
# p-value = доля случайных конфигураций, которые выровнялись так же близко или ближе
p_value = np.sum(simulated_statistics <= empirical_statistic) / n_simulations

print("-" * 50)
print("ИТОГОВЫЙ СТАТИСТИЧЕСКИЙ ВЫВОД:")
print(f"Эмпирическая статистика (S_obs): {empirical_statistic:.3f}°")
print(f"Скорректированный P-value:       {p_value:.5f}")
print("-" * 50)

if p_value < 0.05:
    print("ВЕРДИКТ: Кластеризация статистически ЗНАЧИМА.")
    print("Нулевая гипотеза отвергается. Выравнивание не может быть объяснено")
    print("случайным распределением и наблюдательным искажением (Survey Bias).")
else:
    print("ВЕРДИКТ: Кластеризация статистически НЕ ЗНАЧИМА.")
    print("Наблюдаемое выравнивание может быть следствием наблюдательного искажения.")

# =============================================================================
# 5. ВИЗУАЛИЗАЦИЯ (Для включения в статью)
# =============================================================================
plt.figure(figsize=(10, 6))
plt.hist(simulated_statistics, bins=100, color='royalblue', alpha=0.7, density=True, label='Null Distribution (Monte Carlo)')
plt.axvline(empirical_statistic, color='red', linestyle='dashed', linewidth=2, label=rf'Observed IT3 Alignment ($S_{{obs}} = {empirical_statistic:.2f}^\circ$)')
plt.title(r'Monte Carlo Significance Test for ETNO Topological Anchoring' + '\n' + r'(Adjusted for Ecliptic Survey Bias $\sigma=15^\circ$)', fontsize=14)
plt.ylabel('Probability Density', fontsize=12)
plt.legend(loc='upper right', fontsize=11)
plt.grid(True, alpha=0.3)

# Текстовый блок с p-value на графике
plt.text(0.05, 0.85, f'$N_{{sim}} = {n_simulations}$\n$N_{{ETNO}} = {n_etnos}$\n$p$-value $= {p_value:.5f}$', 
         transform=plt.gca().transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

plt.tight_layout()
plt.show()