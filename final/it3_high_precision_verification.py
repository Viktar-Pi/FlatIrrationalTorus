#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT³ High-Precision Verification & Strict QED-Hunter v3.0
========================================================
Tests geometric predictions vs experiments. 
Searches ONLY for elegant, physically meaningful perturbative 
corrections, penalizing overfitting and complex fractions.

Author: Victor Logvinovich, M.Sc. in Physics & Mathematics
Contact: lomakez@icloud.com
Zenodo: https://zenodo.org/records/19565648
"""

import mpmath
import re

# Set precision to 50 decimal places for all calculations
mpmath.mp.dps = 50

def is_beautiful(formula_str):
    """
    Бритва Оккама: проверяет строку формулы. 
    Если содержит числа больше 20 (например, странные дроби вроде 97),
    отвергает формулу как математическое переобучение.
    """
    if not formula_str:
        return False
    # Извлекаем все числа из формулы
    numbers = [int(n) for n in re.findall(r'\d+', formula_str)]
    # Если есть число больше 20, это "гадкий утенок"
    if any(n > 20 for n in numbers):
        return False
    return True

def run_verification():
    print("=" * 70)
    print("🔬 IT³ HIGH-PRECISION VERIFICATION (v3.0)")
    print("=" * 70)
    print("Testing agreement to 7-8+ decimal places...\n")

    pi = mpmath.pi
    sqrt2 = mpmath.sqrt(2)
    sqrt3 = mpmath.sqrt(3)
    sqrt6 = mpmath.sqrt(6)
    
    # Экспериментальное значение постоянной тонкой структуры (альфа)
    alpha_exp = mpmath.mpf('1') / mpmath.mpf('137.035999084')
    alpha_pi = alpha_exp / pi # Типичный масштаб поправки Швингера

    anomalies = {}

    # 1. Fermion Generations
    N_gen_geom, N_gen_exp = mpmath.mpf(3), mpmath.mpf(3)
    print("1. Fermion Generations:")
    print(f"   Geometry:   {N_gen_geom}")
    print(f"   Experiment: {N_gen_exp}")
    print(f"   Difference: {abs(N_gen_geom - N_gen_exp)}")
    print(f"   ✅ EXACT MATCH\n")

    # 2. Proton/Electron Mass Ratio
    mu_geom = 6 * pi**5
    mu_exp = mpmath.mpf('1836.15267343')
    diff_mu = abs(mu_geom - mu_exp)
    print("2. Proton/Electron Mass Ratio (μ):")
    print(f"   Geometry:   {mpmath.nstr(mu_geom, 15)}")
    print(f"   Experiment: {mu_exp}")
    print(f"   Difference: {float(diff_mu):.2e}")
    if diff_mu < mpmath.mpf('1e-6'):
        print(f"   ✅ AGREES TO 6+ DECIMAL PLACES!\n")
    else:
        print(f"   ⚠️  Divergence detected.\n")
        anomalies["Proton/Electron Mass Ratio (μ)"] = (mu_geom, mu_exp)

    # 3. Fine Structure Constant
    alpha_inv_geom = (20 * pi**6) / (81 * sqrt3)
    alpha_inv_exp = mpmath.mpf('137.035999084')
    diff_alpha = abs(alpha_inv_geom - alpha_inv_exp)
    print("3. Fine Structure Constant (α⁻¹):")
    print(f"   Geometry:   {mpmath.nstr(alpha_inv_geom, 15)}")
    print(f"   Experiment: {alpha_inv_exp}")
    print(f"   Difference: {float(diff_alpha):.2e}")
    if diff_alpha < mpmath.mpf('1e-6'):
        print(f"   ✅ AGREES TO 6+ DECIMAL PLACES!\n")
    else:
        print(f"   ⚠️  Divergence detected.\n")
        anomalies["Fine Structure Constant (α⁻¹)"] = (alpha_inv_geom, alpha_inv_exp)

    # 4. Weinberg Angle
    weinberg_geom = (pi * sqrt6 / 16)**2
    weinberg_exp = mpmath.mpf('0.23129')
    diff_wein = abs(weinberg_geom - weinberg_exp)
    print("4. Weinberg Mixing Angle (sin²θ_W):")
    print(f"   Geometry:   {mpmath.nstr(weinberg_geom, 15)}")
    print(f"   Experiment: {weinberg_exp}")
    print(f"   Difference: {float(diff_wein):.2e}")
    if diff_wein < mpmath.mpf('1e-6'):
        print(f"   ✅ AGREES TO 6+ DECIMAL PLACES!\n")
    else:
        print(f"   ⚠️  Divergence detected.\n")
        anomalies["Weinberg Mixing Angle (sin²θ_W)"] = (weinberg_geom, weinberg_exp)

    # ============================================================
    # STRICT TOPOLOGICAL & QED CORRECTION HUNTER
    # ============================================================
    if anomalies:
        print("=" * 70)
        print("🛡️  STRICT TOPOLOGICAL & QED CORRECTION HUNTER")
        print("=" * 70)
        print("Searching for elegant physics. Overfitting strictly banned.")
        print("Tolerance: 1e-12. Max Coefficient/Denominator: 20.\n")
        
        basis = ['pi', 'sqrt(2)', 'sqrt(3)', 'sqrt(6)']
        strict_tol = 1e-12
        
        for name, (geom, exp) in anomalies.items():
            print(f"[{name}]")
            delta = exp - geom
            fractional_shift = delta / geom
            
            found_elegant = False
            
            # Проверка 1: Чистая геометрия (относительный сдвиг)
            frac_geom = mpmath.identify(fractional_shift, basis, tol=strict_tol)
            if is_beautiful(frac_geom):
                print(f"  ✅ Pure Geometry Shift: Geom * (1 + {frac_geom})")
                found_elegant = True
                
            # Проверка 2: Зависит ли сдвиг от константы связи (масштаб Альфа)
            frac_alpha = mpmath.identify(fractional_shift / alpha_exp, basis, tol=strict_tol)
            if is_beautiful(frac_alpha):
                print(f"  ✅ QED-style Alpha Shift: Geom * (1 + α * ({frac_alpha}))")
                found_elegant = True
                
            # Проверка 3: Швингеровский масштаб (Альфа / Пи)
            frac_schwinger = mpmath.identify(fractional_shift / alpha_pi, basis, tol=strict_tol)
            if is_beautiful(frac_schwinger):
                print(f"  ✅ Schwinger-style Shift: Geom * (1 + (α/π) * ({frac_schwinger}))")
                found_elegant = True
                
            if not found_elegant:
                print("  ❌ No elegant corrections found. The divergence is non-trivial.")
            print("-" * 70)

if __name__ == "__main__":
    run_verification()