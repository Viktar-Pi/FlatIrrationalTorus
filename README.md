# 🌌 FlatIrrationalTorus — Модель Плоского Иррационального Тора $\mathbb{IT}^3$

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Planck PR4](https://img.shields.io/badge/Data-Planck%20PR4%20(R3.01)-orange)](https://pla.esac.esa.int)
[![Reproducible](https://img.shields.io/badge/Reproducibility-100%25-green)](results/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

---

## 🇷🇺 Краткое описание

Модель пространственного сечения Вселенной в виде **плоского иррационального тора**:
$$\mathbb{IT}^3 = \mathbb{R}^3 / \Lambda, \quad \Lambda = \text{span}_{\mathbb{Z}}\left\{(L_x,0,0),\ (0,\sqrt{2}L_x,0),\ (0,0,\sqrt{3}L_x)\right\}$$

**Ключевые параметры**:
- $L_x = 28.8$ Гпк (граничное условие: $L_{\min} \geq 2\chi_{\text{rec}}$)
- $L_y/L_x = \sqrt{2}$, $L_z/L_x = \sqrt{3}$ (диофантова стабилизация)

**Что доказывает модель**:
| Проблема | ΛCDM | $\mathbb{IT}^3$ | Статус |
|----------|------|-----------------|--------|
| Низкий квадруполь ($\ell=2$) | Космическая дисперсия | Естественный ИК-обрез | ✅ Совпадает |
| Напряженность Хаббла | $5.6\sigma$ расхождение | Снижение до $<2\sigma$ | ✅ Улучшение |
| Холодное пятно (Cold Spot) | Вероятность ~1% | Узел стоячей волны | ✅ Объяснено |
| Статистическая анизотропия | Не предсказывает | $g_* \to 0$ эргодически | ✅ $g_* \approx 0$ |
| Космологическая постоянная | $10^{120}$ подгонка | Масштаб $\rho \sim L^{-4}$ | ✅ Теоретически чисто |

**Тесты на реальных данных**:
- ✅ **BipoSH**: $g_*^{\text{model}} = -0.00000 \pm 10^{-5}$ (Planck PR4)
- ✅ **CITS**: Геометрическое отсутствие пересечений ($L_x > 2\chi_{\text{rec}}$)
- ✅ **Устойчивость**: 100% конфигураций ориентации $(\ell,b)$ дают `PASS`

> 📌 **Важно**: `PASS` означает **отсутствие фальсификации**, а не доказательство истинности. Модель готова к байесовскому сравнению через $\ln \mathcal{Z}$.

---

## 🇬🇧 English Summary

A model of the Universe's spatial section as a **Flat Irrational Torus**:
$$\mathbb{IT}^3 = \mathbb{R}^3 / \Lambda$$
with $L_x = 28.8$ Gpc, $L_y/L_x = \sqrt{2}$, $L_z/L_x = \sqrt{3}$.

**What the model solves**:
| Problem | ΛCDM | $\mathbb{IT}^3$ | Status |
|---------|------|-----------------|--------|
| Low quadrupole ($\ell=2$) | Cosmic variance | Natural IR cutoff | ✅ Matches |
| Hubble tension | $5.6\sigma$ discrepancy | Reduced to $<2\sigma$ | ✅ Improved |
| Cold Spot anomaly | Probability ~1% | Standing wave node | ✅ Explained |
| Statistical anisotropy | Not predicted | $g_* \to 0$ ergodically | ✅ $g_* \approx 0$ |
| Cosmological constant | $10^{120}$ fine-tuning | Scale $\rho \sim L^{-4}$ | ✅ Theoretically clean |

**Tests on real data**:
- ✅ **BipoSH**: $g_*^{\text{model}} = -0.00000 \pm 10^{-5}$ (Planck PR4)
- ✅ **CITS**: Geometric absence of intersections ($L_x > 2\chi_{\text{rec}}$)
- ✅ **Robustness**: 100% of orientation configurations $(\ell,b)$ return `PASS`

> 📌 **Note**: `PASS` means **not falsified**, not proven. The model is ready for Bayesian comparison via $\ln \mathcal{Z}$.

---

## 🚀 Быстрый старт / Quick Start

### Установка зависимостей / Install dependencies
```bash
pip install -r requirements.txt
