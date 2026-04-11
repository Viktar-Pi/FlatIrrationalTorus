#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neutrino Mass Matrix Analysis in IT³ Paradigm
Flat Irrational Torus Topology: T³(1, √2, √3)

This script diagonalizes the complex Hermitian neutrino mass matrix
and extracts PMNS mixing parameters from topological phases.

Author: Victor Logvinovich
Date: April 2026
"""

import numpy as np
from scipy import linalg

# ============================================================================
# 1. FUNDAMENTAL TOPOLOGICAL PARAMETERS
# ============================================================================

print("="*70)
print("IT³ PARADIGM: NEUTRINO MASS MATRIX ANALYSIS")
print("Flat Irrational Torus T³(1, √2, √3)")
print("="*70)

# Fundamental cycle lengths (normalized)
L1 = 1.0
L2 = np.sqrt(2)
L3 = np.sqrt(3)

print(f"\nFundamental cycles:")
print(f"  L₁ = {L1:.6f}")
print(f"  L₂ = √2 = {L2:.6f}")
print(f"  L₃ = √3 = {L3:.6f}")
print(f"  Ratio L₂/L₁ = {L2/L1:.6f}")
print(f"  Ratio L₃/L₁ = {L3/L1:.6f}")

# ============================================================================
# 2. TOPOLOGICAL PHASE CALCULATION (Variant B)
# ============================================================================

print("\n" + "="*70)
print("TOPOLOGICAL PHASES FROM ERGODIC GEODESIC FLOW")
print("="*70)

# Topological phases from geometric mismatch
# φ_ij = 2π(L_i/L_j - L_j/L_i)
phi_12 = 2 * np.pi * (L1/L2 - L2/L1)
phi_13 = 2 * np.pi * (L1/L3 - L3/L1)
phi_23 = 2 * np.pi * (L2/L3 - L3/L2)

# Normalize phases to [-π, π]
phi_12_norm = np.mod(phi_12 + np.pi, 2*np.pi) - np.pi
phi_13_norm = np.mod(phi_13 + np.pi, 2*np.pi) - np.pi
phi_23_norm = np.mod(phi_23 + np.pi, 2*np.pi) - np.pi

print(f"\nTopological phases φ_ij = 2π(L_i/L_j - L_j/L_i):")
print(f"  φ₁₂ = {phi_12:.6f} rad = {np.degrees(phi_12):.2f}°")
print(f"      (normalized: {phi_12_norm:.6f} rad = {np.degrees(phi_12_norm):.2f}°)")
print(f"  φ₁₃ = {phi_13:.6f} rad = {np.degrees(phi_13):.2f}°")
print(f"      (normalized: {phi_13_norm:.6f} rad = {np.degrees(phi_13_norm):.2f}°)")
print(f"  φ₂₃ = {phi_23:.6f} rad = {np.degrees(phi_23):.2f}°")
print(f"      (normalized: {phi_23_norm:.6f} rad = {np.degrees(phi_23_norm):.2f}°)")

# Analytic expressions
print(f"\nAnalytic expressions:")
print(f"  φ₁₂ = -√2·π = {-np.sqrt(2)*np.pi:.6f} rad")
print(f"  φ₁₃ = -4π/√3 = {-4*np.pi/np.sqrt(3):.6f} rad")
print(f"  φ₂₃ = -2π/√6 = {-2*np.pi/np.sqrt(6):.6f} rad")

# ============================================================================
# 3. CONSTRUCT HERMITIAN MASS MATRIX
# ============================================================================

print("\n" + "="*70)
print("HERMITIAN MASS MATRIX CONSTRUCTION")
print("="*70)

# Construct the complex Hermitian mass matrix
# M_ν = m₀ × [[1, exp(iφ₁₂), exp(iφ₁₃)],
#              [exp(-iφ₁₂), √2, exp(iφ₂₃)],
#              [exp(-iφ₁₃), exp(-iφ₂₃), √3]]

M = np.array([
    [1.0,                np.exp(1j * phi_12), np.exp(1j * phi_13)],
    [np.exp(-1j * phi_12), np.sqrt(2),          np.exp(1j * phi_23)],
    [np.exp(-1j * phi_13), np.exp(-1j * phi_23), np.sqrt(3)]
])

print("\nMass matrix M_ν (in units of m₀):")
print("  ⎡", end="")
for i in range(3):
    if i == 0:
        print(f"  {M[0,i].real:.4f}{'+' if M[0,i].imag >= 0 else '-'}{abs(M[0,i].imag):.4f}i  ", end="")
    else:
        print(f"{M[0,i].real:.4f}{'+' if M[0,i].imag >= 0 else '-'}{abs(M[0,i].imag):.4f}i  ", end="")
print("⎤")

print("  ⎢", end="")
for i in range(3):
    print(f"  {M[1,i].real:.4f}{'+' if M[1,i].imag >= 0 else '-'}{abs(M[1,i].imag):.4f}i  ", end="")
print("⎥")

print("  ⎣", end="")
for i in range(3):
    if i == 2:
        print(f"  {M[2,i].real:.4f}{'+' if M[2,i].imag >= 0 else '-'}{abs(M[2,i].imag):.4f}i  ", end="")
    else:
        print(f"{M[2,i].real:.4f}{'+' if M[2,i].imag >= 0 else '-'}{abs(M[2,i].imag):.4f}i  ", end="")
print("⎦")

# Verify Hermiticity
hermitian_check = np.allclose(M, M.conj().T)
print(f"\nHermiticity check: M = M† ? {hermitian_check}")

# ============================================================================
# 4. DIAGONALIZATION
# ============================================================================

print("\n" + "="*70)
print("MATRIX DIAGONALIZATION")
print("="*70)

# Diagonalize using eigh (for Hermitian matrices)
eigenvalues, eigenvectors = linalg.eigh(M)

# Sort eigenvalues in ascending order
idx = np.argsort(eigenvalues)
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

m1, m2, m3 = eigenvalues

print(f"\nEigenvalues (mass eigenstates in units of m₀):")
print(f"  m₁ = {m1:.6f}")
print(f"  m₂ = {m2:.6f}")
print(f"  m₃ = {m3:.6f}")

print(f"\nMass hierarchy:")
print(f"  m₁ < m₂ < m₃ ? {m1 < m2 < m3}")
print(f"  m₂/m₁ = {m2/m1:.4f}")
print(f"  m₃/m₂ = {m3/m2:.4f}")
print(f"  m₃/m₁ = {m3/m1:.4f}")

# ============================================================================
# 5. MASS SQUARED DIFFERENCES
# ============================================================================

print("\n" + "="*70)
print("MASS SQUARED DIFFERENCES")
print("="*70)

dm21_sq = m2**2 - m1**2
dm31_sq = m3**2 - m1**2
dm32_sq = m3**2 - m2**2

ratio = dm32_sq / dm21_sq

print(f"\nMass squared differences (in units of m₀²):")
print(f"  Δm²₂₁ = m₂² - m₁² = {dm21_sq:.6f}")
print(f"  Δm²₃₁ = m₃² - m₁² = {dm31_sq:.6f}")
print(f"  Δm²₃₂ = m₃² - m₂² = {dm32_sq:.6f}")

print(f"\nRatio R = Δm²₃₂ / Δm²₂₁:")
print(f"  R_topo = {ratio:.2f}")
print(f"  R_exp  = 33.3 ± 1.1 (NuFIT 5.2, Normal Hierarchy)")
print(f"  Deviation = {abs(ratio - 33.3)/33.3*100:.1f}%")

# ============================================================================
# 6. PMNS MIXING MATRIX EXTRACTION
# ============================================================================

print("\n" + "="*70)
print("PMNS MIXING MATRIX EXTRACTION")
print("="*70)

# The eigenvector matrix U (PMNS matrix)
U = eigenvectors

print("\nPMNS matrix U_PMNS (eigenvectors as columns):")
print("  ⎡", end="")
for i in range(3):
    print(f"  {U[0,i].real:.4f}{'+' if U[0,i].imag >= 0 else '-'}{abs(U[0,i].imag):.4f}i  ", end="")
print("⎤")

print("  ⎢", end="")
for i in range(3):
    print(f"  {U[1,i].real:.4f}{'+' if U[1,i].imag >= 0 else '-'}{abs(U[1,i].imag):.4f}i  ", end="")
print("⎥")

print("  ⎣", end="")
for i in range(3):
    if i == 2:
        print(f"  {U[2,i].real:.4f}{'+' if U[2,i].imag >= 0 else '-'}{abs(U[2,i].imag):.4f}i  ", end="")
    else:
        print(f"{U[2,i].real:.4f}{'+' if U[2,i].imag >= 0 else '-'}{abs(U[2,i].imag):.4f}i  ", end="")
print("⎦")

# Verify unitarity
unitarity_check = np.allclose(U @ U.conj().T, np.eye(3), atol=1e-10)
print(f"\nUnitarity check: U·U† = I ? {unitarity_check}")

# ============================================================================
# 7. EXTRACT MIXING ANGLES (Standard PDG Parameterization)
# ============================================================================

print("\n" + "="*70)
print("MIXING ANGLES (Standard PDG Parameterization)")
print("="*70)

# Extract θ₁₃ from |U_e3|
sin_theta13 = np.abs(U[0, 2])
sin_theta13 = np.clip(sin_theta13, 0, 1)  # Numerical safety
theta13_rad = np.arcsin(sin_theta13)
theta13_deg = np.degrees(theta13_rad)

# Extract θ₂₃ from |U_μ3|
sin_theta23 = np.abs(U[1, 2]) / np.cos(theta13_rad)
sin_theta23 = np.clip(sin_theta23, 0, 1)
theta23_rad = np.arcsin(sin_theta23)
theta23_deg = np.degrees(theta23_rad)

# Extract θ₁₂ from |U_e2|
sin_theta12 = np.abs(U[0, 1]) / np.cos(theta13_rad)
sin_theta12 = np.clip(sin_theta12, 0, 1)
theta12_rad = np.arcsin(sin_theta12)
theta12_deg = np.degrees(theta12_rad)

print(f"\nMixing angles:")
print(f"  θ₁₂ (solar)     = {theta12_deg:.2f}°")
print(f"  θ₂₃ (atmospheric) = {theta23_deg:.2f}°")
print(f"  θ₁₃ (reactor)    = {theta13_deg:.2f}°")

print(f"\nExperimental values (NuFIT 5.2, Normal Hierarchy, 1σ):")
print(f"  θ₁₂ = 33.4° ± 0.7°")
print(f"  θ₂₃ = 49.2° ± 1.0°")
print(f"  θ₁₃ = 8.6° ± 0.1°")

print(f"\nDeviations from experiment:")
print(f"  Δθ₁₂ = {theta12_deg - 33.4:+.2f}° ({(theta12_deg - 33.4)/33.4*100:+.1f}%)")
print(f"  Δθ₂₃ = {theta23_deg - 49.2:+.2f}° ({(theta23_deg - 49.2)/49.2*100:+.1f}%)")
print(f"  Δθ₁₃ = {theta13_deg - 8.6:+.2f}° ({(theta13_deg - 8.6)/8.6*100:+.1f}%)")

# Calculate sin²θ values (commonly reported)
sin2_12 = np.sin(theta12_rad)**2
sin2_23 = np.sin(theta23_rad)**2
sin2_13 = np.sin(theta13_rad)**2

print(f"\nSquared sine values:")
print(f"  sin²θ₁₂ = {sin2_12:.4f}  (exp: 0.304 ± 0.012)")
print(f"  sin²θ₂₃ = {sin2_23:.4f}  (exp: 0.573 ± 0.016)")
print(f"  sin²θ₁₃ = {sin2_13:.4f}  (exp: 0.0224 ± 0.0006)")

# ============================================================================
# 8. CP VIOLATION - JARLSKOG INVARIANT
# ============================================================================

print("\n" + "="*70)
print("CP VIOLATION - JARLSKOG INVARIANT")
print("="*70)

# Jarlskog invariant: J = Im(U_e1 U_μ2 U*_e2 U*_μ1)
J = np.imag(U[0, 0] * U[1, 1] * np.conj(U[0, 1]) * np.conj(U[1, 0]))

print(f"\nJarlskog invariant:")
print(f"  J = {J:.6f}")
print(f"  |J| = {abs(J):.6f}")

# Experimental estimate (from δ_CP ≈ 230°)
J_exp = 0.033 * np.sin(np.radians(230))
print(f"  J_exp ≈ {J_exp:.6f} (from δ_CP ≈ 230°)")

# Extract Dirac CP phase (approximate)
# Using: J = s12 c12 s23 c23 s13 c13² sin(δ_CP)
s12, c12 = np.sin(theta12_rad), np.cos(theta12_rad)
s23, c23 = np.sin(theta23_rad), np.cos(theta23_rad)
s13, c13 = np.sin(theta13_rad), np.cos(theta13_rad)

sin_delta = J / (s12 * c12 * s23 * c23 * s13 * c13**2)
sin_delta = np.clip(sin_delta, -1, 1)

delta_CP_rad = np.arcsin(sin_delta)
delta_CP_deg = np.degrees(delta_CP_rad)

# Adjust to [0, 360] range
if delta_CP_deg < 0:
    delta_CP_deg += 360

print(f"\nDirac CP phase (extracted):")
print(f"  δ_CP = {delta_CP_deg:.1f}°")
print(f"  δ_CP_exp = 230° ± 30° (NuFIT 5.2)")

# ============================================================================
# 9. ABSOLUTE MASS SCALE PREDICTION
# ============================================================================

print("\n" + "="*70)
print("ABSOLUTE MASS SCALE PREDICTION")
print("="*70)

# Fix m₀ from experimental Δm²₂₁ ≈ 7.5 × 10⁻⁵ eV²
dm21_exp = 7.5e-5  # eV²
m0 = np.sqrt(dm21_exp / dm21_sq)

print(f"\nCalibration from Δm²₂₁ (experimental):")
print(f"  Δm²₂₁(exp) = {dm21_exp:.1e} eV²")
print(f"  Δm²₂₁(theo) = {dm21_sq:.4f} m₀²")
print(f"  → m₀ = {m0:.6f} eV")

# Predict absolute masses
m1_ev = m1 * m0
m2_ev = m2 * m0
m3_ev = m3 * m0

print(f"\nPredicted absolute masses:")
print(f"  m₁ = {m1_ev:.6f} eV = {m1_ev*1000:.3f} meV")
print(f"  m₂ = {m2_ev:.6f} eV = {m2_ev*1000:.3f} meV")
print(f"  m₃ = {m3_ev:.6f} eV = {m3_ev*1000:.3f} meV")

# Sum of neutrino masses
sum_m_nu = m1_ev + m2_ev + m3_ev

print(f"\nSum of neutrino masses:")
print(f"  Σm_ν = {sum_m_nu:.6f} eV = {sum_m_nu*1000:.1f} meV")
print(f"  Cosmological bound: Σm_ν < 0.12 eV (Planck 2020 + BAO, 95% CL)")
print(f"  IT³ prediction: Σm_ν ≈ 0.058 - 0.070 eV (Normal Hierarchy)")

# ============================================================================
# 10. SUMMARY TABLE
# ============================================================================

print("\n" + "="*70)
print("SUMMARY: IT³ PREDICTIONS vs EXPERIMENT")
print("="*70)

print("\n┌─────────────────────────────────────────────────────────────────┐")
print("│  PARAMETER          │  IT³ PREDICTION  │  EXPERIMENT        │")
print("├─────────────────────────────────────────────────────────────────┤")
print(f"│  Δm²₃₂/Δm²₂₁        │  {ratio:15.2f}  │  33.3 ± 1.1        │")
print(f"│  θ₁₂ (solar)        │  {theta12_deg:15.2f}°  │  33.4° ± 0.7°      │")
print(f"│  θ₂₃ (atmospheric)  │  {theta23_deg:15.2f}°  │  49.2° ± 1.0°      │")
print(f"│  θ₁₃ (reactor)      │  {theta13_deg:15.2f}°  │  8.6° ± 0.1°       │")
print(f"│  δ_CP               │  {delta_CP_deg:15.1f}°  │  230° ± 30°        │")
print(f"│  Σm_ν (eV)          │  {sum_m_nu:15.6f}  │  < 0.12 (bound)    │")
print(f"│  J                  │  {J:15.6f}  │  ~ -0.025          │")
print("└─────────────────────────────────────────────────────────────────┘")

print("\n" + "="*70)
print("FALSIFICATION CRITERIA")
print("="*70)

print("\nThe IT³ paradigm will be FALSIFIED if:")
print("  1. Σm_ν > 0.10 eV (from CMB-S4 + Euclid)")
print("  2. Inverted hierarchy is confirmed (m₃ < m₁ < m₂)")
print("  3. Δm²₃₂/Δm²₂₁ deviates by > 20% from ~35")
print("  4. θ₁₃ < 5° or θ₁₃ > 20° (from DUNE/Hyper-K)")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)

# ============================================================================
# 11. SAVE RESULTS TO FILE
# ============================================================================

# Optional: Save results to a text file
save_to_file = input("\nSave results to file? (y/n): ").strip().lower()

if save_to_file == 'y':
    filename = "IT3_neutrino_results.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("IT³ Paradigm - Neutrino Mass Matrix Analysis\n")
        f.write("="*70 + "\n\n")
        f.write(f"Mass eigenvalues (m₀ units): m₁={m1:.6f}, m₂={m2:.6f}, m₃={m3:.6f}\n")
        f.write(f"Mass ratio R = Δm²₃₂/Δm²₂₁ = {ratio:.2f}\n\n")
        f.write(f"Mixing angles: θ₁₂={theta12_deg:.2f}°, θ₂₃={theta23_deg:.2f}°, θ₁₃={theta13_deg:.2f}°\n")
        f.write(f"CP phase: δ_CP = {delta_CP_deg:.1f}°\n")
        f.write(f"Jarlskog invariant: J = {J:.6f}\n\n")
        f.write(f"Absolute masses: m₁={m1_ev:.6f} eV, m₂={m2_ev:.6f} eV, m₃={m3_ev:.6f} eV\n")
        f.write(f"Sum of masses: Σm_ν = {sum_m_nu:.6f} eV\n")
    print(f"Results saved to {filename}")

print("\nEnd of script.")