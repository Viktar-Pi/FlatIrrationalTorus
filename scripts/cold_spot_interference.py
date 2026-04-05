#!/usr/bin/env python3
"""
cold_spot_interference.py — Моделирование CMB Cold Spot как узла стоячей волны
Показывает, как геометрия тора создаёт предсказуемые интерференционные минимумы.
"""
import os
import numpy as np
import healpy as hp
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
RESULTS_DIR = os.path.join(PROJECT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Параметры
NSIDE = 128  # достаточно для визуализации крупномасштабных мод
LX, LY, LZ = 28.8, 28.8 * np.sqrt(2), 28.8 * np.sqrt(3)  # Гпк
CHI_REC = 14.0  # Гпк
np.random.seed(42)  # воспроизводимость

def generate_torus_map(nside):
    """Генерация карты CMB как суперпозиции фундаментальных мод тора"""
    npix = hp.nside2npix(nside)
    theta, phi = hp.pix2ang(nside, np.arange(npix))
    vec_x = np.sin(theta) * np.cos(phi)
    vec_y = np.sin(theta) * np.sin(phi)
    vec_z = np.cos(theta)
    
    # Базовые моды (nx, ny, nz, амплитуда)
    modes = [
        (1, 0, 0, 120.0),
        (0, 1, 0, 90.0),
        (0, 0, 1, 70.0),
        (1, 1, 0, 40.0),
        (1, 0, 1, 35.0),
    ]
    
    T_map = np.zeros(npix)
    for nx, ny, nz, amp in modes:
        kx = 2 * np.pi * nx / LX
        ky = 2 * np.pi * ny / LY
        kz = 2 * np.pi * nz / LZ
        
        # Фаза на сфере последнего рассеяния
        phase = kx * CHI_REC * vec_x + ky * CHI_REC * vec_y + kz * CHI_REC * vec_z
        T_map += amp * np.cos(phase)
        
    # Добавление гауссова шума (космическая дисперсия)
    noise = np.random.normal(0, 25.0, npix)
    T_map += noise
    return T_map - np.mean(T_map)

def main():
    print("❄️  Моделирование Cold Spot в модели $\mathbb{IT}^3$")
    print("="*60)
    
    T_map = generate_torus_map(NSIDE)
    rms = np.std(T_map)
    
    # Поиск самого холодного пятна (>3° радиус)
    # Упрощённый поиск: пиксель с минимальной температурой
    min_idx = np.argmin(T_map)
    min_temp = T_map[min_idx]
    sigma_depth = abs(min_temp) / rms
    
    # Координаты пятна
    th_min, ph_min = hp.pix2ang(NSIDE, min_idx)
    l_deg = np.rad2deg(ph_min) % 360
    b_deg = 90.0 - np.rad2deg(th_min)
    
    print(f"📊 Результат:")
    print(f"   Глубина Cold Spot: {min_temp:.1f} мкК")
    print(f"   Отклонение от среднего: {sigma_depth:.2f}σ")
    print(f"   Координаты (галактические): l={l_deg:.1f}°, b={b_deg:.1f}°")
    print(f"   ✅ В $\Lambda$CDM вероятность >{sigma_depth:.1f}σ пятна: ~{100*np.exp(-0.5*sigma_depth**2):.2f}%")
    
    # Визуализация
    plt.figure(figsize=(12, 5))
    
    # Mollweide проекция
    plt.subplot(1, 2, 1, projection='mollweide')
    hp.mollview(T_map, title='Mock CMB Map on $\mathbb{IT}^3$ Torus', 
                unit='μK', cmap='coolwarm', hold=False, min=-150, max=150)
    plt.gca().invert_yaxis()
    
    # Распределение температур
    plt.subplot(1, 2, 2)
    plt.hist(T_map, bins=60, alpha=0.7, color='#1f77b4', edgecolor='black', density=True)
    x = np.linspace(T_map.min(), T_map.max(), 200)
    plt.plot(x, 1/(rms*np.sqrt(2*np.pi)) * np.exp(-0.5*(x/rms)**2), 'r--', linewidth=2, label='Gaussian $\sigma$')
    plt.axvline(min_temp, color='#d62728', linestyle=':', linewidth=2, label=f'Cold Spot ({min_temp:.0f} μK)')
    plt.xlabel('Temperature [μK]')
    plt.ylabel('Probability Density')
    plt.title('Temperature Distribution')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, "cold_spot_it3.png")
    plt.savefig(out_path, dpi=300)
    print(f"\n✅ Карта и гистограмма сохранены: {out_path}")

if __name__ == "__main__":
    main()
