#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT3 Math Proof: Projection of 8 Cube Vertices -> m=4 Symmetry
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

plt.style.use('dark_background')

# 1. Создаем 8 вершин куба в 3D
# Координаты (x, y, z)
cube_vertices = np.array([
    [ 1,  1,  1], [-1,  1,  1], [ 1, -1,  1], [-1, -1,  1], # Верхняя грань
    [ 1,  1, -1], [-1,  1, -1], [ 1, -1, -1], [-1, -1, -1]  # Нижняя грань
])

# 2. Проекция на 2D (xy-плоскость)
# Мы "сплющиваем" куб, игнорируя Z.
# Точки (+,+,1) и (+,+,-1) превращаются в одну точку (+,+)
projected_points = cube_vertices[:, :2] 

# Удаляем дубликаты (те, что наложились друг на друга)
# В результате останется 4 уникальные точки: (1,1), (-1,1), (1,-1), (-1,-1)
unique_points = np.unique(projected_points, axis=0)

print(f"Исходных вершин (3D): {len(cube_vertices)}")
print(f"Точек на проекции (2D): {len(unique_points)}")

# 3. Анализ углового распределения (Имитация того, что мы делали с Gaia)
angles = np.arctan2(unique_points[:, 1], unique_points[:, 0])
# Нормализуем углы в [0, 2pi]
angles = angles % (2*np.pi)
angles.sort()

# Строим гистограмму углов (имитация звездного неба)
# Раскидаем точки по углам 45, 135, 225, 315 градусов
hist, _ = np.histogram(np.degrees(angles), bins=360, range=(0, 360))

# 4. FFT (Поиск гармоники)
fft_val = fft(hist)
power = np.abs(fft_val)**2
power[0] = 0 # Убираем ноль

# Нормализация
power = power / np.max(power)

# 5. Визуализация
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# График проекции
ax1.scatter(cube_vertices[:, 0], cube_vertices[:, 1], c='red', s=100, label='3D Vertices')
ax1.scatter(unique_points[:, 0], unique_points[:, 1], c='yellow', s=200, marker='x', label='2D Projection (Merged)')
ax1.set_title(f"Projection: 8 vertices -> {len(unique_points)} clusters")
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_aspect('equal')

# График спектра
m_vals = np.arange(1, 10)
ax2.plot(m_vals, power[1:10], 'g-o', linewidth=2)
ax2.axvline(x=4, color='yellow', linestyle='--', label='Target m=4')
ax2.set_title('Spectrum of Cube Projection')
ax2.set_xlabel('Harmonic m')
ax2.set_ylabel('Normalized Power')
ax2.set_xticks(m_vals)
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Cube_Projection_Proof.png', dpi=200, facecolor='#0a0a0a')
print("[SAVE] Cube_Projection_Proof.png")
plt.show()