import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def display_transportation_solution(solution_data):
    # Извлекаем данные из словаря
    results = solution_data['results']
    supply_names = solution_data['supply_names']
    demand_names = solution_data['demand_names']
    supply = solution_data['supply']
    demand = solution_data['demand']
    total_cost = solution_data['total_cost']
    original_costs = solution_data['original_costs']
    status = solution_data['status']

    st.title("Решение транспортной задачи")

    # Статус решения
    if status == 'Optimal':
        st.success("✅ Задача решена оптимально!")
    else:
        st.warning(f"Статус решения: {status}")

    # Основные метрики
    st.subheader("📊 Основные показатели")
    col1, col2, col3, col4 = st.columns(4)
    with col2:
        st.metric("Общая стоимость", f"{total_cost:,.0f} р.")
    with col3:
        st.metric("Общий объем", f"{sum(supply):,} т.")


    st.markdown("---")

    #Матрица поставок
    st.subheader("📋 Матрица оптимальных поставок")

    # Создаем DataFrame для матрицы поставок
    df_supply = pd.DataFrame(results, index=supply_names, columns=demand_names)

    # Функция для стилизации
    def style_supply_table(val):
        if val == 0:
            return 'color: lightgray'
        elif isinstance(val, (int, float)) and val > 0:
            return 'color: green; font-weight: bold'
        return ''

    # Отображаем стилизованную таблицу
    styled_df = df_supply.style.map(style_supply_table).format({
        **{name: "{:.1f}" for name in demand_names}
    })

    st.dataframe(styled_df, width='stretch')

    #Диаграмма потоков (Sankey)
    st.subheader("🔗 Визуализация потоков поставок")

    if len(results) > 0 and len(results[0]) > 0:
        source = []
        target = []
        value = []
        label = supply_names + demand_names

        for i, supplier in enumerate(supply_names):
            for j, consumer in enumerate(demand_names):
                if results[i][j] > 0:
                    source.append(i)
                    target.append(len(supply_names) + j)
                    value.append(results[i][j])

        if source:  # Проверяем, есть ли данные для отображения
            fig_sankey = go.Figure(data=[go.Sankey(
                node=dict(
                    label=label
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    color="rgba(184,184,208, 0.9)"
                ),
                textfont=dict(
                    color="rgba(10,10,26, 1)",
                    size=14
                )
            )])

            fig_sankey.update_layout(
                title_text="Потоки поставок между поставщиками и производствами",
                font_size=10,
                height=400
            )
            st.plotly_chart(fig_sankey, width=True)
        else:
            st.info("Нет данных для построения диаграммы потоков")

    #Детализация поставок
    st.subheader("🔍 Детализация поставок")

    deliveries = []
    for i, supplier in enumerate(supply_names):
        for j, consumer in enumerate(demand_names):
            if results[i][j] > 0:
                # Используем оригинальные затраты (без фиктивных)
                cost_per_ton = original_costs[i][j] if i < len(original_costs) and j < len(original_costs[i]) else 0
                if (cost_per_ton != 0):
                    deliveries.append({
                        'От поставщика': supplier,
                        'К потребителю': consumer,
                        'Объем, т.': results[i][j],
                        'Стоимость за тонну, руб.': cost_per_ton,
                        'Общая стоимость, руб.': results[i][j] * cost_per_ton
                    })

    if deliveries:
        df_deliveries = pd.DataFrame(deliveries)

        # Сортируем по стоимости
        df_deliveries = df_deliveries.sort_values('Общая стоимость, руб.', ascending=False)

        st.dataframe(
            df_deliveries.style.format({
                'Объем, т.': '{:.1f}',
                'Стоимость за тонну, руб.': '{:.0f}',
                'Общая стоимость, руб.': '{:,.0f}'
            }),
            width='stretch'
        )
    else:
        st.info("Нет активных поставок для отображения")