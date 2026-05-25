"""
IT3 Framework: Interstellar Kinematic Pressure & Gravitational Focusing
Description: Calculates asymptotic velocities (v_inf) and orbital energies
of comets to map the aerodynamic flow of the Solar System.
"""

import numpy as np
import pandas as pd
import requests
import warnings
import matplotlib.pyplot as plt
from astropy.utils.exceptions import AstropyWarning
from astropy.coordinates import SkyCoord, BarycentricTrueEcliptic, ICRS

warnings.simplefilter('ignore', category=AstropyWarning)

def get_it3_nodes_matrix():
    e_nodes_icrs = {
        "E-1": (128.7948, -22.8280), "E-2": (232.2511, -28.9347),
        "E-3": (52.2511, 28.9347),   "E-4": (308.7948, 22.8280),
        "E-5": (61.2420, -30.4501),  "E-6": (304.8865, -37.0587),
        "E-7": (124.8865, 37.0587),  "E-8": (241.2420, 30.4501),
        "E-9": (357.1350, -47.8740), "E-10": (177.1350, 47.8740),
        "E-11": (182.1584, 6.8241),  "E-12": (2.1584, -6.8241)
    }
    names = list(e_nodes_icrs.keys())
    matrix = []
    for name in names:
        ra, dec = np.radians(e_nodes_icrs[name][0]), np.radians(e_nodes_icrs[name][1])
        matrix.append([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
    return names, np.array(matrix)

def fetch_comet_data():
    print("⏳ [IT3] Загрузка данных NASA JPL SBDB...")
    url = "https://ssd-api.jpl.nasa.gov/sbdb_query.api"
    query_params = {
        'fields': 'full_name,e,a,q,ad,i,om,w',
        'sb-kind': 'c',
        'full-prec': 'true'
    }
    try:
        response = requests.get(url, params=query_params)
        data = response.json()
        df = pd.DataFrame(data['data'], columns=data['fields'])
        for col in ['e', 'a', 'q', 'ad', 'i', 'om', 'w']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # Берем только кометы дальнего космоса
        df = df[(df['e'] > 0.9) & (df['q'] > 1.5)]
        return df.dropna(subset=['e', 'q', 'i', 'om', 'w']).reset_index(drop=True)
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        return pd.DataFrame()

def analyze_kinematics():
    df = fetch_comet_data()
    if df.empty: return
    
    # 1. Расчет инварианта 1/a и Асимптотической скорости (v_inf)
    # 1/a = (1 - e) / q
    df['inv_a'] = (1.0 - df['e']) / df['q']
    
    # Скорость на бесконечности v_inf = 29.78 * sqrt(|1/a|) для e > 1
    # 29.78 км/с - скорость Земли (масштабный коэффициент для GM_sun)
    df['v_inf_kms'] = np.where(df['e'] > 1.0, 29.78 * np.sqrt(np.abs(df['inv_a'])), 0.0)
    
    # 2. Векторный анализ IT3
    om, w, i = np.radians(df['om'].values), np.radians(df['w'].values), np.radians(df['i'].values)
    Ax = -(np.cos(om)*np.cos(w) - np.sin(om)*np.sin(w)*np.cos(i))
    Ay = -(np.sin(om)*np.cos(w) + np.cos(om)*np.sin(w)*np.cos(i))
    Az = -(np.sin(w)*np.sin(i))
    
    coord_ecl = SkyCoord(x=Ax, y=Ay, z=Az, representation_type='cartesian', frame=BarycentricTrueEcliptic)
    coord_eq = coord_ecl.transform_to(ICRS())
    
    comet_vectors = np.vstack([coord_eq.cartesian.x.value, coord_eq.cartesian.y.value, coord_eq.cartesian.z.value]).T
    comet_vectors /= np.linalg.norm(comet_vectors, axis=1, keepdims=True)
    
    node_names, node_matrix = get_it3_nodes_matrix()
    angles_matrix = np.degrees(np.arccos(np.clip(np.dot(comet_vectors, node_matrix.T), -1.0, 1.0)))
    
    df['Best_Node'] = [node_names[idx] for idx in np.argmin(angles_matrix, axis=1)]
    df['Delta_Theta'] = np.min(angles_matrix, axis=1)
    
    # Изолируем только кометы, захваченные узлами (Delta_Theta < 12.0)
    anchored = df[df['Delta_Theta'] <= 12.0].copy()
    
    # 3. Агрегация кинематики по узлам
    stats = anchored.groupby('Best_Node').agg(
        Total_Comets=('full_name', 'count'),
        Hyperbolic_Count=('e', lambda x: (x > 1.0).sum()),
        Avg_Eccentricity=('e', 'mean'),
        Max_V_inf=('v_inf_kms', 'max'),
        Mean_Kinetic_Tension=('inv_a', lambda x: np.mean(np.abs(x)) * 1000) # Прокси для энергии
    ).reset_index()
    
    print("\n==========================================================================")
    print(" [IT3] ИНТЕРСТЕЛЛЯРНАЯ КИНЕМАТИКА И ГРАВИТАЦИОННОЕ ЛИНЗИРОВАНИЕ ХВОСТА")
    print("==========================================================================")
    print(stats.sort_values('Total_Comets', ascending=False).to_string(index=False))
    
    # 4. Построение графика
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Сортируем для красоты
    stats = stats.sort_values('Total_Comets', ascending=False)
    
    bars = ax1.bar(stats['Best_Node'], stats['Total_Comets'], color='cyan', alpha=0.7, label='Total Comets Anchored')
    ax1.set_ylabel('Number of Comets', color='cyan', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='cyan')
    
    # Накладываем линию Кинетического Напряжения (Энергии)
    ax2 = ax1.twinx()
    line = ax2.plot(stats['Best_Node'], stats['Mean_Kinetic_Tension'], color='red', marker='o', 
                    linewidth=2, markersize=8, label='Kinetic Energy Proxy (|1/a| * 1e3)')
    ax2.set_ylabel('Orbital Kinetic Tension', color='red', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='red')
    
    plt.title('IT3 Node Kinematic Stress: Heliotail Gravitational Focusing (E-5 / E-6)', fontsize=14, pad=15)
    
    # Добавляем легенду
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')
    
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig('IT3_Kinematic_Stress.png', dpi=300)
    print("\n✔️ График успешно сохранен как 'IT3_Kinematic_Stress.png'")
    plt.show()

if __name__ == "__main__":
    analyze_kinematics()