import streamlit as st
import pandas as pd


def display():
    st.header("Результаты оптимизации страхового запаса сырья")

    # Проверяем, есть ли результаты в session_state
    if 'task5_results' in st.session_state and st.session_state.task5_results is not None:
        results = st.session_state.task5_results

        # Создаем DataFrame для красивого отображения
        df_results = pd.DataFrame({
            'Сырье': results.keys(),
            'Оптимальный размер поставки, т': results.values()
        })

        # Отображаем таблицу с результатами
        st.dataframe(df_results, use_container_width=True, hide_index=True)

        # Дополнительная визуализация - барчарт
        st.subheader("Визуализация оптимальных размеров поставок")
        chart_data = pd.DataFrame({
            'Сырье': list(results.keys()),
            'Оптимальный размер поставки, т': list(results.values())
        })
        st.bar_chart(chart_data.set_index('Сырье'))

    else:
        st.warning(
            "Результаты оптимизации еще не рассчитаны. Пожалуйста, запустите расчет на странице загрузки данных.")