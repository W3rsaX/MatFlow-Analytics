import os

import pandas as pd
import streamlit as st

from autoTasks.Task1 import GrayScottSupplyModel
from displays.diffusion_1 import display_diffusion_solution
from utils.styles import load_css

favicon_path = os.path.join('assets', 'logo.ico')

# Конфигурация страницы
st.set_page_config(
    page_title="ООО «Строй-Бетон» - Прогнозирование сроков поставки сырья",
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

st.title("Прогнозирование сроков поставки сырья")

# Загрузка данных
st.header("Загрузка данных")
uploaded_file = st.file_uploader("Загрузите данные (CSV)", type="csv")

if uploaded_file:
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig')

        # Проверяем структуру данных
        required_columns = [
            'Поставщик',
            'Плановая_дата',
            'Фактическая_дата'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Отсутствуют обязательные колонки: {missing_columns}")
        else:
            st.success("Данные успешно загружены!")

            if st.checkbox("Показать данные"):
                st.dataframe(df)

            # Анализ
            st.header("Решение")

            # Дополнительные параметры
            col1, col2 = st.columns(2)
            with col1:
                threshold_days = st.slider("Сколько дней симулировать", min_value=1, max_value=15, value=10)
            with col2:
                selected_supplier = st.selectbox("Выберите поставщика для визуализации",
                                                 df['Поставщик'].unique())

            # Центрируем кнопку запуска прогноза
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                button_clicked = st.button("Решить", width='stretch', key="run_forecast")

            if button_clicked:
                with st.spinner("Выполняется расчет модели диффузии...", width="stretch"):
                    # Инициализация и расчет модели
                    model = GrayScottSupplyModel()
                    model.calculate_supplier_parameters(df)

                    # Отображение результатов через отдельный файл
                    display_diffusion_solution(model, df, threshold_days, selected_supplier)

                    # Сохранение модели в session state
                    st.session_state.diffusion_model = model

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
