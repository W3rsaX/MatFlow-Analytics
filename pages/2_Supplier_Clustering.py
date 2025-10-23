import os

import pandas as pd
import streamlit as st

from autoTasks.Task2 import clustering_solver
from displays.clustering_2 import results_display
from utils.styles import load_css

favicon_path = os.path.join('assets', 'logo.ico')

# Конфигурация страницы
st.set_page_config(
    page_title="ООО «Строй-Бетон» - Кластеризация поставщиков",
    page_icon=favicon_path,
    layout="centered",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Загрузка CSS стилей
load_css()
st.logo("assets/logo.png")

# Проверка авторизации
if 'authentication_status' not in st.session_state or not st.session_state.authentication_status:
    st.switch_page("Home.py")

st.title("Кластеризация поставщиков")

# Загрузка данных
st.header("Загрузка данных")
uploaded_file = st.file_uploader("Загрузите данные (CSV)", type="csv")

if uploaded_file:
    try:
        # Загружаем с указанием разделителя ;
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig')

        # Проверяем структуру данных
        required_columns = [
            'Название поставщика',
            'Коэффициент выполнения поставок в срок (%)',
            'Стоимость 1 тонны песка (руб)',
            'Содержание примесей (%)'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Отсутствуют обязательные колонки: {missing_columns}")
        else:
            st.success(f"Данные успешно загружены! Загружено {len(df)} поставщиков.")

            if st.checkbox("Показать данные"):
                st.dataframe(df)

            # Анализ
            st.header("Решение")

            # Центрируем кнопку запуска кластеризации
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                button_clicked = st.button("Решить", width='stretch', key="run_clustering")

            if button_clicked:
                with st.spinner("Выполняется кластеризация поставщиков...", width="stretch"):
                    try:
                        # Выполняем кластеризацию
                        result_df, cluster_stats, elbow_data = clustering_solver.perform_clustering(df)

                        st.success("Кластеризация завершена успешно!")

                        # Отображаем результаты
                        results_display.display_cluster_summary(cluster_stats)
                        results_display.display_cluster_plot(result_df)
                        results_display.display_pair_plot(result_df)
                        results_display.display_raw_data(result_df, cluster_stats)

                    except Exception as e:
                        st.error(f"Ошибка при выполнении кластеризации: {str(e)}")

    except Exception as e:
        st.error(f"Ошибка загрузки файла: {str(e)}")
        st.info("Убедитесь, что файл имеет разделитель ';' и кодировку UTF-8")

with st.sidebar:
    if st.button("↩️ На главную страницу", width='stretch'):
        st.switch_page("pages/Analytics_Dashboard.py")

    # Кнопка выхода
    st.markdown("---")
    if st.button("🚪 Выйти из системы", width='stretch'):
        # Очищаем сессию
        for key in ['authentication_status', 'name', 'username', 'role']:
            if key in st.session_state:
                del st.session_state[key]
        # Перенаправляем на Home страницу
        st.switch_page("Home.py")
