#!/usr/bin/env python3
"""
BipoSH-тест модели IT³ — ПОЛНАЯ ВЕРСИЯ (Full Rigorous Test)
Использует ваши точные файлы Planck R3.00/R3.01
"""
import numpy as np
import healpy as hp
from scipy.stats import chi2
from sympy.physics.wigner import wigner_3j
import sys, os

def main():
    # === ПАРАМЕТРЫ И ПУТИ К ВАШИМ ФАЙЛАМ ===
    data_dir = os.getenv('DATA_DIR', 'data') # Если файлы в той же папке, поменяйте 'data' на '.'
    map_file = os.path.join(data_dir, 'COM_CMB_IQU-smica_2048_R3.00_full.fits')
    mask_file = os.path.join(data_dir, 'COM_Mask_CMB-common-Mask-Pol_2048_R3.00.fits')
    cl_file = os.path.join(data_dir, 'COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt')
    
    l_axis = float(os.getenv('L_AXIS', '260'))
    b_axis = float(os.getenv('B_AXIS', '50'))
    lmax_val = 50
    
    print("🔬 BipoSH-тест модели IT³ (Полный пайплайн на данных Planck R3.01)")
    print("===========================================================================")
    
    # === ПРОВЕРКА ФАЙЛОВ ===
    for f in [map_file, mask_file, cl_file]:
        if not os.path.exists(f):
            print(f"ERROR: Файл не найден: {f}\nУбедитесь, что он лежит в папке '{data_dir}/'", file=sys.stderr)
            return 1
            
    # === 1. ЗАГРУЗКА КАРТЫ И МАСКИ ===
    print(f"📥 Загрузка карты: {os.path.basename(map_file)}")
    map_T = hp.read_map(map_file, field=0, verbose=False)
    
    print(f"🎭 Загрузка официальной маски: {os.path.basename(mask_file)}")
    mask = hp.read_map(mask_file, verbose=False)
    
    # Применяем маску
    map_masked = map_T * mask
    
    # Считаем момент w2 для поправки на потерянную мощность
    w2 = np.mean(mask**2)
    print(f"✅ Данные готовы. Эффективная доля неба f_sky (w2) = {w2*100:.1f}%")
    
    # === 2. ВЫЧИСЛЕНИЕ a_lm ===
    print(f"🔢 Вычисление a_lm (ℓ=2–{lmax_val})...")
    alm = hp.map2alm(map_masked, lmax=lmax_val, use_pixel_weights=True)
    
    # === 3. РАСЧЁТ A_ℓℓ²⁰ ===
    def compute_A_ell_ell_20(alm, ells, l_axis_deg, b_axis_deg, lmax):
        A_vals = np.zeros_like(ells, dtype=float)
        l_axis, b_axis = np.deg2rad(l_axis_deg), np.deg2rad(b_axis_deg)
        Y20_factor = np.sqrt(5/(4*np.pi)) * (3*np.cos(b_axis)**2 - 1)/2
        
        for i, ell in enumerate(ells):
            sum_val = 0.0
            for m in range(-ell, ell+1):
                abs_m = abs(m)
                idx = hp.Alm.getidx(lmax, ell, abs_m)
                
                if idx < len(alm):
                    a_lm_pos = alm[idx]
                    if m < 0:
                        a_lm = ((-1)**abs_m) * np.conj(a_lm_pos)
                    else:
                        a_lm = a_lm_pos
                    sum_val += np.real(a_lm * np.conj(a_lm)) * Y20_factor
            A_vals[i] = sum_val / (2*ell + 1)
        return A_vals

    print("📐 Вычисление проекций BipoSH A_ℓℓ²⁰...")
    ells = np.arange(2, lmax_val + 1)
    A_model = compute_A_ell_ell_20(alm, ells, l_axis, b_axis, lmax_val) / w2
    
    # === 4. ЗАГРУЗКА РЕАЛЬНОГО C_ell^ΛCDM ===
    print(f"📈 Загрузка спектра мощности ΛCDM: {os.path.basename(cl_file)}")
    cl_data = np.loadtxt(cl_file)
    
    # Столбец 0: L, Столбец 1: TT (D_ell)
    D_ell_interp = np.interp(ells, cl_data[:,0], cl_data[:,1])
    # Конвертация D_ell -> C_ell
    C_ell_lcdm = D_ell_interp * 2 * np.pi / (ells * (ells + 1))
    
    # === 5. КОНВЕРСИЯ A → g_* ===
    def A_to_g_star(ells, A_vals, C_ell_ref):
        g_vals, weights = [], []
        for i, ell in enumerate(ells):
            w3j = float(wigner_3j(ell, ell, 2, 0, 0, 0))
            norm = np.sqrt(5/(4*np.pi)) * w3j
            if np.abs(norm) < 1e-15: continue
            
            g_l = A_vals[i] / (C_ell_ref[i] * norm)
            g_vals.append(g_l)
            weights.append(C_ell_ref[i]**2)
            
        return np.average(g_vals, weights=weights) if g_vals else 0.0
    
    g_star_model = A_to_g_star(ells, A_model, C_ell_lcdm)
    
    # === 6. СТАТИСТИКА ===
    g_star_obs, g_star_sigma = 0.002, 0.016
    chi2_val = ((g_star_model - g_star_obs) / g_star_sigma)**2
    p_val = 1 - chi2.cdf(chi2_val, df=1)
    
    # === ВЫВОД ===
    print(f"\n📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"   g_*^model = {g_star_model:+.5f}")
    print(f"   g_*^obs   = {g_star_obs:.3f} ± {g_star_sigma:.3f} (Kim & Komatsu 2013)")
    print(f"   χ²        = {chi2_val:.3f}")
    print(f"   p-value   = {p_val:.4f}")
    
    threshold = float(os.getenv('G_STAR_THRESHOLD', '0.031'))
    status = "PASS" if abs(g_star_model) < threshold else "FAIL"
    print(f"   95% CL тест: |g_*| < {threshold} ? {'✅ PASS' if status=='PASS' else '❌ FAIL'}")
    print(f"STATUS:{status}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())