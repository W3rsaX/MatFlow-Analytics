import pandas as pd
import scipy.stats as stats
from scipy.stats import f
import numpy as np


class Task6:
    """
    Класс для анализа влияния времени года на стоимость сырья
    """

    def __init__(self, data):
        """
        Инициализация класса с данными

        Args:
            data (pd.DataFrame): DataFrame с данными о стоимости сырья по сезонам
        """
        self.data = data
        self.alpha = 0.05

    def anova_analysis(self):
        """
        Проводит однофакторный дисперсионный анализ

        Returns:
            dict: Результаты анализа
        """
        # Извлекаем данные по сезонам (исключаем колонку 'Год')
        seasons_data = []
        season_names = []

        for col in self.data.columns[1:]:  # Пропускаем первую колонку (Год)
            season_data = self.data[col].dropna().values
            seasons_data.append(season_data)
            season_names.append(col)

        # Выполняем однофакторный ANOVA
        f_stat, p_value = stats.f_oneway(*seasons_data)

        # Вычисляем дополнительные параметры
        k = len(seasons_data)  # количество групп
        n_total = sum(len(group) for group in seasons_data)  # общее количество наблюдений
        df_between = k - 1  # степени свободы между группами
        df_within = n_total - k  # степени свободы внутри групп

        # Вычисляем критическое значение F
        f_critical = f.ppf(1 - self.alpha, df_between, df_within)

        return {
            'f_statistic': f_stat,
            'p_value': p_value,
            'f_critical': f_critical,
            'df_between': df_between,
            'df_within': df_within,
            'seasons_data': seasons_data,
            'season_names': season_names,
            'is_significant': p_value < self.alpha
        }

    def find_optimal_season(self, season_names, seasons_data):
        """
        Находит оптимальный сезон для закупки

        Args:
            season_names (list): Список названий сезонов
            seasons_data (list): Список массивов с данными по сезонам

        Returns:
            str: Название оптимального сезона
        """
        # Вычисляем средние значения по каждому сезону
        season_means = [np.mean(season_data) for season_data in seasons_data]

        # Находим сезон с минимальной средней стоимостью (оптимальный для закупки)
        min_mean_idx = np.argmin(season_means)
        optimal_season = season_names[min_mean_idx]

        return optimal_season

    def solve(self):
        """
        Основной метод решения задачи

        Returns:
            tuple: (название сырья, оптимальный сезон, результаты ANOVA)
        """
        # Определяем название сырья
        material_name = "Строительное сырье"

        # Проводим дисперсионный анализ
        anova_results = self.anova_analysis()

        # Находим оптимальный сезон
        optimal_season = self.find_optimal_season(
            anova_results['season_names'],
            anova_results['seasons_data']
        )

        return material_name, optimal_season, anova_results