import os

import pandas as pd
import streamlit as st

from autoTasks.Task3 import solve_transportation_problem
from displays.plan_3 import display_transportation_solution
from utils.styles import load_css

favicon_path = os.path.join('assets', 'logo.ico')

# Конфигурация страницы
st.set_page_config(
    page_title="ООО «Строй-Бетон» - План закупок сырья",
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

st.title("План закупок сырья")

# Загрузка данных
st.header("Загрузка данных")
uploaded_file = st.file_uploader("Загрузите данные (CSV)", type="csv")

if uploaded_file:

    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig')

        # Проверяем структуру данных
        required_columns = [
            'Тип',
            'Поставщик/Производство',
            'Мощность/Потребность'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Отсутствуют обязательные колонки: {missing_columns}")
        else:
            # Кол-во производств
            sprows_count = len(df[df['Тип'] == 'Спрос'])
            required_sprows = len(df.columns) - 3

            # Кол-во поставщиков
            cost_count = len(df[df['Тип'] == 'Стоимость'])
            power_count = len(df[df['Тип'] == 'Мощность'])

            # Контроль названия
            suppliers_cost = set(df[df['Тип'] == 'Стоимость']['Поставщик/Производство'])
            suppliers_power = set(df[df['Тип'] == 'Мощность']['Поставщик/Производство'])
            productions = set(df[df['Тип'] == 'Спрос']['Поставщик/Производство'])
            production_columns = set(df.columns[2:-1])

            if sprows_count != required_sprows:
                st.error(
                    f"Количество строк с типом \"Спрос\" равное: {sprows_count}, а количество столбцов производств равно: {required_sprows}.\nПо структуре CSV файла их должно быть равное количество.")
            elif cost_count != power_count:
                st.error(
                    f"Количество строк c типом \"Стоимость\" равное: {cost_count}, а количество строк c типом \"Мощность\" равно: {power_count}.\nПо структуре CSV файла их должно быть равное количество.")
            elif suppliers_cost != suppliers_power:
                st.error(
                    f"Поставщики: {suppliers_cost - suppliers_power} есть в 'Стоимости', но нет в 'Мощности'.\nА поставщики: {suppliers_power - suppliers_cost} есть в 'Мощности', но нет в 'Стоимости'")
            elif production_columns != productions:
                st.error(
                    f"Производства/о:  {production_columns - productions} есть в столбцах, но нет в спросе.\nА производства/о: {productions - production_columns} есть в спросе, но нет в столбцах")
            else:
                st.success("Данные успешно загружены!")

                if st.checkbox("Показать данные"):
                    st.dataframe(df, hide_index=True)
                # Анализ
                st.header("Решение ")

                # Центрируем кнопку запуска прогноза
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    button_clicked = st.button("Решить", width='stretch', key="run_forecast")

                if button_clicked:
                    with st.spinner("Решаем транспортную задачу...", width='stretch'):
                        solution_data = solve_transportation_problem(dataframe=df)

                    # Отображение результатов
                    display_transportation_solution(solution_data)

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
