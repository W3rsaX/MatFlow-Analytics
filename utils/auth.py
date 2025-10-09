import streamlit as st


def check_password(username, password):
    users = {
        'manager': {'password': 'password123', 'name': 'Менеджер МТС', 'role': 'manager'},
        'director': {'password': 'admin123', 'name': 'Директор по производству', 'role': 'director'}
    }

    if username in users and users[username]['password'] == password:
        return True, users[username]['name'], users[username]['role']
    return False, None, None


def login_form():
    with st.form("login_form"):

        st.header("Авторизация", anchor=False)

        username = st.text_input("Логин", placeholder="Введите ваш логин")
        password = st.text_input("Пароль", type="password", placeholder="Введите ваш пароль")

        submitted = st.form_submit_button("Войти", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Пожалуйста, заполните все поля")
            else:
                success, name, role = check_password(username, password)
                if success:
                    st.session_state.update({
                        'authentication_status': True,
                        'name': name,
                        'username': username,
                        'role': role
                    })
                    st.success(f"Добро пожаловать, {name}!")
                    st.rerun()
                else:
                    st.error("Неверные учетные данные")
