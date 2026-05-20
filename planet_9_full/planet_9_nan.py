import pandas as pd
import numpy as np

def process_it3_targeted_mesh(input_file: str, output_file: str):
    print("Загрузка таргетных данных NOIRLab...")
    df = pd.read_csv(input_file)

    # 1. Глубокая фильтрация (Оставляем только глубокий космос с ошибкой кинематики)
    df['deltamjd'] = df['deltamjd'].fillna(0)
    
    # Ищем красные флаги пайплайна (ошибка > 90.0)
    error_mask = (df['pmraerr'] > 90.0) | (df['pmdecerr'] > 90.0)
    deep_space_mask = df['deltamjd'] > 30.0
    
    df_nan = df[error_mask & deep_space_mask].copy()
    print(f"Изолировано глубоководных структурных аномалий: {len(df_nan)}")

    if len(df_nan) == 0:
        print("В текущей выборке нет объектов, удовлетворяющих жестким критериям.")
        return

    # 2. 3D Проекция
    R_mid = 343.6
    ra_rad = np.radians(df_nan['ra'])
    dec_rad = np.radians(df_nan['dec'])

    df_nan['X'] = R_mid * np.cos(dec_rad) * np.cos(ra_rad)
    df_nan['Y'] = R_mid * np.cos(dec_rad) * np.sin(ra_rad)
    df_nan['Z'] = R_mid * np.sin(dec_rad)

    # 3. Валидация Резонанса (Кубооктаэдр)
    r_in = 243.0
    nodes = np.array([
        [r_in, r_in, 0], [r_in, -r_in, 0], [-r_in, r_in, 0], [-r_in, -r_in, 0],
        [r_in, 0, r_in], [r_in, 0, -r_in], [-r_in, 0, r_in], [-r_in, 0, -r_in],
        [0, r_in, r_in], [0, r_in, -r_in], [0, -r_in, r_in], [0, -r_in, -r_in]
    ])

    nodes_norm = nodes / np.linalg.norm(nodes, axis=1)[:, np.newaxis]
    obj_vectors = df_nan[['X', 'Y', 'Z']].values
    obj_norm = obj_vectors / np.linalg.norm(obj_vectors, axis=1)[:, np.newaxis]

    dot_products = np.dot(obj_norm, nodes_norm.T)
    dot_products = np.clip(dot_products, -1.0, 1.0)
    angles_deg = np.degrees(np.arccos(dot_products))

    df_nan['delta_theta'] = np.min(angles_deg, axis=1)

    # 4. Аналитика ближайших
    print("\n--- Аналитика ближайших кандидатов (Топ-5) ---")
    top_closest = df_nan.nsmallest(5, 'delta_theta')
    print(top_closest[['id', 'ra', 'dec', 'deltamjd', 'delta_theta', 'class_star']])

    # 5. Экспорт
    df_filtered = df_nan[df_nan['delta_theta'] < 3.0]
    print(f"\nОбъектов внутри 3-градусного окна резонанса (Δθ < 3.0°): {len(df_filtered)}")

    if len(df_filtered) > 0:
        output_cols = ['id', 'ra', 'dec', 'X', 'Y', 'Z', 'delta_theta', 'deltamjd', 'class_star']
        df_filtered[output_cols].to_csv(output_file, index=False)
        print(f"Матрица резонанса сохранена: {output_file}")

if __name__ == "__main__":
    process_it3_targeted_mesh('NOIRLab_12_Point.csv', 'IT3_Resonance_Hits.csv')