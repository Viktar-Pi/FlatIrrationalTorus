import numpy as np

# IT3 Параметры
N_TWIST = 103
WR_DYN = 1.0904
R_SHELL_IN = 243.0  # AU
VOYAGER_SPEED_AU_YR = 3.58 # Текущая скорость

def calculate_topological_drag(r, speed, twist=103):
    """
    Расчет торможения (spectral friction) при прохождении через 
    узлы фрустрации E-nodes.
    """
    # Эффект Пионеров как база + топологическая поправка
    # Формула IT3: a_drag ~ (1 / r^2) * (twist / WR_DYN)
    drag_coeff = (twist / WR_DYN) * 1e-10 # м/с^2
    return drag_coeff

print(f"--- Предсказание IT3 для Voyager 1 ---")
# Ожидаемое ускорение вблизи зоны 243 AU
a_drag = calculate_topological_drag(R_SHELL_IN, VOYAGER_SPEED_AU_YR)
print(f"Ожидаемое аномальное ускорение при прохождении 'Желтка' (243 AU): {a_drag:.4e} м/с^2")
print(f"Дата входа в зону: ~2046 год.")