import os

import pandas as pd
import streamlit as st

from utils.styles import load_css

favicon_path = os.path.join('assets', 'logo.ico')

# Конфигурация страницы
st.set_page_config(
    page_title="ООО «Строй-Бетон» - Оптимизация страхового запаса сырья",
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

st.title("Оптимизация страхового запаса сырья")

# Загрузка данных
st.header("Загрузка данных")
uploaded_file = st.file_uploader("Загрузите данные (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig')
    if df is not None:

        st.success("Данные успешно загружены!")

        if st.checkbox("Показать данные"):
            st.dataframe(df.head())

        # Анализ
        st.header("Решение ")

        # Центрируем кнопку запуска прогноза
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            button_clicked = st.button("Решить", width='stretch', key="run_forecast")

        if button_clicked:
            # Здесь будет реальная модель
            st.success("Оптимизация страхового запаса сырья выполнена успешно!")

            st.subheader("Результаты")

    else:
        st.error("Ошибка загрузки файла")

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
