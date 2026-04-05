#!/usr/bin/env python3
"""
CITS-тест (Circles in the Sky) модели IT³ — ЗАЩИЩЕННАЯ ВЕРСИЯ
Извлекает строго упорядоченные 1D-профили колец на сфере и ищет их корреляцию.
"""
import numpy as np
import healpy as hp
from scipy.stats import pearsonr
import sys, os

def extract_ring_profile(map_T, mask, center_theta, center_phi, radius_deg, n_points=720):
    """Извлекает упорядоченный 1D-профиль вдоль окружности на сфере."""
    radius_rad = np.deg2rad(radius_deg)
    center_vec = hp.ang2vec(center_theta, center_phi)
    
    # Создаем локальную декартовую систему координат вокруг центра окружности
    vec_z = center_vec
    if abs(vec_z[2]) < 0.99:
        vec_x = np.cross(vec_z, np.array([0, 0, 1.0]))
    else:
        vec_x = np.cross(vec_z, np.array([1.0, 0, 0]))
    vec_x /= np.linalg.norm(vec_x)
    vec_y = np.cross(vec_z, vec_x)
    
    # Генерируем точки периметра кольца
    alphas = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    ring_x = np.cos(radius_rad)*vec_z[0] + np.sin(radius_rad)*(np.cos(alphas)*vec_x[0] + np.sin(alphas)*vec_y[0])
    ring_y = np.cos(radius_rad)*vec_z[1] + np.sin(radius_rad)*(np.cos(alphas)*vec_x[1] + np.sin(alphas)*vec_y[1])
    ring_z = np.cos(radius_rad)*vec_z[2] + np.sin(radius_rad)*(np.cos(alphas)*vec_x[2] + np.sin(alphas)*vec_y[2])
    
    # Интерполируем значения температуры и маски на эти точные координаты
    prof_T = hp.get_interp_val(map_T, ring_x, ring_y, ring_z)
    prof_mask = hp.get_interp_val(mask, ring_x, ring_y, ring_z)
    
    # Если кольцо слишком глубоко уходит в Галактику (более 30% скрыто), бракуем его
    valid_pixels = prof_mask > 0.5
    if np.sum(valid_pixels) / n_points < 0.7:  
        return None, None
        
    return prof_T, valid_pixels

def main():
    # === ПАРАМЕТРЫ МОДЕЛИ ===
    Lx = float(os.getenv('LX', '28.8'))  # Гпк
    chi_rec = 14.0                       # Гпк (сопутствующее расстояние до ПР)
    data_file = os.getenv('DATA_FILE', 'data/COM_CMB_IQU-smica_2048_R3.00_full.fits')
    
    print("🔬 Запуск CITS-теста (Circles in the Sky) для модели IT³")
    print("="*65)
    
    # 1. ГЕОМЕТРИЧЕСКИЙ ТЕСТ
    has_intersection = Lx < 2 * chi_rec
    print(f"📐 Геометрия: L_min = {Lx:.1f} Гпк, Диаметр горизонта = {2*chi_rec:.1f} Гпк")
    if not has_intersection:
        print("✅ Результат: Топология больше горизонта. Окружности не пересекаются.")
        print("STATUS: PASS_GEOM")
        return 0
    else:
        print("⚠️ Топология меньше горизонта. Ожидаются парные окружности.")
        
    # 2. ПОДГОТОВКА ДАННЫХ
    if not os.path.exists(data_file):
        print(f"ERROR: Карта не найдена: {data_file}", file=sys.stderr)
        return 1
        
    print(f"\n📥 Загрузка карты: {data_file}")
    map_T = hp.read_map(data_file, field=0)
    nside = hp.get_nside(map_T)
    
    # Генерируем резкую маску для профилей (сглаживание тут не нужно)
    npix = hp.nside2npix(nside)
    theta, _ = hp.pix2ang(nside, np.arange(npix))
    mask = (np.abs(np.rad2deg(np.pi/2 - theta)) > 20.0).astype(float)
    
    # 3. ПОИСК И КОРРЕЛЯЦИЯ
    # Считаем радиус окружности по геометрии плоского тора
    radius_rad = np.arccos(Lx / (2 * chi_rec))
    radius_deg = np.rad2deg(radius_rad)
    print(f"🎯 Ожидаемый радиус окружностей: {radius_deg:.2f}°")
    
    # Для MVP берем две противоположные точки на экваторе (ось X)
    center1 = (np.pi/2, 0.0)
    center2 = (np.pi/2, np.pi)
    
    print(f"🔄 Извлечение 1D-профилей вдоль периметра (N_points=720)...")
    prof1, valid1 = extract_ring_profile(map_T, mask, center1[0], center1[1], radius_deg)
    
    # Второе кольцо обходится в обратном направлении (эффект зеркального пересечения)
    prof2, valid2 = extract_ring_profile(map_T, mask, center2[0], center2[1], radius_deg)
    if prof2 is not None:
        prof2 = prof2[::-1]
        valid2 = valid2[::-1]
    
    if prof1 is None or prof2 is None:
        print("\n❌ Окружности слишком сильно перекрываются с плоскостью Галактики.")
        print("Недостаточно чистых данных для достоверной корреляции.")
        print("STATUS: UNKNOWN (Masked)")
        return 0
        
    # Совместная маска (выбрасываем пиксели, где хотя бы одно кольцо в Галактике)
    valid_both = valid1 & valid2
    
    # Считаем корреляцию Пирсона на "чистых" участках колец
    r, p_val = pearsonr(prof1[valid_both], prof2[valid_both])
    
    # 4. ВЫВОД РЕЗУЛЬТАТОВ
    print("\n📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"   Корреляция колец (r) = {r:+.4f}")
    
    # Стандартный порог обнаружения CITS
    threshold = float(os.getenv('CITS_THRESHOLD', '0.65')) 
    status = "FAIL" if r > threshold else "PASS"
    
    print(f"   Порог обнаружения    = {threshold}")
    print(f"   Тест: нет аномального совпадения колец? {'✅ PASS' if status=='PASS' else '❌ FAIL'}")
    print(f"STATUS: {status}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())