import pandas as pd
import numpy as np

def run_topological_mapping():
    print("[IT3] INITIALIZING GEOMETRIC CROSS-MATCH...")
    
    # 1. Загрузка сырых данных (сбойные треклеты из пайплайнов)
    input_file = 'IT3_Resonance_Hits.csv'
    try:
        df = pd.read_csv(input_file)
        print(f"[IT3] LOADED {len(df)} ANOMALIES FROM {input_file}")
    except FileNotFoundError:
        print(f"ERROR: {input_file} not found. Ensure the dataset is in the directory.")
        return

    # 2. Математическое ядро IT3: Координаты 12 E-узлов
    # r_in = 243.0 AU (касание внутренних граней куба)
    x = 243.0 
    
    # Топологические якоря (середины ребер вписанного гексаэдра)
    e_nodes = {
        'E1': np.array([x, x, 0]),
        'E2': np.array([x, -x, 0]),
        'E3': np.array([-x, x, 0]),
        'E4': np.array([-x, -x, 0]),
        'E5': np.array([x, 0, x]),
        'E6': np.array([x, 0, -x]),
        'E7': np.array([-x, 0, x]),
        'E8': np.array([-x, 0, -x]),
        'E9': np.array([0, x, x]),
        'E10': np.array([0, x, -x]),
        'E11': np.array([0, -x, x]),
        'E12': np.array([0, -x, -x])
    }

    # Нормализуем узловые векторы для расчета угловых отклонений
    e_nodes_norm = {name: vec / np.linalg.norm(vec) for name, vec in e_nodes.items()}

    # 3. Функция векторизации и привязки
    def anchor_to_node(row):
        # Извлекаем декартовы координаты объекта
        vec_obj = np.array([row['X'], row['Y'], row['Z']])
        norm_obj = np.linalg.norm(vec_obj)
        
        if norm_obj == 0: 
            return 'ORPHAN'
            
        vec_obj_norm = vec_obj / norm_obj
        
        best_node = None
        min_angle = float('inf')
        
        # Поиск минимального расхождения
        for node_name, n_vec in e_nodes_norm.items():
            dot_prod = np.clip(np.dot(vec_obj_norm, n_vec), -1.0, 1.0)
            angle = np.arccos(dot_prod) 
            
            if angle < min_angle:
                min_angle = angle
                best_node = node_name
                
        return best_node

    print("[IT3] EXECUTING TENSOR ALIGNMENT ON ALL VECTORS...")
    df['Target_E_Node'] = df.apply(anchor_to_node, axis=1)

    # 4. Вывод статистики резонансов
    print("\n[IT3] =================================")
    print("[IT3] MACROSCOPIC CONDENSATION RESULTS:")
    print("[IT3] =================================")
    distribution = df['Target_E_Node'].value_counts()
    print(distribution)
    
    # 5. Экспорт результатов
    output_file = 'IT3_Mapped_Nodes.csv'
    df.to_csv(output_file, index=False)
    print(f"\n[IT3] MAPPING COMPLETE. ENFORCEMENT DATA SAVED TO {output_file}")
    print("[IT3] AWAITING TELESCOPE DEPLOYMENT.")

if __name__ == "__main__":
    run_topological_mapping()