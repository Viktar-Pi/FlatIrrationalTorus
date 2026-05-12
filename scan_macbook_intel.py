import pandas as pd
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
import warnings
import ssl

# Отключаем проверку сертификатов и предупреждения
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings('ignore')

target_nodes = {
    "O-5 (Восточный Вектор)": (91.6926, 3.8861),
    "O-6 (Южный Вектор)": (271.6926, -3.8861),
    "E-5 (Нижний Предел)": (61.2420, -30.4501),
    "E-11 (Верхний Предел)": (182.1584, 6.8241),
    "E-2 (Западный Вектор)": (232.2511, -28.9347)
}

print("🌌 ПРОЕКТ IT3: ТЕПЛОВОЕ СКАНИРОВАНИЕ ГЛУБОКОГО КОСМОСА")
print("🎯 ПОИСК БИНАРНОГО КОМПАНЬОНА НА ОРБИТЕ ~2453 AU")
print("="*70)

# Используем '**', чтобы принудительно выкачать все колонки базы данных
v = Vizier(catalog="II/365/catwise", columns=['**'])
v.ROW_LIMIT = 50000 
search_radius = 3.0 # Расширяем зону захвата до 3 градусов

for name, (ra, dec) in target_nodes.items():
    print(f"\n📡 Сканирование вектора {name} [RA: {ra:.2f}, Dec: {dec:.2f}]...")
    coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='icrs')
    
    try:
        result = v.query_region(coord, radius=search_radius * u.deg)
        
        if len(result) > 0:
            df = result[0].to_pandas()
            
            # Умный поиск нужных колонок (обход ошибок API VizieR)
            w1_col = next((c for c in df.columns if 'W1' in c and ('mpro' in c.lower() or 'mag' in c.lower())), None)
            w2_col = next((c for c in df.columns if 'W2' in c and ('mpro' in c.lower() or 'mag' in c.lower())), None)
            pmra_col = next((c for c in df.columns if 'pmRA' in c or 'pmra' in c.lower()), None)
            pmde_col = next((c for c in df.columns if 'pmDE' in c or 'pmdec' in c.lower()), None)
            
            if w1_col and w2_col and pmra_col and pmde_col:
                # Конвертируем данные в числа
                df[w1_col] = pd.to_numeric(df[w1_col], errors='coerce')
                df[w2_col] = pd.to_numeric(df[w2_col], errors='coerce')
                df[pmra_col] = pd.to_numeric(df[pmra_col], errors='coerce')
                df[pmde_col] = pd.to_numeric(df[pmde_col], errors='coerce')
                
                # Вычисляем индекс цвета и суммарное движение
                df['color_index'] = df[w1_col] - df[w2_col]
                df['pm_total'] = (df[pmra_col]**2 + df[pmde_col]**2)**0.5
                
                # ФИЛЬТР: Ультрахолодные (W1-W2 > 0.8) и аномально подвижные (> 100 mas/yr)
                candidates = df[(df['color_index'] >= 0.8) & (df['pm_total'] >= 100)]
                
                if not candidates.empty:
                    print(f"  ⚠️ НАЙДЕНО КАНДИДАТОВ СУБЗВЕЗДНОЙ МАССЫ: {len(candidates)}")
                    # Выводим Топ-5 самых холодных (вероятных) кандидатов
                    candidates = candidates.sort_values(by='color_index', ascending=False).head(5)
                    
                    for _, row in candidates.iterrows():
                        # Декодируем байтовое имя, если оно есть
                        obj_name = row['Name'] if 'Name' in df.columns else "CatWISE_Obj"
                        if isinstance(obj_name, bytes): obj_name = obj_name.decode('utf-8')
                            
                        print(f"     ID: {obj_name}")
                        print(f"     Цвет (W1-W2): {row['color_index']:.2f} (Сверххолодный)")
                        print(f"     Кинематика: {row['pm_total']:.1f} mas/yr")
                        print("     - - -")
                else:
                    print("  Кандидаты не найдены (объекты либо статичны, либо слишком горячие).")
            else:
                print(f"  Ошибка: сервер не вернул нужные метрики. Доступны: {list(df.columns)}")
        else:
            print("  В этом секторе нет инфракрасных данных.")
            
    except Exception as e:
        print(f"  Системная ошибка: {e}")

print("\n" + "="*70)
print("🏁 СКАНИРОВАНИЕ ЗАВЕРШЕНО.")