# IT³ Framework - Computational Tools

This repository contains the computational tools for reproducing the results 
in "IT³ Framework: Geometry as the Primary Substrate of a Deterministic 
Quasicrystalline Universe" by Victor Logvinovich.

## Files

1. **spectral_gap_calculator.py**
   - Computes eigenvalues of -∇² on T³(1, √2, √3)
   - Verifies Lemma 9.1 (spectral gap)
   - Usage: `python spectral_gap_calculator.py`

2. **tension_field_solver.py**
   - Numerical solution of modified Poisson equation
   - ∇²Φ_eff = 4πG(ρ_baryon + ρ_T)
   - Usage: `python tension_field_solver.py`

3. **correlation_aware_fisher.R**
   - Implementation of Definition 11.1
   - Correlation-aware Fisher test for combining p-values
   - Usage: `Rscript correlation_aware_fisher.R`

4. **requirements.txt**
   - Python package dependencies

## Installation

### Python
```bash
pip install -r requirements.txt