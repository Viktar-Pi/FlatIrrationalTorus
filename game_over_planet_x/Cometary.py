import numpy as np
import pandas as pd
import requests
import warnings
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
    print("⏳ [IT3] Запрашиваем данные комет (JPL SBDB API)...")
    url = "https://ssd-api.jpl.nasa.gov/sbdb_query.api"
    
    # СТАБИЛЬНЫЙ СИНТАКСИС: используем базовую фильтрацию, которая точно пропускается сервером
    query_params = {
        'fields': 'full_name,e,a,q,ad,i,om,w',
        'sb-kind': 'c',
        'full-prec': 'true'
    }
    
    try:
        response = requests.get(url, params=query_params)
        
        # Если NASA возвращает ошибку (например, 400 или 502), мы перехватим её здесь
        if response.status_code != 200:
            print(f"❌ [IT3] Сервер вернул статус-код: {response.status_code}")
            print(f"Ответ сервера: {response.text[:200]}")
            return pd.DataFrame()
            
        data = response.json()
        if 'data' not in data: 
            print("❌ [IT3] API вернул пустой контейнер данных.")
            return pd.DataFrame()
            
        df = pd.DataFrame(data['data'], columns=data['fields'])
        
        # Приведение типов данных
        for col in ['e', 'a', 'q', 'ad', 'i', 'om', 'w']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Отрезаем кометы, не проходящие по вашему базовому условию e > 0.9 и q > 1.5 на уровне Pandas
        df = df[(df['e'] > 0.9) & (df['q'] > 1.5)]
        
        return df.dropna(subset=['e', 'i', 'om', 'w']).reset_index(drop=True)
        
    except Exception as e:
        print(f"❌ Системная ошибка при обработке запроса: {e}")
        return pd.DataFrame()

def analyze_vectorized():
    df = fetch_comet_data()
    if df.empty: 
        print("❌ Данные пусты. Анализ невозможен.")
        return
    
    print(f"✔️ [IT3] Успешно загружено и отфильтровано комет: {len(df)}")
    print("⏳ [IT3] Векторизованный тензорный анализ...")
    
    om, w, i = np.radians(df['om'].values), np.radians(df['w'].values), np.radians(df['i'].values)
    
    # Векторы афелия в эклиптике J2000
    Ax = -(np.cos(om)*np.cos(w) - np.sin(om)*np.sin(w)*np.cos(i))
    Ay = -(np.sin(om)*np.cos(w) + np.cos(om)*np.sin(w)*np.cos(i))
    Az = -(np.sin(w)*np.sin(i))
    
    # Трансформация декартовых векторов в ICRS (экваториал)
    coord_ecl = SkyCoord(x=Ax, y=Ay, z=Az, representation_type='cartesian', frame=BarycentricTrueEcliptic)
    coord_eq = coord_ecl.transform_to(ICRS())
    
    # Единичные экваториальные векторы комет (Матрица N x 3)
    comet_vectors = np.vstack([coord_eq.cartesian.x.value, coord_eq.cartesian.y.value, coord_eq.cartesian.z.value]).T
    comet_vectors /= np.linalg.norm(comet_vectors, axis=1, keepdims=True)
    
    # Матрица узлов (12 x 3)
    node_names, node_matrix = get_it3_nodes_matrix()
    
    # Матричное умножение (N x 12) — вычисляет углы мгновенно для всей базы данных
    dot_products = np.dot(comet_vectors, node_matrix.T)
    dot_products = np.clip(dot_products, -1.0, 1.0)
    angles_matrix = np.degrees(np.arccos(dot_products))
    
    best_node_indices = np.argmin(angles_matrix, axis=1)
    min_angles = np.min(angles_matrix, axis=1)
    best_node_names = [node_names[idx] for idx in best_node_indices]
    
    # Обработка радиальных зон с учетом параболических траекторий (e >= 1.0 или NaN в афелии)
    q_vals = df['ad'].values
    e_vals = df['e'].values
    radial_zones = []
    
    for Q, ecc in zip(q_vals, e_vals):
        if pd.isna(Q) or ecc >= 1.0: 
            radial_zones.append("Parabolic / Open Trajectory")
        elif abs(Q - 243.0) / 243.0 < 0.15: radial_zones.append("Inner Sphere (r_in ~243 AU)")
        elif abs(Q - 343.6) / 343.6 < 0.15: radial_zones.append("E-Node Tension (R_mid ~343 AU)")
        elif abs(Q - 420.9) / 420.9 < 0.15: radial_zones.append("Outer Shell (R_out ~420 AU)")
        elif abs(Q - 2453.1) / 2453.1 < 0.20: radial_zones.append("Terminal Anchor (R_deep ~2453 AU)")
        elif Q > 5000: radial_zones.append("Deep Space Oort (> 5000 AU)")
        else: radial_zones.append("Transitional Scattering Zone")
        
    df_res = pd.DataFrame({
        'Object': df['full_name'], 'Q (AU)': df['ad'], 'Eccentricity': df['e'],
        'Best_Node': best_node_names, 'Delta_Theta (deg)': min_angles, 'Radial_Zone': radial_zones
    })
    
    tolerance = 12.0
    anchored = df_res[df_res['Delta_Theta (deg)'] <= tolerance]
    
    print("\n=======================================================")
    print(" [IT3] OPTIMIZED VECTORIZED SCANNER RESULTS ")
    print("=======================================================")
    print(f"Всего комет: {len(df_res)}")
    print(f"Захвачено узлами IT3 (Δθ <= {tolerance}°): {len(anchored)} ({len(anchored)/len(df_res)*100:.1f}%)")
    
    print("\nРаспределение по скорректированным зонам мембран:")
    print(df_res['Radial_Zone'].value_counts())
    
    print("\nПлотность распределения попаданий по конкретным узлам решетки:")
    print(anchored['Best_Node'].value_counts().sort_index().to_string())
    
    print(f"\nТоп-15 самых точных топологических привязок:")
    print(anchored.sort_values('Delta_Theta (deg)').head(15).to_string(index=False))

if __name__ == "__main__":
    analyze_vectorized()
