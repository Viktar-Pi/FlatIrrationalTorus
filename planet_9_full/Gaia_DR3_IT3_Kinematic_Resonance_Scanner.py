#!/usr/bin/env python3
"""
Gaia DR3 IT3 Kinematic Resonance Scanner
---------------------------------------
Сканер макроскопических резонансных узлов (E-nodes) в кинематике
Млечного Пути. Использует базу данных ESA Gaia DR3 и инварианты 
парадигмы IT3.
"""

import requests
import pandas as pd
import io
import numpy as np

def run_gaia_it3_scan():
    print("="*70)
    print(" ИНИЦИАЛИЗАЦИЯ GAIA IT3 SCANNER (ESA TAP API) ")
    print("="*70)
    
    # URL для ESA Gaia TAP сервера
    gaia_tap_url = "https://gea.esac.esa.int/tap-server/tap/sync"
    
    # ADQL запрос к Gaia DR3
    # Фокус на локальной галактической окрестности (~500 пк) с высокой точностью параллакса
    adql_query = """
    SELECT TOP 5000 
        source_id, ra, dec, parallax, pmra, pmdec, radial_velocity, phot_g_mean_mag 
    FROM gaiadr3.gaia_source 
    WHERE parallax > 2.0 
      AND parallax_over_error > 10 
      AND pmra IS NOT NULL 
      AND pmdec IS NOT NULL 
      AND radial_velocity IS NOT NULL
    """
    
    params = {
        "REQUEST": "doQuery",
        "LANG": "ADQL",
        "FORMAT": "csv",
        "QUERY": adql_query
    }
    
    print("[*] Отправка ADQL запроса к архивам Gaia...")
    try:
        response = requests.get(gaia_tap_url, params=params, timeout=60)
        if response.status_code != 200:
            print(f"[-] Ошибка API Gaia: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"[-] Сетевая ошибка: {e}")
        return

    # Загрузка данных в pandas DataFrame
    df = pd.read_csv(io.StringIO(response.text))
    print(f"[+] Успешно загружено {len(df)} высокоточных звездных треков.\n")
    
    # Фундаментальная константа парадигмы IT3 (Квадрат инварианта продольного натяжения)
    Lambda1_sq = 101.911688
    
    # Расчет полного собственного движения (mas/yr)
    df['pm_total'] = np.sqrt(df['pmra']**2 + df['pmdec']**2)
    
    # Расчет поперечной скорости (v_T) в км/с: v_T = 4.74 * (pm / parallax)
    df['v_transverse_kms'] = 4.74 * df['pm_total'] / df['parallax']
    
    # Расчет расстояния в парсеках
    df['distance_pc'] = 1000.0 / df['parallax']
    
    # Поиск топологического резонанса
    # Кинематика квантуется гармониками инварианта Lambda1. 
    # Базовая резонансная скорость для локального узла:
    harmonic_base = Lambda1_sq / 2.0  # ~50.95 км/с
    tolerance = 2.5 # Окно допустимого геометрического отклонения (резонансный пояс)
    
    # Фильтрация E-nodes (звезды в кинематическом резонансе)
    df['Topological_Resonance'] = np.abs(df['v_transverse_kms'] - harmonic_base) < tolerance
    
    resonance_nodes = df[df['Topological_Resonance']].copy()
    resonance_nodes = resonance_nodes.sort_values(by='distance_pc')
    
    print("=== ТОП-15 КАНДИДАТОВ В КИНЕМАТИЧЕСКИЕ E-NODES (ГАЛАКТИЧЕСКИЙ РЕЗОНАНС IT3) ===")
    print(f"{'Source ID':<20} | {'Dist (pc)':<10} | {'v_trans (km/s)':<15} | {'Radial Vel':<12}")
    print("-" * 65)
    
    for _, row in resonance_nodes.head(15).iterrows():
        print(f"{row['source_id']:<20} | {row['distance_pc']:<10.2f} | {row['v_transverse_kms']:<15.2f} | {row['radial_velocity']:<12.2f}")
        
    # Сохранение результатов
    output_filename = "gaia_it3_resonance_nodes.csv"
    resonance_nodes.to_csv(output_filename, index=False)
    print(f"\n[+] Полный список галактических узлов сохранен в файл: {output_filename}")
    print("="*70)

if __name__ == "__main__":
    run_gaia_it3_scan()