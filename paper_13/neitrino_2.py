#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT³ Neutrino Mass Matrix: α-Optimization Scan
Finds optimal power-law suppression for off-diagonal elements
to simultaneously fit mass ratios AND mixing angles.

Author: Victor Logvinovich
Date: April 2026
"""

import numpy as np
from scipy import linalg
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# EXPERIMENTAL TARGETS (NuFIT 5.2, Normal Hierarchy, 1σ)
# ============================================================================

EXP = {
    'dm21_sq': 7.5e-5,      # eV²
    'dm32_sq': 2.5e-3,      # eV²
    'theta12': 33.4,        # degrees
    'theta23': 49.2,        # degrees
    'theta13': 8.6,         # degrees
    'sigma_dm21': 0.2e-5,
    'sigma_dm32': 0.07e-3,
    'sigma_t12': 0.7,
    'sigma_t23': 1.0,
    'sigma_t13': 0.1,
}

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def build_mass_matrix(alpha, L1=1.0, L2=np.sqrt(2), L3=np.sqrt(3)):
    """
    Construct Hermitian mass matrix with power-law suppressed off-diagonals.
    M_ij = (S0 / (L_i * L_j))^alpha * exp(i * phi_ij)
    """
    # Topological phases
    phi_12 = 2 * np.pi * (L1/L2 - L2/L1)
    phi_13 = 2 * np.pi * (L1/L3 - L3/L1)
    phi_23 = 2 * np.pi * (L2/L3 - L3/L2)
    
    # Base scale for off-diagonals
    S0 = L1 * L2  # = sqrt(2)
    
    # Off-diagonal magnitudes with power-law suppression
    off_12 = (S0 / (L1 * L2))**alpha  # = 1^alpha = 1
    off_13 = (S0 / (L1 * L3))**alpha  # = (sqrt(2)/sqrt(3))^alpha
    off_23 = (S0 / (L2 * L3))**alpha  # = (sqrt(2)/(sqrt(2)*sqrt(3)))^alpha = (1/sqrt(3))^alpha
    
    # Build Hermitian matrix
    M = np.array([
        [L1, off_12 * np.exp(1j * phi_12), off_13 * np.exp(1j * phi_13)],
        [off_12 * np.exp(-1j * phi_12), L2, off_23 * np.exp(1j * phi_23)],
        [off_13 * np.exp(-1j * phi_13), off_23 * np.exp(-1j * phi_23), L3]
    ])
    return M

def extract_angles(U):
    """Extract PMNS angles from eigenvector matrix U (PDG convention)."""
    sin_t13 = np.abs(U[0, 2])
    sin_t13 = np.clip(sin_t13, 0, 1)
    t13 = np.arcsin(sin_t13)
    
    sin_t23 = np.abs(U[1, 2]) / np.cos(t13)
    sin_t23 = np.clip(sin_t23, 0, 1)
    t23 = np.arcsin(sin_t23)
    
    sin_t12 = np.abs(U[0, 1]) / np.cos(t13)
    sin_t12 = np.clip(sin_t12, 0, 1)
    t12 = np.arcsin(sin_t12)
    
    return np.degrees(t12), np.degrees(t23), np.degrees(t13)

def compute_chi2(alpha):
    """Compute χ² for given α relative to experimental targets."""
    M = build_mass_matrix(alpha)
    evals, evecs = linalg.eigh(M)
    
    # Sort eigenvalues
    idx = np.argsort(evals)
    m = evals[idx]
    U = evecs[:, idx]
    
    # Mass squared differences (in m₀² units)
    dm21 = m[1]**2 - m[0]**2
    dm32 = m[2]**2 - m[1]**2
    
    # Calibrate m₀ from experimental Δm²₂₁
    m0 = np.sqrt(EXP['dm21_sq'] / dm21)
    
    # Predicted observables
    R_pred = dm32 / dm21
    R_exp = EXP['dm32_sq'] / EXP['dm21_sq']
    
    t12, t23, t13 = extract_angles(U)
    
    # χ² components (mass ratio + 3 angles)
    chi2_R = ((R_pred - R_exp) / 0.1)**2  # 10% tolerance on ratio
    chi2_t12 = ((t12 - EXP['theta12']) / EXP['sigma_t12'])**2
    chi2_t23 = ((t23 - EXP['theta23']) / EXP['sigma_t23'])**2
    chi2_t13 = ((t13 - EXP['theta13']) / EXP['sigma_t13'])**2
    
    return chi2_R + chi2_t12 + chi2_t23 + chi2_t13, {
        'm': m, 'R': R_pred, 'angles': (t12, t23, t13), 'm0': m0, 'U': U
    }

# ============================================================================
# SCAN OVER α
# ============================================================================

print("="*70)
print("IT³ NEUTRINO SECTOR: α-OPTIMIZATION SCAN")
print("Power-law suppression: |M_ij| = (S₀/(LᵢLⱼ))^α")
print("="*70)

alphas = np.linspace(0.30, 0.70, 41)
results = []

print(f"\n{'α':>6} | {'χ²':>8} | {'R':>7} | {'θ₁₂':>6} | {'θ₂₃':>6} | {'θ₁₃':>6}")
print("-"*70)

for a in alphas:
    chi2, data = compute_chi2(a)
    t12, t23, t13 = data['angles']
    print(f"{a:6.3f} | {chi2:8.2f} | {data['R']:7.2f} | {t12:6.2f}° | {t23:6.2f}° | {t13:6.2f}°")
    results.append((a, chi2, data))

# Find best α
best = min(results, key=lambda x: x[1])
alpha_opt, chi2_min, data_opt = best

print("\n" + "="*70)
print(f"✓ OPTIMAL α = {alpha_opt:.3f} (χ² = {chi2_min:.2f})")
print("="*70)

# ============================================================================
# DETAILED OUTPUT FOR BEST α
# ============================================================================

m = data_opt['m']
R = data_opt['R']
t12, t23, t13 = data_opt['angles']
m0 = data_opt['m0']
U = data_opt['U']

# Absolute masses
m1_ev = m[0] * m0
m2_ev = m[1] * m0
m3_ev = m[2] * m0
sum_m = m1_ev + m2_ev + m3_ev

# Jarlskog invariant
J = np.imag(U[0,0]*U[1,1]*np.conj(U[0,1])*np.conj(U[1,0]))

print(f"\n📊 PREDICTIONS AT α = {alpha_opt:.3f}:")
print(f"\nMass eigenvalues (m₀ units):")
print(f"  m₁ = {m[0]:.4f}, m₂ = {m[1]:.4f}, m₃ = {m[2]:.4f}")
print(f"\nMass ratio R = Δm²₃₂/Δm²₂₁:")
print(f"  IT³: {R:.2f} | Exp: 33.3 ± 1.1 | Deviation: {abs(R-33.3)/33.3*100:.1f}%")
print(f"\nMixing angles:")
print(f"  θ₁₂ = {t12:.2f}° (exp: 33.4° ± 0.7°) | Δ = {t12-33.4:+.2f}°")
print(f"  θ₂₃ = {t23:.2f}° (exp: 49.2° ± 1.0°) | Δ = {t23-49.2:+.2f}°")
print(f"  θ₁₃ = {t13:.2f}° (exp: 8.6° ± 0.1°)  | Δ = {t13-8.6:+.2f}°")
print(f"\nAbsolute masses:")
print(f"  m₁ = {m1_ev*1000:.3f} meV, m₂ = {m2_ev*1000:.3f} meV, m₃ = {m3_ev*1000:.3f} meV")
print(f"  Σm_ν = {sum_m*1000:.1f} meV (target: 58–70 meV)")
print(f"\nCP violation:")
print(f"  J = {J:.4f} (exp: ~ -0.025)")

# Save best result
save = input("\n💾 Save optimal result to file? (y/n): ").strip().lower()
if save == 'y':
    with open(f"IT3_optimal_alpha_{alpha_opt:.3f}.txt", 'w', encoding='utf-8') as f:
        f.write(f"IT³ Optimal α = {alpha_opt:.3f}\n")
        f.write(f"χ² = {chi2_min:.2f}\n\n")
        f.write(f"Masses (m₀): {m[0]:.4f}, {m[1]:.4f}, {m[2]:.4f}\n")
        f.write(f"R = {R:.2f}\n")
        f.write(f"Angles: θ₁₂={t12:.2f}°, θ₂₃={t23:.2f}°, θ₁₃={t13:.2f}°\n")
        f.write(f"Σm_ν = {sum_m:.6f} eV\n")
        f.write(f"J = {J:.4f}\n")
    print("✓ Saved.")

print("\n✅ Scan complete.")