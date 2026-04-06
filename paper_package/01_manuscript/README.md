# Manuscript Sources — Flat Irrational Torus Model

This folder contains the LaTeX source files for the main manuscript submitted to Physical Review Letters.

## 📄 Files

| File | Description |
|------|-------------|
| `main.tex` | Main manuscript source (English, PRL format) |
| `main.pdf` | Compiled PDF for submission |
| `main_ru.pdf` | Russian translation (for broader dissemination) |
| `references.bib` | BibTeX bibliography database |

## 🔧 Compilation

To compile the manuscript locally:

```bash
# Using pdflatex + bibtex
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Or using latexmk (recommended)
latexmk -pdf main.tex

📋 PRL Formatting Notes
Document class: revtex4-2 (APS style)
Page limit: ~4 pages (PRL Letter format)
Figures: Embedded as PDF/PNG, 300+ DPI
Equations: Numbered, referenced as Eq.~(1)
🔗 Related
Supplementary Materials: ../02_supplementary/
Administrative Docs: ../03_administrative/
GitHub Repository: https://github.com/Viktar-Pi/FlatIrrationalTorus
Zenodo Archive: https://doi.org/10.5281/zenodo.19440498
Last updated: April 2026



4. Нажмите **Commit changes**

---

## 📁 Шаг 2: Переместите файлы статьи в новую папку

**Действия:**

1. Откройте файл `main.tex` в корне репозитория
2. Нажмите ✏️ **Edit** → в правом верхнем углу нажмите **Move** (иконка 📄→📁)
3. Введите новый путь: `paper_package/01_manuscript/main.tex`
4. Нажмите **Commit changes**

**Повторите для:**
- `main.pdf` → `paper_package/01_manuscript/main.pdf`
- `main_ru.pdf` → `paper_package/01_manuscript/main_ru.pdf`
- `references.bib` → `paper_package/01_manuscript/references.bib`

> 💡 **Совет:** Если кнопка **Move** не отображается, вы можете:
> 1. Скопировать содержимое файла
> 2. Создать новый файл в нужной папке
> 3. Вставить контент
> 4. Удалить старый файл

---

## 📄 Шаг 3: Создайте `paper_package/02_supplementary/README.md`

**Действия:**
1. **Add file** → **Create new file**
2. Имя: `paper_package/02_supplementary/README.md`
3. Контент:

```markdown
# Supplementary Materials — Flat Irrational Torus Model

This folder contains additional technical materials that support the main manuscript but are too detailed for the primary PRL letter format.

## 📄 Contents

| File | Description |
|------|-------------|
| `supplementary.tex` | LaTeX source for supplementary document |
| `supplementary.pdf` | Compiled supplementary PDF |
| `additional_plots/` | Extended figure set (high-resolution) |
| `derivations/` | Detailed mathematical derivations |
| `validation_tests/` | Additional convergence and robustness checks |

## 🔬 What's Included

### Mathematical Derivations
- Full derivation of the topological transfer function F(ℓ)
- Proof of irrational ratio suppression of anisotropy
- Detailed BipoSH analysis methodology

### Additional Figures
- Corner plots with extended parameter sets
- Residual plots: IT³ vs ΛCDM
- Sensitivity analysis for prior choices

### Validation Tests
- Gelman-Rubin convergence diagnostics for all chains
- Importance-sampling weights distribution (DESI validation)
- Alternative topology configurations (rational ratios)

## 📊 How to Use

To regenerate supplementary figures:
```bash
cd FlatIrrationalTorus
python3 scripts/plot_supplementary.py

To compile the supplementary PDF:
cd paper_package/02_supplementary
pdflatex supplementary.tex

🔗 Related
Main Manuscript: ../01_manuscript/
Administrative Docs: ../03_administrative/
GitHub Repository: https://github.com/Viktar-Pi/FlatIrrationalTorus
Last updated: April 2026



4. **Commit changes**

---

## 📄 Шаг 4: Создайте `paper_package/03_administrative/README.md`

**Действия:**
1. **Add file** → **Create new file**
2. Имя: `paper_package/03_administrative/README.md`
3. Контент:

```markdown
# Administrative Documents — Flat Irrational Torus Model

This folder contains legal, ethical, and procedural statements required for journal submission and open science compliance.

## 📄 Documents

| File | Purpose | Required by |
|------|---------|-------------|
| `author_contributions.md` | CRediT taxonomy statement | APS, PRL |
| `conflict_of_interest.md` | COI declaration | APS, PRL |
| `data_availability.md` | FAIR data statement | APS, PRL, funders |
| `ethics_statement.md` | Research ethics declaration | APS |

## 📋 Quick Reference

### Author Contributions (CRediT)
- **Conceptualization, Methodology, Software, Validation, Formal Analysis, Investigation, Resources, Data Curation, Writing, Visualization, Project Administration**: Viktor Logvinovich
- **Funding Acquisition**: N/A (self-funded)

### Conflict of Interest
- No financial or non-financial conflicts declared
- Independent researcher status confirmed
- Full code/data transparency provided

### Data Availability
- Primary data: Planck PR4, DESI 2024, Pantheon+ (public archives)
- Derived data: MCMC chains, figures (GitHub + Zenodo)
- Code: MIT License, Docker container for reproducibility

### Ethics
- No human/animal subjects
- No dual-use concerns
- Computational resources used efficiently

## 🔗 Submission Checklist

- [x] Author contributions statement
- [x] Conflict of interest declaration
- [x] Data availability statement
- [x] Ethics statement
- [x] Cover letter (in root `/paper/`)
- [x] Suggested reviewers list (in submission system)

## 📬 Contact

For questions about administrative documents:
**Viktor Logvinovich** — lomakez@icloud.com

---

*Last updated: April 2026*
