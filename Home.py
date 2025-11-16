import os

import streamlit as st

from utils.auth import login_form
from utils.styles import load_css

favicon_path = os.path.join('assets', 'logo.ico')

# Конфигурация страницы
st.set_page_config(
    page_title="ООО «Строй-Бетон» - Авторизация",
    page_icon=favicon_path,
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=None
)

load_css()


def main():
    if st.session_state.get('authentication_status'):
        st.switch_page("pages/Analytics_Dashboard.py")

    st.image("assets/logo.png", width="stretch")

    # Заголовок и описание
    st.title("Управление цепочками поставок сырья", anchor=False)
    st.markdown("""
        <p style='font-size: 1.2rem;'>
        Платформа для управления поставками сырья<br>
        На основе автоматизации задач
        </p>
    """, unsafe_allow_html=True)

    # Форма авторизации
    login_form()

    # Тестовые доступы
    with st.expander("Тестовые доступы", expanded=False):
        st.info("""
        **Для тестирования системы:**
        - 👤 **Доступ менеджера**: `manager`/`password123`
        - 👤 **Доступ директора**: `director`/`admin123`

        *Используйте эти данные для ознакомления со всеми функциями*
        """)

    # Футер
    st.markdown("""
        <div style='
            text-align: center; 
            color: #B8B8D0; 
            margin-top: 3rem;
            padding: 1.5rem;
            border-top: 1px solid #2D2B55;
        '>
        <p style='margin: 0; font-size: 0.9rem;'>
        MatFlow Analytics • Системы управления цепочками поставок сырья • 2025
        </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
