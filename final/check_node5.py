import pandas as pd

csv_file = "IT3_SNIPER_EXPANDED_Node_5_Cetus_EXPANDED.csv"

try:
    df = pd.read_csv(csv_file)
    print("="*60)
    print("🎉 ДАННЫЕ УЗЛА №5 (КИТ/РЫБЫ) УСПЕШНО ИЗВЛЕЧЕНЫ!")
    print("="*60)
    
    # Группируем по найденным орбитам
    for track_id, group in df.groupby('track_id'):
        print(f"\n🚀 ОРБИТА: {track_id}")
        print(f"Среднее RA:  {group['ra'].mean():.5f}°")
        print(f"Среднее Dec: {group['dec'].mean():.5f}°")
        print(f"Яркость:     {group['mag'].mean():.2f} mag")
        print(f"Кол-во фото: {len(group)}")
        print(f"Даты (MJD):  {group['mjd'].min():.1f} — {group['mjd'].max():.1f}")
        
    print("\n" + "="*60)
except Exception as e:
    print(f"Ошибка чтения файла: {e}. Скрипт еще работает?")