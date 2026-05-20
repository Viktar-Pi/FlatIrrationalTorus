import pandas as pd
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u

target_nodes = {
    "O-5 (Восточный Вектор)": (91.6926, 3.8861),
    "O-6 (Южный Вектор)": (271.6926, -3.8861),
    "E-5 (Нижний Предел)": (61.2420, -30.4501),
    "E-11 (Верхний Предел)": (182.1584, 6.8241),
    "E-2 (Западный Вектор)": (232.2511, -28.9347)
}

print("🌌 ПРОЕКТ IT3: ТЕПЛОВОЕ СКАНИРОВАНИЕ ГЛУБОКОГО КОСМОСА (CatWISE2020)")
print("🎯 Ограничение на наличие барионных компаньонов (Y/T карликов)")
print("="*75)

# Мы ТОЧНО знаем схему из ответа сервера, запрашиваем только нужное для скорости
exact_columns = ['Name', 'RA_ICRS', 'DE_ICRS', 'pmRA', 'pmDE', 'W1mproPM', 'W2mproPM', 'snrW1pm', 'snrW2pm']

v = Vizier(catalog="II/365/catwise", columns=exact_columns)
v.ROW_LIMIT = 50000 
search_radius = 2.0 

for name, (ra, dec) in target_nodes.items():
    print(f"\n📡 Сканирование вектора {name} [RA: {ra:.2f}, Dec: {dec:.2f}] (r={search_radius}°)...")
    coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='icrs')
    
    try:
        result = v.query_region(coord, radius=search_radius * u.deg)
        
        if len(result) > 0:
            df = result[0].to_pandas()
            
            # Конвертируем в числа (защита от мусора в базе)
            for col in ['W1mproPM', 'W2mproPM', 'pmRA', 'pmDE', 'snrW1pm', 'snrW2pm']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
            df['color_index'] = df['W1mproPM'] - df['W2mproPM']
            df['pm_total'] = (df['pmRA']**2 + df['pmDE']**2)**0.5
            
            # СТРОГИЕ ФИЛЬТРЫ ИЗ СТАТЬИ
            candidates = df[
                (df['color_index'] >= 0.8) & 
                (df['pm_total'] >= 100.0) &
                (df['snrW1pm'] > 5.0) &
                (df['snrW2pm'] > 5.0)
            ]
            
            if not candidates.empty:
                print(f"  ⚠️ НАЙДЕНО ИСТОЧНИКОВ, УДОВЛЕТВОРЯЮЩИХ КРИТЕРИЯМ: {len(candidates)}")
                candidates = candidates.sort_values(by='color_index', ascending=False).head(5)
                
                for _, row in candidates.iterrows():
                    obj_name = row['Name'] if 'Name' in df.columns else "CatWISE_Obj"
                    if isinstance(obj_name, bytes): obj_name = obj_name.decode('utf-8')
                        
                    print(f"     ID: {obj_name}")
                    print(f"     Цвет (W1-W2): {row['color_index']:.2f} | SNR: W1={row['snrW1pm']:.1f}, W2={row['snrW2pm']:.1f}")
                    print(f"     Кинематика: {row['pm_total']:.1f} mas/yr")
                    print("     - - -")
            else:
                print("  ✅ Null Result: Кандидаты, удовлетворяющие жестким критериям, не найдены.")
        else:
            print("  ✅ Null Result: В этом секторе нет инфракрасных источников.")
            
    except Exception as e:
        print(f"  ❌ Системная ошибка при запросе к VizieR: {e}")

print("\n" + "="*75)
print("🏁 СКАНИРОВАНИЕ ЗАВЕРШЕНО.")