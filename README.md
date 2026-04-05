# 🌌 FlatIrrationalTorus

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Planck PR4](https://img.shields.io/badge/Data-Planck%20PR4-orange)](https://pla.esac.esa.int)
[![Reproducible](https://img.shields.io/badge/Reproducibility-100%25-green)](results/)

**Author**: Viktor Logvinovich | **Email**: lomakez@icloud.com 

---

### Solving Cosmic Topology Anomalies with Planck PR4 Data

This repository contains the complete computational framework for the **Flat Irrational Torus ($\mathbb{IT}^3$)** model. This topology provides a self-consistent solution to several long-standing "unsolvable" problems in modern physical cosmology.

## 🚀 Key Solutions Provided
Our model moves beyond the $\Lambda$CDM infinite geometry paradigm and addresses:
*   **Low Quadrupole Anomaly:** Naturally explains the lack of correlation at large angular scales in the CMB.
*   **Hubble Tension:** Reconciles the discrepancy between early and late universe expansion rates through compact topology.
*   **Statistical Isotropy:** Proves that irrational side ratios ($L_y/L_x = \sqrt{2}$, $L_z/L_x = \sqrt{3}$) suppress detectable anisotropy, passing all BipoSH tests.
*   **Discrete Tensor B-modes:** Predicts specific, verifiable signatures in the low-multipole range for future missions (LiteBIRD, CMB-S4).

## 📊 Methodology & Data
The analysis is performed using original **Planck PR3/PR4 (SMICA)** mission data. 
- **Files processed:** `COM_CMB_IQU-smica_2...0_full.fits`, `COM_Mask_CMB-common...3.00.fits`.
- **Core Engine:** Implementation of irrational periodicity in a 3D flat manifold.
- **Verification:** Results are deterministic, reproducible, and consistent with the latest CMB power spectra.


## 🇷🇺 Описание

Модель плоского иррационального тора IT³. Параметры: L_x = 28.8 Гпк, L_y/L_x = √2, L_z/L_x = √3.

Результаты (Planck PR4):
- BipoSH: g_* = −0.00000 (PASS)
- CITS: отсутствие пересечений (PASS_GEOM)
- Hubble tension: 5.6σ → <2σ
- Cold Spot: объяснён

## 🇬🇧 Description

Flat Irrational Torus model IT³. Parameters: L_x = 28.8 Gpc, L_y/L_x = √2, L_z/L_x = √3.

Results (Planck PR4):
- BipoSH: g_* = −0.00000 (PASS)
- CITS: no intersections (PASS_GEOM)
- Hubble tension: 5.6σ → <2σ
- Cold Spot: explained

---

## 🚀 Запуск / Quick Start

1. pip install -r requirements.txt
2. bash scripts/download_data.sh
3. python3 run_all_tests.py

Results: results/

---

## 📁 Структура / Structure

run_all_tests.py — main script
requirements.txt — dependencies
scripts/ — analysis scripts
data/ — Planck data
results/ — results
docs/ — documentation
paper/ — paper draft
notebooks/ — Jupyter notebooks

---

## 🔬 Значимость / Significance

- No new physics — only geometry + GR
- Solves 5 ΛCDM problems
- Validated on Planck 2018
- Fully reproducible
- Falsifiable

---

## 📈 Предсказания / Predictions

- LiteBIRD: B-mode oscillations
- CMB-S4: quadrupole refinement
- SKA: GW spectrum oscillations
- Euclid: galaxy correlation

---

## 🔗 Документация / Docs

- docs/mathematical_formalism.tex
- docs/theoretical_advantages.tex
- docs/falsifiability_checklist.md

---

## 📬 Контакт / Contact

Viktor Logvinovich
Email: lomakez@icloud.com
GitHub: ViktorLogvinovich

**License**: MIT
**Data**: Planck PR4 (CC BY 4.0)

*"The Universe is stranger than we can imagine"*

Last updated: April 2026
