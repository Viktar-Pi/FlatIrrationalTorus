"""
IT3 Framework: ETNO Topological Anchoring
Description: Retrieves extreme trans-Neptunian objects from the NASA JPL SBDB 
and calculates their 3D alignment with the IT3 spatial nodes.
"""

import numpy as np
import pandas as pd
import requests
import warnings
import ssl
from astropy.coordinates import SkyCoord, BarycentricTrueEcliptic
import astropy.units as u

# Обход проверки SSL для совместимости локальных сертификатов при запросах к API NASA
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings('ignore')

# Координаты 12 E-узлов (ICRS)
e_nodes_icrs = {
    "E-1": (128.7948, -22.8280), "E-2": (232.2511, -28.9347),
    "E-3": (52.2511, 28.9347),   "E-4": (308.7948, 22.8280),
    "E-5": (61.2420, -30.4501),  "E-6": (304.8865, -37.0587),
    "E-7": (124.8865, 37.0587),  "E-8": (241.2420, 30.4501),
    "E-9": (152.2254, -82.1378), "E-10": (2.1584, -6.8241),
    "E-11": (182.1584, 6.8241),  "E-12": (332.2254, 82.1378)
}

print("🌌 ПРОЕКТ IT3: ПОИСК ГРАВИТАЦИОННОГО ЗАХВАТА ETNO (NASA JPL DATA)")
print("="*65)

# Резервная БД на случай таймаута API или отсутствия интернета
fallback_etnos = [
    {"full_name": "90377 Sedna", "a": 484.0, "e": 0.84, "i": 11.9, "om": 144.5, "w": 311.5},
    {"full_name": "2012 VP113 (Biden)", "a": 261.0, "e": 0.69, "i": 24.1, "om": 90.3, "w": 294.0},
    {"full_name": "541132 Leleakuhonua", "a": 1094.0, "e": 0.94, "i": 11.6, "om": 300.9, "w": 118.0},
    {"full_name": "2014 SR349", "a": 296.0, "e": 0.84, "i": 18.0, "om": 34.6, "w": 341.2},
    {"full_name": "2013 SY99", "a": 732.0, "e": 0.93, "i": 4.2, "om": 29.5, "w": 32.4},
    {"full_name": "2010 GB174", "a": 361.0, "e": 0.86, "i": 21.5, "om": 130.6, "w": 347.8},
    {"full_name": "2004 VN112", "a": 318.0, "e": 0.85, "i": 25.5, "om": 66.0, "w": 327.1},
    {"full_name": "148209 (2000 CR105)", "a": 226.0, "e": 0.80, "i": 22.7, "om": 128.2, "w": 317.2},
    {"full_name": "474640 Alicanto", "a": 328.0, "e": 0.86, "i": 25.5, "om": 66.0, "w": 327.2}
]

df = None
try:
    print("📡 Подключение к NASA JPL SBDB...")
    url = "https://ssd-api.jpl.nasa.gov/sbdb_query.api"
    # Запрос объектов с большой полуосью > 100 AU и перигелием > 30 AU
    params = {"fields": "full_name,a,e,i,om,w", "sb-cdata": '{"AND":["a|GT|100","q|GT|30"]}'}
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'data' in data:
        df = pd.DataFrame(data['data'], columns=data['fields'])
        for col in ['a', 'e', 'i', 'om', 'w']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        print("✅ Реальные данные успешно загружены из базы NASA.")
    else:
        raise ValueError("No data array in JSON response")
except Exception as e:
    print(f"⚠️ Ошибка API ({e}). Использование резервной offline-базы...")
    df = pd.DataFrame(fallback_etnos)

df = df.dropna()
df['aphelion'] = df['a'] * (1 + df['e'])
# Фильтрация объектов с афелием дальше 150 AU
etnos = df[df['aphelion'] > 150]

print(f"\n⏳ Расчет 3D-векторов афелия для {len(etnos)} объектов ETNO...")
results = []

for idx, obj in etnos.iterrows():
    om = np.radians(obj['om'])
    w = np.radians(obj['w'])
    i = np.radians(obj['i'])
    
    # Строгий 3D-Вектор перигелия (в эклиптике) и афелия (-P)
    Px = np.cos(om)*np.cos(w) - np.sin(om)*np.sin(w)*np.cos(i)
    Py = np.sin(om)*np.cos(w) + np.cos(om)*np.sin(w)*np.cos(i)
    Pz = np.sin(w)*np.sin(i)
    Ax, Ay, Az = -Px, -Py, -Pz
    
    lon = np.degrees(np.arctan2(Ay, Ax))
    lat = np.degrees(np.arcsin(Az))
    
    # Трансформация координат афелия в экваториальную систему (ICRS)
    coord_eq = SkyCoord(lon=lon*u.deg, lat=lat*u.deg, frame=BarycentricTrueEcliptic).transform_to('icrs')
    
    # Сверка с координатами E-узлов
    for node_name, (n_ra, n_dec) in e_nodes_icrs.items():
        sep = coord_eq.separation(SkyCoord(ra=n_ra*u.deg, dec=n_dec*u.deg, frame='icrs')).degree
        if sep < 20.0: # Порог захвата в 20 градусов
            results.append({
                "Объект": str(obj['full_name']).strip(),
                "Узел": node_name,
                "Отклонение (°)": round(sep, 2),
                "Афелий (AU)": round(obj['aphelion'], 1)
            })

if results:
    res_df = pd.DataFrame(results).sort_values('Отклонение (°)')
    print("\n🎯 ОБНАРУЖЕНЫ ТОПОЛОГИЧЕСКИЕ ЯКОРЯ (Захват E-узлами):")
    print(res_df.to_string(index=False))
else:
    print("\n🧐 В радиусе 20° совпадений не найдено.")

print("\n" + "="*65)