#!/usr/bin/env python3
"""
run_all_tests.py — Единый скрипт валидации модели IT³ (ИСПРАВЛЕННЫЙ)
Автор: Виктор Логвинович <lomakez@icloud.com>
Исправление: hp.Alm.getidx(lmax, l, m) — три аргумента
"""
import os, sys, numpy as np, healpy as hp
from scipy.stats import chi2
from sympy.physics.wigner import wigner_3j
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

MAP_FILE = os.path.join(DATA_DIR, "COM_CMB_IQU-smica_2048_R3.00_full.fits")
MASK_FILE = os.path.join(DATA_DIR, "COM_Mask_CMB-common-Mask-Pol_2048_R3.00.fits")
CL_FILE = os.path.join(DATA_DIR, "COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt")

LX, CHI_REC = 28.8, 14.0
L_AXIS, B_AXIS, G_THRESH = 260.0, 50.0, 0.031
LMAX = 50  # Важно: должен совпадать с lmax в map2alm

def banner(msg): print("\n" + "="*60 + f"\n {msg}\n" + "="*60)

def run_biposh():
    banner("🔬 ТЕСТ 1: BipoSH")
    try:
        print("📥 Загрузка данных...")
        map_T = hp.read_map(MAP_FILE, field=0)
        mask = hp.read_map(MASK_FILE)
        
        map_masked = map_T * mask
        w2 = np.mean(mask**2)
        print(f"✅ f_sky = {w2*100:.1f}%")
        
        print(f"🔢 Вычисление a_lm (ℓ=2–{LMAX})...")
        alm = hp.map2alm(map_masked, lmax=LMAX, use_pixel_weights=True)
        
        ells = np.arange(2, LMAX + 1)
        A_vals = np.zeros_like(ells, dtype=float)
        la, ba = np.deg2rad(L_AXIS), np.deg2rad(B_AXIS)
        Y20 = np.sqrt(5/(4*np.pi)) * (3*np.cos(ba)**2 - 1)/2
        
        for i, ell in enumerate(ells):
            s = 0.0
            for m in range(-ell, ell+1):
                # 🔧 ИСПРАВЛЕНИЕ: getidx требует (lmax, l, abs(m))
                idx = hp.Alm.getidx(LMAX, ell, abs(m))
                if idx < len(alm):
                    a = alm[idx]
                    # Учёт свойства сферических гармоник для отрицательных m
                    if m < 0:
                        a = ((-1)**abs(m)) * np.conj(a)
                    s += np.real(a * np.conj(a)) * Y20
            A_vals[i] = s / (2*ell + 1)
            
        A_vals /= w2  # поправка на потерю мощности
        
        print("📈 Загрузка спектра ΛCDM и конверсия A → g_*...")
        cl_data = np.loadtxt(CL_FILE)
        D_ell = np.interp(ells, cl_data[:,0], cl_data[:,1])
        C_ell_lcdm = D_ell * 2 * np.pi / (ells * (ells + 1))
        
        g_vals, wts = [], []
        for i, ell in enumerate(ells):
            w3j = float(wigner_3j(ell, ell, 2, 0, 0, 0))
            norm = np.sqrt(5/(4*np.pi)) * w3j
            if np.abs(norm) < 1e-15: continue
            g_l = A_vals[i] / (C_ell_lcdm[i] * norm)
            g_vals.append(g_l)
            wts.append(C_ell_lcdm[i]**2)
            
        g_star = np.average(g_vals, weights=wts) if g_vals else 0.0
        
        # Статистика
        g_obs, g_sig = 0.002, 0.016
        chi2_v = ((g_star - g_obs) / g_sig)**2
        p_v = 1 - chi2.cdf(chi2_v, df=1)
        status = "PASS" if abs(g_star) < G_THRESH else "FAIL"
        
        print(f"\n📊 РЕЗУЛЬТАТ BipoSH:")
        print(f"   g_*^model = {g_star:+.5f}")
        print(f"   g_*^obs   = {g_obs:.3f} ± {g_sig:.3f} (Kim & Komatsu 2013)")
        print(f"   χ² = {chi2_v:.3f}, p-value = {p_v:.4f}")
        print(f"   95% CL: |g_*| < {G_THRESH} ? {'✅ PASS' if status=='PASS' else '❌ FAIL'}")
        
        return {"g": g_star, "chi2": chi2_v, "p": p_v, "status": status}
        
    except Exception as e:
        import traceback
        print(f"❌ Ошибка в BipoSH: {e}")
        traceback.print_exc()
        return {"status": "ERROR"}

def run_cits():
    banner("📐 ТЕСТ 2: CITS (Геометрия)")
    print(f"📏 Параметры: L_min = {LX:.1f} Гпк, 2×χ_rec = {2*CHI_REC:.1f} Гпк")
    
    if LX >= 2 * CHI_REC:
        print("✅ Геометрия: Топология больше горизонта наблюдений.")
        print("   Сфера последнего рассеяния не пересекает саму себя.")
        print("   Парные окружности физически невозможны.")
        print("STATUS: PASS_GEOM")
        return {"status": "PASS_GEOM"}
    else:
        print("⚠️  Требуется поиск корреляций (не реализован в MVP)")
        return {"status": "SKIP"}

def save_report(b, c):
    rp = os.path.join(RESULTS_DIR, "report_final.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(rp, "w", encoding="utf-8") as f:
        f.write(f"# Отчёт валидации $\\mathbb{{IT}}^3$\n\n")
        f.write(f"**Дата**: {now}\n\n")
        f.write("## Результаты тестов\n\n")
        f.write("### BipoSH\n")
        if b.get("status") == "ERROR":
            f.write("❌ Ошибка выполнения\n")
        else:
            f.write(f"- $g_*^{{\\text{{model}}}} = {b.get('g', 'N/A'):+.5f}$\n")
            f.write(f"- $\\chi^2 = {b.get('chi2', 'N/A'):.3f}$, $p = {b.get('p', 'N/A'):.4f}$\n")
            f.write(f"- Статус: **{b.get('status')}**\n")
        f.write("\n### CITS\n")
        f.write(f"- Статус: **{c.get('status')}**\n")
        f.write(f"- Геометрическое пересечение: {'Да' if LX < 2*CHI_REC else 'Нет'}\n")
        f.write("\n## Сводка\n| Тест | Статус |\n|------|--------|\n")
        f.write(f"| BipoSH | {b.get('status')} |\n")
        f.write(f"| CITS   | {c.get('status')} |\n")
        f.write("\n## Воспроизводимость\n```bash\npython3 run_all_tests.py\n```\n")
    print(f"\n📄 Отчёт сохранён: {rp}")

def main():
    print("╔════════════════════════════════════════╗")
    print("║  FlatIrrationalTorus v1.1 — Валидация  ║")
    print("╚════════════════════════════════════════╝")
    
    missing = [f for f in [MAP_FILE, MASK_FILE, CL_FILE] if not os.path.exists(f)]
    if missing:
        print("\n❌ Отсутствуют файлы данных:")
        for name in missing: print(f"   - {os.path.basename(name)}")
        print("\n💡 Запустите: bash scripts/download_data.sh")
        sys.exit(1)
        
    print("\n✅ Все файлы данных найдены. Начинаю вычисления...\n")
    
    b = run_biposh()
    c = run_cits()
    save_report(b, c)
    
    banner("✅ ВАЛИДАЦИЯ ЗАВЕРШЕНА")
    print("📊 См. отчёт: results/report_final.md")

if __name__ == "__main__":
    main()
