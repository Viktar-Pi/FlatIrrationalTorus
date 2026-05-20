import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

def create_sphere(radius, color, opacity, name):
    """Генерирует 3D-сферу для визуализации вакуумных мембран IT3"""
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    
    return go.Surface(
        x=x, y=y, z=z,
        opacity=opacity,
        colorscale=[[0, color], [1, color]],
        showscale=False,
        name=name,
        hoverinfo='skip'
    )

def build_it3_architecture(input_file):
    print("Инициализация IT3 Galactic Resonance Architecture Visualizer...")
    
    # 1. Загрузка эмпирических данных
    try:
        df = pd.read_csv(input_file)
        print(f"Загружено {len(df)} кандидатов в узлы.")
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return

    # Если точек слишком много, берем репрезентативную выборку, чтобы браузер не завис
    MAX_POINTS = 10000
    if len(df) > MAX_POINTS:
        print(f"Сэмплирование до {MAX_POINTS} точек для плавной 3D-отрисовки...")
        df_plot = df.sample(MAX_POINTS, random_state=42)
    else:
        df_plot = df

    fig = go.Figure()

    # 2. Добавление эмпирических данных (Аномалии NOIRLab)
    fig.add_trace(go.Scatter3d(
        x=df_plot['X'], y=df_plot['Y'], z=df_plot['Z'],
        mode='markers',
        marker=dict(
            size=2,
            color=df_plot['delta_theta'],  # Цветовая шкала по точности совпадения
            colorscale='Plasma',
            opacity=0.8,
            colorbar=dict(title="Отклонение Δθ (град)", x=0.85)
        ),
        name='Аномалии NOIRLab',
        text=df_plot['id'] + '<br>Δθ: ' + df_plot['delta_theta'].round(3).astype(str) + '°',
        hoverinfo='text'
    ))

    # 3. Генерация 12 теоретических E-узлов (Кубооктаэдр IT3)
    r_in = 243.0
    nodes = np.array([
        [r_in, r_in, 0], [r_in, -r_in, 0], [-r_in, r_in, 0], [-r_in, -r_in, 0],
        [r_in, 0, r_in], [r_in, 0, -r_in], [-r_in, 0, r_in], [-r_in, 0, -r_in],
        [0, r_in, r_in], [0, r_in, -r_in], [0, -r_in, r_in], [0, -r_in, -r_in]
    ])
    
    fig.add_trace(go.Scatter3d(
        x=nodes[:, 0], y=nodes[:, 1], z=nodes[:, 2],
        mode='markers+text',
        marker=dict(size=8, color='red', symbol='diamond'),
        text=[f'E-{i+1}' for i in range(12)],
        textposition='top center',
        name='Теоретические узлы IT3'
    ))

    # 4. Отрисовка Внутренней резонансной сферы (r_in = 243.0 AU)
    fig.add_trace(create_sphere(243.0, 'cyan', 0.1, 'Inner Sphere (243.0 AU)'))

    # 5. Отрисовка Внешней резонансной сферы (R_out = 420.9 AU)
    fig.add_trace(create_sphere(420.9, 'blue', 0.05, 'Outer Sphere (420.9 AU)'))

    # 6. Добавление центрального узла (Солнце)
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=10, color='yellow', symbol='circle'),
        name='Солнце (0,0,0)'
    ))

    # 7. Настройка космического интерфейса, осей и вращения
    axis_config = dict(
        showbackground=False,
        showgrid=True,
        zeroline=True,
        gridcolor='rgba(255, 255, 255, 0.2)',
        zerolinecolor='rgba(255, 255, 255, 0.5)'
    )

    fig.update_layout(
        title='IT3 Framework: Galactic Resonance Architecture (NOIRLab Empirical Data)',
        scene=dict(
            xaxis=dict(title='X (AU)', range=[-450, 450], **axis_config),
            yaxis=dict(title='Y (AU)', range=[-450, 450], **axis_config),
            zaxis=dict(title='Z (AU)', range=[-450, 450], **axis_config),
            aspectmode='cube' # Важно! Чтобы сферы не были сплюснутыми
        ),
        paper_bgcolor='black',
        font=dict(color='white'),
        margin=dict(l=0, r=0, b=0, t=40),
        # Добавляем кнопки для управления вращением
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]),
                     dict(label="Pause",
                          method="animate",
                          args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])],
            showactive=False,
            x=0.1,
            y=0.1,
            xanchor="right",
            yanchor="top"
        )]
    )

    # 8. Создание кадров для анимации вращения камеры
    frames = []
    for i in range(0, 360, 2):
        angle = math.radians(i)
        camera_x = 1.5 * math.cos(angle)
        camera_y = 1.5 * math.sin(angle)
        
        frames.append(go.Frame(layout=dict(scene=dict(camera=dict(eye=dict(x=camera_x, y=camera_y, z=0.5))))))
    
    fig.frames = frames
    fig.layout.scene.camera = dict(eye=dict(x=1.5, y=0, z=0.5))

    # 9. Рендеринг и сохранение
    output_html = "IT3_Architecture_3D.html"
    fig.write_html(output_html, auto_play=False)
    print(f"\nГотово! Интерактивная 3D модель сохранена как: {output_html}")
    return output_html

if __name__ == "__main__":
    build_it3_architecture('IT3_Resonance_Hits.csv')