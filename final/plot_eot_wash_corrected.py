#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT³ Eöt-Wash Visualization Plot (Fixed Axis Limits)
"""

import numpy as np
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 7), dpi=300)

x1, y1 = 1e-5, 16.0
x2, y2 = 1e-4, 0.035
B = np.log(y2 / y1) / np.log(x2 / x1)
A = y1 / (x1 ** B)

x_curve = np.logspace(-5, -3, 500)
y_curve = A * (x_curve ** B)

plt.plot(x_curve, y_curve, 'k-', linewidth=2.5, label='Eöt-Wash 95% Confidence Limit')
plt.fill_between(x_curve, y_curve, 1e4, color='lightgray', label='Excluded Region', alpha=0.8)

lx_target = 115.2e-6
plt.axvline(x=lx_target, color='red', linestyle='--', alpha=0.5)

# Наивная модель ADD (на уровне alpha = 1)
plt.plot(lx_target, 1.0, 'wo', markeredgecolor='gray', markersize=10, 
         label='Naive ADD Model (Excluded)')

# Предсказание IT³ (на уровне alpha = 0.00112)
alpha_eff = 0.00112
plt.plot(lx_target, alpha_eff, 'ro', markeredgecolor='black', markersize=12, 
         label='IT³ Prediction ($\\alpha_{eff} \\approx 0.00112$)')

# Стрелка и текст подавления (координаты скорректированы)
plt.annotate('', xy=(lx_target, alpha_eff * 1.5), xytext=(lx_target, 0.5),
             arrowprops=dict(facecolor='blue', shrink=0.0, width=2, headwidth=8, alpha=0.7))
plt.text(lx_target * 1.15, 0.02, 'Topological Suppression\n(Irrational Geometry + Orbifold)', 
         color='blue', fontsize=11, weight='bold', verticalalignment='center')

# Информационная плашка (координаты скорректированы)
plt.text(1.35e-4, 1.5e-4, 'IT³ prediction sits safely\nin the ALLOWED region', 
         fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

# Форматирование осей
plt.xscale('log')
plt.yscale('log')
plt.xlim(1e-5, 1e-3)
# ИСПРАВЛЕНО: нижняя граница теперь 1e-4 вместо 1e-2
plt.ylim(1e-4, 1e4)

plt.xlabel('Length Scale $\\lambda$ (m)', fontsize=14)
plt.ylabel(r'Yukawa Coupling Strength $|\alpha|$', fontsize=14)
plt.title('IT³ Paradigm vs. Eöt-Wash Inverse-Square Law Tests', fontsize=16, pad=15)
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.legend(loc='upper right', fontsize=12)

plt.tight_layout()
plt.savefig('IT3_EotWash_Corrected_v2.png')
print("✅ График успешно сгенерирован: IT3_EotWash_Corrected_v2.png")