# 🌌 FlatIrrationalTorus

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Planck PR4](https://img.shields.io/badge/Data-Planck%20PR4-orange)](https://pla.esac.esa.int)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19440498.svg)](https://doi.org/10.5281/zenodo.19440498)

> **Manuscript submitted to Physical Review Letters** (April 2026)  
> *Tracking ID: es2026apr06_647*

## 🎯 Overview

Complete computational framework for the **Flat Irrational Torus (IT³)** model — a compact flat topology providing geometric solutions to the low-ℓ CMB anomaly and Hubble tension without new physics beyond General Relativity.

### Key Results (Planck PR4 TT)

- **Topology Scale:** L<sub>x</sub> = 28.57<sup>+0.73</sup><sub>-0.87</sub> Gpc (consistent with L<sub>x</sub> ≥ 2χ<sub>rec</sub>)
- **Hubble Constant:** H<sub>0</sub> = 67.55 ± 1.77 km/s/Mpc (reduces tension from 5σ to 2.68σ)
- **Fit Improvement:** Δχ² = -5.33 vs ΛCDM (>2σ improvement)
- **Information Criterion:** ΔBIC = +2.49 ("inconclusive to positive")
- **Correlation:** r(L<sub>x</sub>, H<sub>0</sub>) = 0.258
- **Validation:** N<sub>eff</sub> = 17,633 (27% survival with DESI 2024 + Pantheon+)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/Viktar-Pi/FlatIrrationalTorus.git
cd FlatIrrationalTorus
docker build -t it3-analysis .
docker run -v $(pwd)/results:/app/results it3-analysis python3 analysis/run_all.py
```

### Option 2: Native Python

```bash
pip install -r requirements.txt
python3 scripts/download_planck_data.py
python3 analysis/run_all.py
```

## 📁 Repository Structure

```
FlatIrrationalTorus/
├── analysis/           # MCMC pipeline and likelihood
│   ├── run_all.py
│   ├── likelihood_it3.py
│   ├── mcmc_sampler.py
│   └── utils.py
├── scripts/            # Plotting and utilities
│   ├── plot_correlation.py
│   ├── plot_corner.py
│   ├── check_survival.py
│   └── extract_stats.py
├── data/               # MCMC chains
│   ├── samples_it3.pkl
│   └── samples_lcdm.pkl
├── figures/            # Publication figures
│   ├── corner_it3.png
│   ├── correlation_Lx_H0.png
│   └── survival_check_DESI.png
├── paper/              # LaTeX manuscript
│   ├── main.tex
│   └── references.bib
├── notebooks/          # Jupyter explorations
├── docker/             # Reproducible environment
│   ├── Dockerfile
│   └── requirements.txt
├── tests/              # Unit tests
├── docs/               # Documentation
├── LICENSE             # MIT License
├── CITATION.cff        # Citation metadata
└── README.md           # This file
```

## 🔬 Methodology

**Model:** IT³ topology with L<sub>y</sub>/L<sub>x</sub> = √2, L<sub>z</sub>/L<sub>x</sub> = √3

**Inference:** Bayesian MCMC (emcee, 32 walkers, 5000 steps) with modified CLASS Boltzmann code

**Transfer Function:** Topological suppression F(ℓ) = [1 + exp(-(ℓ-ℓ<sub>cut</sub>)/Δℓ)]⁻¹

**Data:** Planck PR4 (NPIPE) temperature spectrum, 2 ≤ ℓ ≤ 2000

**Convergence:** Gelman-Rubin R̂ < 1.01 for all parameters

## 📈 Predictions for Future Observations

| Mission | Observable | IT³ Prediction |
|---------|-----------|----------------|
| **LiteBIRD** | Low-ℓ B-modes | Characteristic oscillations at ℓ ≲ 10 |
| **CMB-S4** | Quadrupole precision | ΔC<sub>2</sub>/C<sub>2</sub> ~ 5% test |
| **Euclid/DESI** | BAO at z > 2 | Sub-percent deviations in D<sub>M</sub>(z)/r<sub>d</sub> |
| **SKA** | 21cm intensity mapping | Anisotropic correlation at scales ~ L<sub>x</sub> |
| **LISA** | Stochastic GW background | Modulations at f ~ c/L<sub>x</sub> |

## 🔗 Resources

- **Mathematical Formalism:** [`docs/mathematical_formalism.pdf`](docs/mathematical_formalism.pdf)
- **Reproducibility Guide:** [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)
- **Falsifiability Checklist:** [`docs/falsifiability_checklist.md`](docs/falsifiability_checklist.md)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-idea`
3. Commit changes: `git commit -m 'Add amazing idea'`
4. Push to branch: `git push origin feature/amazing-idea`
5. Open a Pull Request

**Guidelines:**
- Follow PEP 8 for Python code
- Include docstrings and type hints
- Add tests for new functionality

## 📬 Contact & Support

**Corresponding Author:**  
Viktor Logvinovich  
📧 lomakez@icloud.com  
🔗 [GitHub Profile](https://github.com/Viktar-Pi)

**Bug Reports & Questions:**  
Please use the [GitHub Issues](https://github.com/Viktar-Pi/FlatIrrationalTorus/issues) tracker.

---

## 📜 License & Citation

### License
This code is distributed under the **MIT License**.  
The manuscript text is licensed under **CC-BY-4.0**.

### Citation
If you use this software or results in your research, please cite:

```bibtex
@article{Logvinovich2026IT3,
  title = {Flat Irrational Torus Topology: Simultaneous Resolution of Low-ℓ Anomaly and Hubble Tension},
  author = {Logvinovich, Victor},
  journal = {Physical Review Letters (submitted)},
  year = {2026},
  doi = {10.5281/zenodo.19440498},
  url = {https://github.com/Viktar-Pi/FlatIrrationalTorus}
}
```

### Zenodo Archive
A permanent, versioned archive of this repository is available at:  
🔗 [10.5281/zenodo.19440498](https://doi.org/10.5281/zenodo.19440498)

---

> *"The Universe is not only stranger than we imagine, it is stranger than we can imagine."*  
> — J.B.S. Haldane

*Last updated: April 2026*
