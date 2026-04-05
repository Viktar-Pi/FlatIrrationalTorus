#!/usr/bin/env python3
"""
run_all_tests.py — Единый скрипт валидации модели IT³
Заменяет bash run_validation.sh. Работает на macOS/Linux/Windows.
Автор: Виктор Логвинович <lomakez@icloud.com>
"""
import os
import sys
import numpy as np
import healpy as hp
from scipy.stats import chi2
from sympy.physics.wigner import wigner_3j
from datetime import datetime

# ================= КОНФИГУРАЦИЯ =================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "data")
RESULTS_DIR= os.path.join(SCRIPT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Ожидаемые файлы данных
MAP_FILE  = os.path.join(DATA_DIR, "COM_CMB_IQU-smica_2048_R3.00_full.fits")
MASK_FILE = os.path.join(DATA_DIR, "COM_Mask_CMB-common-Mask-Pol_2048_R3.00.fits")
CL_FILE   = os.path.join(DATA_DIR, "COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt")

# Параметры модели
LX = 28.8      # Гпк
CHI_REC = 14.0 # Гпк
L_AXIS = 260.0
B_AXIS = 50.0
G_THRESH = 0.031

def banner(msg):
    print("\n" + "="*60)
    print(f" {msg}")
    print("="*60)

def check_dependencies():
    missing = []
    for f in [MAP_FILE, MASK_FILE, CL_FILE]:
        if not os.path.exists(f):
            missing.append(os.path.basename(f))
    return missing

def run_biposh():
    banner("🔬 ТЕСТ 1: BipoSH (Статистическая анизотропия)")
    try:
        print("📥 Загрузка карты и маски...")
        map_T = hp.read_map(MAP_FILE, field=0)
        mask  = hp.read_map(MASK_FILE)
        
        map_masked = map_T * mask
        w2 = np.mean(mask**2)
        print(f"✅ Маска применена. f_sky (w2) = {w2*100:.1f}%")
        
        print("🔢 Вычисление a_lm (ℓ=2–50)...")
        alm = hp.map2alm(map_masked, lmax=50, use_pixel_weights=True)
        
        ells = np.arange(2, 51)
        A_vals = np.zeros_like(ells, dtype=float)
        l_axis, b_axis = np.deg2rad(L_AXIS), np.deg2rad(B_AXIS)
        Y20_factor = np.sqrt(5/(4*np.pi)) * (3*np.cos(b_axis)**2 - 1)/2
        
        for i, ell in enumerate(ells):
            s = 0.0
            for m in range(-ell, ell+1):
                idx = hp.Alm.getidx(ell, m)
                if idx < len(alm):
                    a = alm[idx]
                    if m < 0:
                        a = ((-1)**abs(m)) * np.conj(a)
                    s += np.real(a * np.conj(a)) * Y20_factor
            A_vals[i] = s / (2*ell + 1)
            
        A_vals /= w2  # поправка на потерю мощности
        
        print("📈 Загрузка спектра ΛCDM и конверсия A → g_*...")
        cl_data = np.loadtxt(CL_FILE)
        D_ell = np.interp(ells, cl_data[:,0], cl_data[:,1])
        C_ell_lcdm = D_ell * 2 * np.pi / (ells * (ells + 1))
        
        g_vals, weights = [], []
        for i, ell in enumerate(ells):
            w3j = float(wigner_3j(ell, ell, 2, 0, 0, 0))
            norm = np.sqrt(5/(4*np.pi)) * w3j
            if np.abs(norm) < 1e-15: continue
            g_l = A_vals[i] / (C_ell_lcdm[i] * norm)
            g_vals.append(g_l)
            weights.append(C_ell_lcdm[i]**2)
            
        g_star = np.average(g_vals, weights=weights) if g_vals else 0.0
        
        # Статистика
        g_obs, g_sig = 0.002, 0.016
        chi2_val = ((g_star - g_obs) / g_sig)**2
        p_val = 1 - chi2.cdf(chi2_val, df=1)
        status = "PASS" if abs(g_star) < G_THRESH else "FAIL"
        
        print(f"\n📊 РЕЗУЛЬТАТ BipoSH:")
        print(f"   g_*^model = {g_star:+.5f}")
        print(f"   g_*^obs   = {g_obs:.3f} ± {g_sig:.3f} (Kim & Komatsu 2013)")
        print(f"   χ² = {chi2_val:.3f}, p-value = {p_val:.4f}")
        print(f"   95% CL: |g_*| < {G_THRESH} ? {'✅ PASS' if status=='PASS' else '❌ FAIL'}")
        
        return {"g_star": g_star, "chi2": chi2_val, "p": p_val, "status": status}
        
    except Exception as e:
        print(f"❌ Ошибка в BipoSH: {e}")
        return {"g_star": None, "chi2": None, "p": None, "status": "ERROR"}

def run_cits():
    banner("📐 ТЕСТ 2: CITS (Геометрия торa)")
    print(f"📏 Параметры: L_min = {LX:.1f} Гпк, 2×χ_rec = {2*CHI_REC:.1f} Гпк")
    
    if LX >= 2 * CHI_REC:
        print("✅ Геометрия: Топология больше горизонта наблюдений.")
        print("   Сфера последнего рассеяния не пересекает саму себя.")
        print("   Парные окружности физически невозможны.")
        print("STATUS: PASS_GEOM")
        return {"status": "PASS_GEOM", "radius": None, "corr": None}
    else:
        print("⚠️  Геометрия: Топология меньше горизонта. Требуется поиск корреляций.")
        # Здесь можно добавить полный алгоритм extract_ring, 
        # но для текущих параметров LX=28.8 он не вызывается.
        return {"status": "SKIP", "radius": None, "corr": None}

def save_report(biposh, cits):
    report_path = os.path.join(RESULTS_DIR, "report_final.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Отчёт валидации $\\mathbb{{IT}}^3$\n\n")
        f.write(f"**Дата**: {now}\n\n")
        f.write("## Результаты тестов\n\n")
        
        f.write("### BipoSH\n")
        if biposh["status"] == "ERROR":
            f.write("❌ Ошибка выполнения\n")
        else:
            f.write(f"- $g_*^{{\\text{{model}}}} = {biposh['g_star']:+.5f}$\n")
            f.write(f"- $\\chi^2 = {biposh['chi2']:.3f}$, $p = {biposh['p']:.4f}$\n")
            f.write(f"- Статус: **{biposh['status']}**\n")
            
        f.write("\n### CITS\n")
        f.write(f"- Статус: **{cits['status']}**\n")
        f.write(f"- Геометрическое пересечение: {'Да' if LX < 2*CHI_REC else 'Нет'}\n")
        
        f.write("\n## Сводка\n")
        f.write("| Тест | Статус |\n|------|--------|\n")
        f.write(f"| BipoSH | {biposh['status']} |\n")
        f.write(f"| CITS   | {cits['status']} |\n")
        
        f.write("\n## Воспроизводимость\n")
        f.write("```bash\npython3 run_all_tests.py\n```\n")
        f.write(f"Данные: `{DATA_DIR}/`\n")
        
    print(f"\n📄 Отчёт сохранён: {report_path}")

def main():
    print("╔════════════════════════════════════════╗")
    print("║  FlatIrrationalTorus v1.0 — Валидация  ║")
    print("╚════════════════════════════════════════╝")
    
    missing = check_dependencies()
    if missing:
        print("\n❌ Отсутствуют файлы данных:")
        for name in missing:
            print(f"   - {name}")
        print("\n💡 Запустите загрузку:")
        print("   bash scripts/download_data.sh")
        sys.exit(1)
        
    print("\n✅ Все файлы данных найдены. Начинаю вычисления...\n")
    
    biposh_res = run_biposh()
    cits_res   = run_cits()
    
    save_report(biposh_res, cits_res)
    
    banner("✅ ВАЛИДАЦИЯ ЗАВЕРШЕНА")
    print("📊 См. отчёт: results/report_final.md")
    print("📋 Логи выводились в консоль выше.")
    print("\n🔗 Следующие шаги:")
    print("   • Байесовский анализ: docs/cobaya_guide.md")
    print("   • Визуализация: python3 notebooks/03_plotting.ipynb")
    print("   • Публикация: docs/falsifiability_checklist.md")

if __name__ == "__main__":
    main()
