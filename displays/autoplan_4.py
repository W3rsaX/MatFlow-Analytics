import streamlit as st
import pandas as pd
import numpy as np
from autoTasks.Task4 import Task4


def display_autoplan_results(df):
    """Отображение результатов решения задачи замены автопарка"""

    st.header("📊 Результаты планирования замены автопарка")

    # Извлечение данных из DataFrame
    try:
        # Поиск нужных столбцов
        profit_row = df[df['Переменная'] == 'Прибыль автопарка']
        residual_row = df[df['Переменная'] == 'Остаточная стоимость автопарка']
        cost_row = df[df['Переменная'] == 'Стоимость нового автопарка']

        if profit_row.empty or residual_row.empty or cost_row.empty:
            st.error("Не найдены необходимые данные в файле")
            return

        # Извлечение данных
        profit_data = [float(x.strip()) for x in profit_row['Данные'].iloc[0].split(',')]
        residual_data = [float(x.strip()) for x in residual_row['Данные'].iloc[0].split(',')]
        new_fleet_cost = float(cost_row['Данные'].iloc[0])

        st.subheader("Исходные данные")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Прибыль по годам:**")
            profit_df = pd.DataFrame({
                'Возраст': range(len(profit_data)),
                'Прибыль (млн. руб.)': profit_data
            })
            st.dataframe(profit_df, hide_index=True, width='stretch')

        with col2:
            st.write("**Остаточная стоимость:**")
            residual_df = pd.DataFrame({
                'Возраст': range(len(residual_data)),
                'Стоимость (млн. руб.)': residual_data
            })
            st.dataframe(residual_df, hide_index=True, width='stretch')

        st.metric("Стоимость нового автопарка", f"{new_fleet_cost} млн. руб.")

        task = Task4(profit_data, residual_data, new_fleet_cost)
        results = task.solve()

        # Отображение оптимальной стратегии
        st.subheader("🎯 Оптимальная стратегия замены")

        strategy_df = task.get_strategy_table()
        st.dataframe(strategy_df, width='stretch', hide_index=True)

        st.success(
            f"🎉 **Итоговая прибыль за {len(results['optimal_strategy'])} лет: {results['total_profit']} млн. руб.**")

    except Exception as e:
        st.error(f"Ошибка при обработке данных: {str(e)}")
        st.info("Убедитесь, что формат данных соответствует ожидаемому:")
        st.code("""
Переменная;Данные
Прибыль автопарка;10,9,9,8,8,7,6;
Остаточная стоимость автопарка;9,8,8,7,6,6,4;
Стоимость нового автопарка;10
        """)