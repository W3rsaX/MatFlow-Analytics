import streamlit as st
import pandas as pd
import numpy as np


def show(material_name, optimal_season, anova_results):
    """
    Отображает результаты анализа влияния времени года на стоимость сырья

    Args:
        material_name (str): Название сырья
        optimal_season (str): Оптимальный сезон для закупки
        anova_results (dict): Результаты дисперсионного анализа
    """
    # Статистические критерии
    st.subheader("📊 Статистические критерии")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "F-статистика",
            f"{anova_results['f_statistic']:.6f}"
        )

    with col2:
        st.metric(
            "P-значение",
            f"{anova_results['p_value']:.6f}"
        )

    with col3:
        st.metric(
            "F-критическое",
            f"{anova_results['f_critical']:.6f}"
        )

    with col4:
        st.metric(
            "Степени свободы",
            f"({anova_results['df_between']}, {anova_results['df_within']})"
        )

    st.divider()

    # Заключение
    st.subheader("📋 Заключение")

    if anova_results['is_significant']:
        st.success("✓ СТАТИСТИЧЕСКИ ЗНАЧИМЫЕ РАЗЛИЧИЯ ОБНАРУЖЕНЫ")

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"P-значение ({anova_results['p_value']:.6f}) < α (0.05)")
        with col2:
            st.info(
                f"F-наблюдаемое ({anova_results['f_statistic']:.4f}) > F-критического ({anova_results['f_critical']:.4f})")

        st.write("**ВЫВОД:** На уровне значимости α=0.05 отвергаем нулевую гипотезу.")
        st.write("Время года оказывает статистически значимое влияние на стоимость сырья.")

    else:
        st.warning("✓ СТАТИСТИЧЕСКИ ЗНАЧИМЫЕ РАЗЛИЧИЯ НЕ ОБНАРУЖЕНЫ")

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"P-значение ({anova_results['p_value']:.6f}) ≥ α (0.05)")
        with col2:
            st.info(
                f"F-наблюдаемое ({anova_results['f_statistic']:.4f}) ≤ F-критического ({anova_results['f_critical']:.4f})")

        st.write("**ВЫВОД:** На уровне значимости α=0.05 нет оснований отвергать нулевую гипотезу.")
        st.write("Статистически значимых различий между групповыми средними не обнаружено.")