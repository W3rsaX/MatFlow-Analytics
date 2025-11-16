import os

import streamlit as st

from utils.styles import load_css

favicon_path = os.path.join('assets', 'logo.ico')

# Конфигурация страницы
st.set_page_config(
    page_title="ООО «Строй-Бетон» - Аналитическая панель",
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

if 'authentication_status' not in st.session_state or not st.session_state.authentication_status:
    st.warning("Пожалуйста, авторизуйтесь")

    container = st.container()
    with container:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Перейти на страницу авторизации", width='stretch'):
                st.switch_page("Home.py")

    st.stop()

# Основной контент
st.markdown("<h1>Аналитическая панель<br>ООО «Строй-Бетон»</h1>",unsafe_allow_html=True)
st.success(f"Добро пожаловать, {st.session_state['name']}! 👋")

# Сайдбар с навигацией
with st.sidebar:
    # Безопасное получение данных из session_state
    user_name = st.session_state.get('name', 'Пользователь')
    username = st.session_state.get('username', '')

    if username == 'manager':
        user_role = 'Менеджер'
    elif username == 'director':
        user_role = 'Директор'
    else:
        user_role = 'Гость'

    st.markdown(f"""
        <style>
        .sidebar-header {{
            text-align: center;
            margin-bottom: 1rem;
        }}
        .user-info {{
            background: linear-gradient(135deg, rgba(123, 104, 238, 0.1) 0%, rgba(106, 90, 205, 0.1) 100%);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #3D3B6B;
        }}
        </style>

        <div class="sidebar-header">
            <h1>Навигация</h1>
        </div>

        <div class="user-info">
            <strong>👤 {user_name}</strong><br>
            <small>Роль: {user_role}</small>
        </div>
    """, unsafe_allow_html=True)

    # Навигация
    st.subheader("Основные задачи", anchor=False)

    if st.button("📈 Прогнозирование сроков поставки сырья", width='stretch'):
        st.switch_page("pages/1_Delivery_Forecast.py")

    if st.button("🏷️ Кластеризация поставщиков", width='stretch'):
        st.switch_page("pages/2_Supplier_Clustering.py")

    if st.button("📋 План закупок сырья", width='stretch'):
        st.switch_page("pages/3_Procurement_Plan.py")

    if st.button("📅 План обновления автопарка", width='stretch'):
        st.switch_page("pages/4_Auto_PLan.py")

    if st.button("🛡️ Оптимизация управления запасами сырья", width='stretch'):
        st.switch_page("pages/5_Safety_Stock.py")

    if st.button("⭐ Анализ влияния времени года на стоимость сырья", width='stretch'):
        st.switch_page("pages/6_Disperison.py")

    # Кнопка выхода
    st.markdown("---")
    if st.button("🚪 Выйти из системы", width='stretch'):
        # Очищаем сессию
        for key in ['authentication_status', 'name', 'username', 'role']:
            if key in st.session_state:
                del st.session_state[key]
        # Перенаправляем на Home страницу
        st.switch_page("Home.py")

# Основной контент дашборда
st.markdown("""
    <div style='
        background: linear-gradient(135deg, #161635 0%, #1E1E3F 100%);
        border: 1px solid #2D2B55;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
    '>
    <h3 style='color: #7B68EE; margin-bottom: 1rem; text-decoration: none;'>🎯 Обзор системы</h3>
    <p style='color: #B8B8D0;'>
    MatFlow Analytics предоставляет комплексные инструменты для оптимизации цепочки поставок строительных материалов. 
    Выберите задачу в боковой панели для начала работы.
    </p>
    </div>
""", unsafe_allow_html=True)