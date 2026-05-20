import pyvo as vo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import sys

C_CYAN = '\033[96m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_RESET = '\033[0m'

def log(msg, level="INFO"):
    ts = time.strftime("%H:%M:%S")
    color = {"INFO": C_CYAN, "EXEC": C_YELLOW, "DATA": C_GREEN, "ERR": C_RED}.get(level, C_CYAN)
    print(f"{color}[{ts}] [{level}] {msg}{C_RESET}")

log("Инициализация TAP. Режим: КИНЕМАТИКА ПО АНОМАЛИЯМ (v2.2 + ПАСПОРТ)...")
service = vo.dal.TAPService("https://datalab.noirlab.edu/tap")

sectors = [
    {"name": "E1", "cond": "ra BETWEEN 42.0 AND 48.0 AND dec BETWEEN -3.0 AND 3.0"},
    {"name": "E2", "cond": "ra BETWEEN 132.0 AND 138.0 AND dec BETWEEN -3.0 AND 3.0"},
    {"name": "E3", "cond": "ra BETWEEN 222.0 AND 228.0 AND dec BETWEEN -3.0 AND 3.0"},
    {"name": "E4", "cond": "ra BETWEEN 312.0 AND 318.0 AND dec BETWEEN -3.0 AND 3.0"},
    {"name": "E5", "cond": "(ra BETWEEN 357.0 AND 360.0 OR ra BETWEEN 0.0 AND 3.0) AND dec BETWEEN 42.0 AND 48.0"},
    {"name": "E6", "cond": "ra BETWEEN 87.0 AND 93.0 AND dec BETWEEN 42.0 AND 48.0"},
    {"name": "E7", "cond": "ra BETWEEN 177.0 AND 183.0 AND dec BETWEEN 42.0 AND 48.0"},
    {"name": "E8", "cond": "ra BETWEEN 267.0 AND 273.0 AND dec BETWEEN 42.0 AND 48.0"},
    {"name": "E9", "cond": "(ra BETWEEN 357.0 AND 360.0 OR ra BETWEEN 0.0 AND 3.0) AND dec BETWEEN -48.0 AND -42.0"},
    {"name": "E10", "cond": "ra BETWEEN 87.0 AND 93.0 AND dec BETWEEN -48.0 AND -42.0"},
    {"name": "E11", "cond": "ra BETWEEN 177.0 AND 183.0 AND dec BETWEEN -48.0 AND -42.0"},
    {"name": "E12", "cond": "ra BETWEEN 267.0 AND 273.0 AND dec BETWEEN -48.0 AND -42.0"}
]

all_data = []
log("Сбор сырой кинематики сломанных треклетов...", "EXEC")

for i, sector in enumerate(sectors):
    sys.stdout.write(f"\r{C_CYAN}[EXEC] СКАНИРОВАНИЕ {i+1}/12: Сектор {sector['name']}...{C_RESET}")
    sys.stdout.flush()
    
    # ВНИМАНИЕ: Добавлен 'id' в SELECT
    adql_query = f"""
    SELECT TOP 1000 id, ra, dec, pmra, pmdec, pmraerr, pmdecerr 
    FROM nsc_dr2.object 
    WHERE ({sector['cond']}) 
    AND (pmraerr > 90.0 OR pmdecerr > 90.0 OR ABS(pmra) > 10000)
    AND pmra IS NOT NULL AND pmdec IS NOT NULL
    AND deltamjd > 30.0 
    AND ndet >= 3
    """
    
    try:
        job = service.submit_job(adql_query)
        job.run()
        while job.phase not in ("COMPLETED", "ERROR", "ABORTED"):
            time.sleep(0.5)
            
        if job.phase == "COMPLETED":
            df_chunk = job.fetch_result().to_table().to_pandas()
            all_data.append(df_chunk)
    except Exception as e:
        pass
    time.sleep(1)

print()
df = pd.concat(all_data, ignore_index=True)
log(f"Загружено {len(df)} кинематических векторов аномалий.", "DATA")

# ==========================================
# ФИЗИЧЕСКОЕ ЯДРО: РАСЧЕТ ИСТИННОЙ ДИСТАНЦИИ
# ==========================================
log("Обработка обратной Кеплеровской задачи...", "EXEC")

df['mu_total_arcsec'] = np.sqrt(df['pmra']**2 + df['pmdec']**2) / 1000.0
df = df[df['mu_total_arcsec'] > 0.01] 
KEPLER_CONSTANT = 1_296_000
df['D_calc'] = (KEPLER_CONSTANT / df['mu_total_arcsec'])**(2/3)

df = df[(df['D_calc'] > 150) & (df['D_calc'] < 600)]
df['R_true'] = df['D_calc']

log(f"После кинематического фильтра (150 - 600 AU) осталось кандидатов: {len(df)}", "DATA")

# ==========================================
# ВЫВОД ГИСТОГРАММЫ В КОНСОЛЬ
# ==========================================
log("Анализ плотности резонансов (Гистограмма R_true):", "INFO")
counts, edges = np.histogram(df['R_true'], bins=20, range=(150, 600))
max_c = max(counts) if max(counts) > 0 else 1

for c, e_start, e_end in zip(counts, edges[:-1], edges[1:]):
    bar = '█' * int(40 * c / max_c)
    if 330 <= e_start <= 360:
        print(f"{e_start:6.1f} - {e_end:6.1f} AU | {c:5d} | {C_YELLOW}{bar} < E-NODE ZONE{C_RESET}")
    elif 400 <= e_start <= 430:
        print(f"{e_start:6.1f} - {e_end:6.1f} AU | {c:5d} | {C_CYAN}{bar} < SHELL ZONE{C_RESET}")
    else:
        print(f"{e_start:6.1f} - {e_end:6.1f} AU | {c:5d} | {C_RED}{bar}{C_RESET}")

stat_e_node = len(df[(df['R_true'] >= 330) & (df['R_true'] <= 360)])
stat_shell = len(df[(df['R_true'] >= 400) & (df['R_true'] <= 430)])

print(f"\n[СТАТИСТИКА КЛАСТЕРИЗАЦИИ]")
print(f"Точек в зоне E-nodes (~343.6 AU): {stat_e_node}")
print(f"Точек в зоне Скорлупы (~420.9 AU): {stat_shell}")

# ==========================================
# ПАСПОРТ КАНДИДАТА IT3 (ИЗВЛЕЧЕНИЕ ДАННЫХ)
# ==========================================
if len(df) > 0:
    print("\n" + "="*55)
    print(f"{C_GREEN}[ ОБНАРУЖЕН КИНЕМАТИЧЕСКИЙ УЗЕЛ IT3 ]{C_RESET}")
    print("="*55)
    
    for index, row in df.iterrows():
        print(f"ID объекта (NSC DR2):    {C_YELLOW}{int(row['id'])}{C_RESET}")
        print(f"Прямое восхождение (RA): {C_CYAN}{row['ra']:.6f}°{C_RESET}")
        print(f"Склонение (Dec):         {C_CYAN}{row['dec']:.6f}°{C_RESET}")
        print("-" * 55)
        print(f"Собственное движение RA: {row['pmra']:.2f} mas/yr")
        print(f"Собственное движение Dec:{row['pmdec']:.2f} mas/yr")
        print(f"Общий вектор скорости:   {row['mu_total_arcsec']:.5f} arcsec/yr")
        print("-" * 55)
        print(f"Расчетный радиус R_true: {C_GREEN}{row['R_true']:.2f} AU{C_RESET}")
        print("="*55)
        print("\n[Анализ позиционирования]")
        print("Сравни эти координаты RA/Dec с твоей теоретической матрицей.")
        print("Это физический кандидат для кросс-матчинга с архивами ESA/Gaia.")
else:
    log("Кандидат потерян при фильтрации. Пусто.", "ERR")

# ==========================================
# ДИНАМИЧЕСКИЙ РЕНДЕРИНГ 3D
# ==========================================
if len(df) > 0:
    ra_rad = np.radians(df['ra'])
    dec_rad = np.radians(df['dec'])
    df['x'] = df['R_true'] * np.cos(dec_rad) * np.cos(ra_rad)
    df['y'] = df['R_true'] * np.cos(dec_rad) * np.sin(ra_rad)
    df['z'] = df['R_true'] * np.sin(dec_rad)

R_OUT = 420.9  
R_IN = 243.0   
vertices = np.array([
    [R_IN, R_IN, R_IN], [R_IN, R_IN, -R_IN], [R_IN, -R_IN, R_IN], [R_IN, -R_IN, -R_IN],
    [-R_IN, R_IN, R_IN], [-R_IN, R_IN, -R_IN], [-R_IN, -R_IN, R_IN], [-R_IN, -R_IN, -R_IN]
])
edges_list = [(0,1), (0,2), (0,4), (1,3), (1,5), (2,3), (2,6), (3,7), (4,5), (4,6), (5,7), (6,7)]

plt.style.use('dark_background')
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0a0a1a')
fig.patch.set_facecolor('#0a0a1a')

# Каркас
for edge in edges_list:
    pt1 = vertices[edge[0]]
    pt2 = vertices[edge[1]]
    ax.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]], [pt1[2], pt2[2]], color='#00ffcc', linewidth=1.5, alpha=0.5)
ax.scatter(vertices[:,0], vertices[:,1], vertices[:,2], color='#00ffcc', s=80, label='Restored Topology', zorder=5)

# Динамические аномалии
if len(df) > 0:
    ax.scatter(df['x'], df['y'], df['z'], color='#ff0055', s=15, alpha=0.8, label=f'Kinematic Entities (n={len(df)})')

max_range = R_OUT * 1.2
ax.set_xlim([-max_range, max_range])
ax.set_ylim([-max_range, max_range])
ax.set_zlim([-max_range, max_range])
ax.axis('off')

plt.title('IT3 Dynamic Verification: Kinematic Radius vs Lattice', color='#ffffff', pad=20)
plt.legend(loc='upper right', facecolor='#000000', edgecolor='#00ffcc')

log("График построен. Ожидание завершения...", "INFO")
plt.tight_layout()
plt.show()