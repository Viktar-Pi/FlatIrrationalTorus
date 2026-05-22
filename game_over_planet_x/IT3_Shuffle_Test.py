#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT3 Shuffle Test (FIXED): Circular Aperture Mask
Проверка: является ли пик m=4 следствием формы окна выборки или реальной структурой
ИСПРАВЛЕНИЕ: Строгая круговая апертура для исключения артефактов углов
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
from tqdm import tqdm

plt.style.use('dark_background')
C_GREEN = '\033[92m'
C_RED = '\033[91m'
C_YELLOW = '\033[93m'
C_RESET = '\033[0m'

# === НАСТРОЙКИ ===
TARGET_RA = 270.0
TARGET_DEC = 45.0
REGION_RADIUS = 3.0  # градусы
N_SHUFFLES = 1000    # число итераций
RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)

print(f"{C_GREEN}[IT3 Shuffle Test v2.0]{C_RESET}")
print(f"Используется СТРОГО КРУГОВАЯ апертура (Circular Aperture)\n")

# === 1. ЗАГРУЗКА ДАННЫХ (С КРУГОВОЙ МАСКОЙ) ===
def load_and_filter_circular(filepath, catalog_name):
    """Загрузка и фильтрация данных по КРУГУ"""
    try:
        df = pd.read_csv(filepath)
        if 'ra' not in df.columns:
            if 'gaia' in filepath.lower():
                cols = ['ra','dec','pmra','pmdec','pmraerr','pmdecerr','parallax'] + [f'col{i}' for i in range(7,30)]
            else:
                cols = ['id','ra','dec','pmra','pmdec','pmraerr','pmdecerr','gmag','rmag','imag','ndet','mjd','deltamjd','class_star','flags','random_id']
            df = pd.read_csv(filepath, header=None, names=cols)
        
        # 1. Предварительный фильтр (квадрат с запасом), чтобы не грузить весь файл
        buffer = 0.5 
        mask_pre = (
            (df['ra'] >= TARGET_RA - REGION_RADIUS - buffer) & 
            (df['ra'] <= TARGET_RA + REGION_RADIUS + buffer) &
            (df['dec'] >= TARGET_DEC - REGION_RADIUS - buffer) & 
            (df['dec'] <= TARGET_DEC + REGION_RADIUS + buffer)
        )
        df_pre = df[mask_pre].copy()
        
        # Очистка
        for col in ['ra', 'dec']:
            df_pre[col] = pd.to_numeric(df_pre[col], errors='coerce')
        df_pre.dropna(subset=['ra', 'dec'], inplace=True)

        # 2. СТРОГАЯ КРУГОВАЯ МАСКА
        # Формула углового расстояния (приближенная для малых углов)
        dx = (df_pre['ra'] - TARGET_RA) * np.cos(np.radians(TARGET_DEC))
        dy = (df_pre['dec'] - TARGET_DEC)
        dist = np.sqrt(dx**2 + dy**2)
        
        mask_circle = dist <= REGION_RADIUS
        df_final = df_pre[mask_circle].copy()
        
        print(f"[{C_GREEN}OK{C_RESET}] {catalog_name}: {len(df_final)} объектов в КРУГЕ R={REGION_RADIUS}°")
        return df_final
    except Exception as e:
        print(f"{C_RED}[ERROR] {catalog_name}: {e}{C_RESET}")
        return None

df_gaia = load_and_filter_circular('gaia.csv', 'Gaia DR3')
df_nsc = load_and_filter_circular('noirlab.csv', 'NOIRLab NSC DR2')

if df_gaia is None and df_nsc is None:
    exit()

# === 2. ФУНКЦИЯ РАСЧЁТА СПЕКТРА ===
def compute_power_spectrum(ra, dec, center_ra, center_dec, bins=360):
    dx = (ra - center_ra) * np.cos(np.radians(center_dec))
    dy = dec - center_dec
    phi = np.arctan2(dy, dx)
    phi[phi < 0] += 2 * np.pi
    
    hist, _ = np.histogram(phi, bins=bins, range=(0, 2*np.pi))
    fft_vals = fft(hist)
    power = np.abs(fft_vals)**2
    power[0] = 0
    max_p = np.max(power[1:])
    return power / max_p if max_p > 0 else power

# === 3. REAL SPECTRUM ===
print(f"\n[{C_YELLOW}REAL{C_RESET}] Расчёт спектра (Круговая выборка)...")
real_spectra = {}

if df_gaia is not None:
    real_spectra['Gaia'] = compute_power_spectrum(df_gaia['ra'].values, df_gaia['dec'].values, TARGET_RA, TARGET_DEC)
if df_nsc is not None:
    real_spectra['NOIRLab'] = compute_power_spectrum(df_nsc['ra'].values, df_nsc['dec'].values, TARGET_RA, TARGET_DEC)

# === 4. SHUFFLE TEST ===
print(f"\n[{C_YELLOW}SHUFFLE{C_RESET}] Запуск {N_SHUFFLES} итераций...")

def shuffle_azimuth(ra, dec, center_ra, center_dec):
    dx = (ra - center_ra) * np.cos(np.radians(center_dec))
    dy = dec - center_dec
    r = np.sqrt(dx**2 + dy**2)
    phi_rand = np.random.uniform(0, 2*np.pi, len(ra))
    dx_new = r * np.cos(phi_rand)
    dy_new = r * np.sin(phi_rand)
    ra_new = center_ra + dx_new / np.cos(np.radians(center_dec))
    dec_new = center_dec + dy_new
    return ra_new, dec_new

null_dist_m4 = {name: [] for name in real_spectra.keys()}

for name, df in [('Gaia', df_gaia), ('NOIRLab', df_nsc)]:
    if df is None: continue
    
    ra_orig = df['ra'].values
    dec_orig = df['dec'].values
    
    for i in tqdm(range(N_SHUFFLES), desc=f"{name} shuffle", leave=False):
        ra_shuf, dec_shuf = shuffle_azimuth(ra_orig, dec_orig, TARGET_RA, TARGET_DEC)
        power_shuf = compute_power_spectrum(ra_shuf, dec_shuf, TARGET_RA, TARGET_DEC)
        null_dist_m4[name].append(power_shuf[4])

# === 5. РЕЗУЛЬТАТЫ ===
print(f"\n[{C_GREEN}RESULTS{C_RESET}] Оценка значимости...")
results = {}
for name in real_spectra.keys():
    real_m4 = real_spectra[name][4]
    null_m4 = np.array(null_dist_m4[name])
    p_val = np.mean(null_m4 >= real_m4)
    mu_null = np.mean(null_m4)
    
    results[name] = {'real_m4': real_m4, 'p_value': p_val}
    
    # Вывод
    status_color = C_GREEN if p_val < 0.05 else C_RED
    print(f"\n{name}:")
    print(f"  Реальный P(m=4)  : {real_m4:.4f}")
    print(f"  Шум (mean)       : {mu_null:.4f}")
    print(f"  p-value          : {p_val:.4e}")
    print(f"  Статус           : {status_color}{'SIGNIFICANT' if p_val < 0.05 else 'NOT SIGNIFICANT'}{C_RESET}")

# === 6. ГРАФИК ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
m_vals = range(1, 15)
for name, power in real_spectra.items():
    color = 'cyan' if 'Gaia' in name else 'magenta'
    axes[0].plot(m_vals, power[1:15], 'o-', color=color, label=name, linewidth=2)
axes[0].axvline(x=4, color='yellow', linestyle='--', label='Target m=4')
axes[0].set_title('Real Data Spectrum (Circular Mask)')
axes[0].legend(); axes[0].grid(True, alpha=0.3)

for name in results.keys():
    color = 'cyan' if 'Gaia' in name else 'magenta'
    axes[1].hist(null_dist_m4[name], bins=50, color=color, alpha=0.5, density=True)
    axes[1].axvline(x=results[name]['real_m4'], color=color, linestyle='-', linewidth=2)
    axes[1].text(0.95, 0.95, f'p = {results[name]["p_value"]:.2e}', transform=axes[1].transAxes, 
                 ha='right', va='top', bbox=dict(facecolor='black', alpha=0.7, edgecolor=color))
axes[1].set_title('Shuffle Test (Circular Mask)')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('IT3_Shuffle_Circular.png', dpi=200, facecolor='#0a0a0a')
print(f"\n[{C_GREEN}SAVE{C_RESET}] IT3_Shuffle_Circular.png")
plt.show()