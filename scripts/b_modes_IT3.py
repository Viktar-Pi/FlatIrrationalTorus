#!/usr/bin/env python3
"""
b_modes_IT3.py — Расчёт тензорных B-мод для модели $\mathbb{IT}^3$
Сравнивает дискретный спектр тора с континуальным $\Lambda$CDM.
Демонстрирует предсказанные осцилляции при $\ell \lesssim 10$.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import spherical_jn

# Настройка путей
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
RESULTS_DIR = os.path.join(PROJECT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Параметры модели
LX, LY, LZ = 28.8, 28.8 * np.sqrt(2), 28.8 * np.sqrt(3)  # Гпк
CHI_REC = 14000.0  # Мпк
R_TENSOR = 0.01    # tensor-to-scalar ratio
A_S = 2.21e-9
N_S = 0.965
N_T = -R_TENSOR / 8.0  # consistency relation
K_PIVOT = 0.05         # Мпк⁻¹
LMAX = 20
N_CUT = 10             # обрезка суммы по узлам решётки

def get_lattice_modes(N_cut):
    n = np.arange(-N_cut, N_cut + 1)
    nx, ny, nz = np.meshgrid(n, n, n, indexing='ij')
    mask = ~((nx == 0) & (ny == 0) & (nz == 0))
    return nx[mask], ny[mask], nz[mask]

def compute_BB_torus(ells):
    """Дискретная сумма тензорных мод на торе"""
    nx, ny, nz = get_lattice_modes(N_CUT)
    kx = 2 * np.pi * nx / (LX * 1000.0)  # Гпк -> Мпк
    ky = 2 * np.pi * ny / (LY * 1000.0)
    kz = 2 * np.pi * nz / (LZ * 1000.0)
    k = np.sqrt(kx**2 + ky**2 + kz**2)
    
    # Первичный тензорный спектр
    P_T = R_TENSOR * A_S * (k / K_PIVOT)**N_T * (2 * np.pi**2 / k**3)
    
    C_BB = np.zeros_like(ells, dtype=float)
    for i, ell in enumerate(ells):
        # Long-wavelength approximation для тензорных мод
        Delta_T = (1.0 / 5.0) * spherical_jn(ell, k * CHI_REC)
        contrib = P_T * Delta_T**2
        C_BB[i] = np.sum(contrib) / (LX * LY * LZ * 1e9)  # нормировка на объём
    return C_BB

def compute_BB_lcdm(ells):
    """Континуальная аппроксимация $\Lambda$CDM"""
    C_BB = np.zeros_like(ells, dtype=float)
    for i, ell in enumerate(ells):
        k_peak = (ell + 0.5) / CHI_REC
        P_T = R_TENSOR * A_S * (k_peak / K_PIVOT)**N_T * (2 * np.pi**2 / k_peak**3)
        Delta_T = (1.0 / 5.0) * spherical_jn(ell, k_peak * CHI_REC)
        C_BB[i] = (2 / np.pi) * P_T * Delta_T**2 * k_peak**2
    return C_BB

def main():
    print("🌊 Расчёт тензорных B-мод: $\mathbb{IT}^3$ vs $\Lambda$CDM")
    print("="*60)
    
    ells = np.arange(2, LMAX + 1)
    C_BB_torus = compute_BB_torus(ells)
    C_BB_lcdm = compute_BB_lcdm(ells)
    
    # Относительная разница (осцилляции)
    diff_pct = np.where(C_BB_lcdm > 1e-30, (C_BB_torus - C_BB_lcdm) / C_BB_lcdm * 100, 0.0)
    osc_amp = np.std(diff_pct[2:8])  # амплитуда в диапазоне $\ell=3$–$8$
    
    print(f"📊 Предсказанные осцилляции ($\ell=3$–$8$): {osc_amp:.2f}%")
    print(f"📈 Сохранение графика в results/BB_modes_IT3.png")
    
    # Визуализация
    plt.figure(figsize=(9, 5))
    plt.plot(ells, ells * (ells + 1) * C_BB_lcdm, 'o-', label=r'$\Lambda$CDM (continuum)', color='gray', markersize=6)
    plt.plot(ells, ells * (ells + 1) * C_BB_torus, 's-', label=r'$\mathbb{IT}^3$ (discrete)', color='#d62728', markersize=6)
    plt.xlabel(r'Multipole $\ell$', fontsize=12)
    plt.ylabel(r'$\ell(\ell+1)C_\ell^{BB}$ [μK²]', fontsize=12)
    plt.title(r'Tensor B-modes on $\mathbb{IT}^3$ Torus ($r=0.01$)', fontsize=13)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    out_path = os.path.join(RESULTS_DIR, "BB_modes_IT3.png")
    plt.savefig(out_path, dpi=300)
    print("✅ Готово. График сохранён.")

if __name__ == "__main__":
    main()
