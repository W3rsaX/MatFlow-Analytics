import os
import tempfile

import matplotlib.animation as animation
import streamlit as st
from matplotlib import pyplot as plt

from autoTasks.Task1 import DiffusionSimulator


def display_diffusion_solution(model, df, days, selected_supplier):
    """Отображает результаты модели диффузии"""

    st.header("Результаты прогнозирования")

    # Получаем параметры выбранного поставщика
    supplier_params = model.get_supplier_parameters(selected_supplier)

    if not supplier_params:
        st.error(f"Данные для поставщика {selected_supplier} не найдены")
        return

    # Показываем статистику поставщика
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего поставок", supplier_params['total_deliveries'])
    with col2:
        st.metric("Поставки вовремя", supplier_params['on_time_deliveries'])
    with col3:
        st.metric("Средняя задержка", f"{supplier_params['avg_delay']:.1f} дней")

    # Запускаем симуляцию диффузии
    simulator = DiffusionSimulator()
    result = simulator.simulate_diffusion(
        supplier_params['grouped_delays'],
        steps=days - 1,
        n=50
    )

    # Показываем вероятности задержек
    st.subheader("Вероятности")

    delay_probs = result['delay_probabilities']
    for delay_days, probability in delay_probs.items():
        col1, col2 = st.columns([1, 3])
        if delay_days == 0:
            with col1:
                st.write(f"Поставки вовремя:")
            with col2:
                st.progress(probability / 100, text=f"{probability:.1f}%")
        elif delay_days == 1:
            with col1:
                st.write(f"Задержки на {delay_days} день:")
            with col2:
                st.progress(probability / 100, text=f"{probability:.1f}%")
        elif delay_days == 3:
            with col1:
                st.write(f"Задержки на {delay_days} дня:")
            with col2:
                st.progress(probability / 100, text=f"{probability:.1f}%")
        else:
            with col1:
                st.write(f"Задержки на {delay_days} дней:")
            with col2:
                st.progress(probability / 100, text=f"{probability:.1f}%")

    # Создаем и отображаем анимацию
    st.subheader("Визуализация модели диффузии")

    # Создаем временный файл для GIF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.gif') as tmp_file:
        gif_path = tmp_file.name

    try:
        # Создаем анимацию
        fig = plt.figure(figsize=(8, 8), facecolor='white')
        plt.rcParams['toolbar'] = 'None'

        def update(frame):
            plt.gca().clear()
            im = plt.imshow(
                result['frames'][frame],
                cmap=result['color_cmap'],
                alpha=0.7,
                vmin=0,
                vmax=1,
                interpolation='none',
                origin='upper',
                extent=[0, 50, 0, 50]
            )
            plt.axis('off')

            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

            # Добавляем информацию о дне
            plt.annotate(
                f"День {frame + 1}/{days}",
                xy=(0, 0),
                xytext=(0.98, 0.98),
                xycoords='axes fraction',
                fontsize=10,
                fontfamily='monospace',
                color='#2F2F2F',
                ha='right',
                va='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
            )
            return [im]

        anim = animation.FuncAnimation(
            fig, update, frames=len(result['frames']),
            interval=200, blit=False, repeat=True
        )

        # Сохраняем GIF
        anim.save(gif_path, writer='pillow', fps=5, dpi=80)
        plt.close(fig)

        # Отображаем GIF в Streamlit
        st.image(gif_path, width='stretch')

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            with open(gif_path, "rb") as file:
                btn = st.download_button(
                    label="📥 Скачать модель",
                    data=file,
                    file_name=f"Модель диффузии для поставщика: {selected_supplier}.gif",
                    mime="image/gif",
                    width='stretch'
                )

    finally:
        # Очистка временных файлов
        try:
            if 'gif_path' in locals() and os.path.exists(gif_path):
                os.unlink(gif_path)
        except Exception as cleanup_error:
            # Игнорируем ошибки очистки, так как это временные файлы
            pass
