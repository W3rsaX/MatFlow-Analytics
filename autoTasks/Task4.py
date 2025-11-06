import numpy as np
import pandas as pd


class Task4:
    def __init__(self, profit_data, residual_value, new_fleet_cost, planning_period=6):
        """
        Класс для решения задачи замены автопарка

        Args:
            profit_data (list): Прибыль автопарка по годам
            residual_value (list): Остаточная стоимость автопарка по годам
            new_fleet_cost (float): Стоимость нового автопарка
            planning_period (int): Период планирования в годах
        """
        self.r = profit_data  # Прибыль
        self.s = residual_value  # Остаточная стоимость
        self.P = new_fleet_cost  # Стоимость нового автопарка
        self.n = planning_period  # Период планирования
        self.max_age = len(profit_data) - 1  # Максимальный возраст автопарка

        # Инициализация таблиц
        self.F = np.zeros((self.n + 1, self.max_age + 1))  # Таблица максимумов
        self.keep_table = np.zeros((self.n + 1, self.max_age + 1))  # Таблица сохранения
        self.replace_table = np.zeros((self.n + 1, self.max_age + 1))  # Таблица замен
        self.decision_table = np.empty((self.n + 1, self.max_age + 1), dtype=object)  # Таблица решений

        # Результаты
        self.optimal_strategy = []
        self.total_profit = 0

    def solve(self):
        """Решение задачи динамического программирования"""
        # Для последнего года (год n)
        for t in range(1, self.max_age + 1):
            if t < len(self.r):
                keep_val = self.r[t]
                replace_val = self.s[t] - self.P + self.r[0]
                self.F[self.n][t] = max(keep_val, replace_val)
                self.keep_table[self.n][t] = keep_val
                self.replace_table[self.n][t] = replace_val
                self.decision_table[self.n][t] = "сохр." if keep_val >= replace_val else "зам."

        # Для лет n-1 до 1
        for k in range(self.n - 1, 0, -1):
            for t in range(1, self.max_age + 1):
                if t < len(self.r) - 1:  # Учитываем, что возраст не может превышать max_age
                    # Для Keep: прибыль этого года + F следующего года с возрастом t+1
                    keep_val = self.r[t] + self.F[k + 1][t + 1]

                    # Для Replace: продажа старого - покупка нового + прибыль нового + F след. года с возрастом 1
                    replace_val = self.s[t] - self.P + self.r[0] + self.F[k + 1][1]

                    self.keep_table[k][t] = keep_val
                    self.replace_table[k][t] = replace_val
                    self.F[k][t] = max(keep_val, replace_val)
                    self.decision_table[k][t] = "сохр." if keep_val >= replace_val else "зам."
                elif t == self.max_age:
                    # Если возраст максимальный, то только замена
                    replace_val = self.s[t] - self.P + self.r[0] + self.F[k + 1][1]
                    self.F[k][t] = replace_val
                    self.decision_table[k][t] = "зам."

        # Вычисление оптимальной стратегии
        self._calculate_optimal_strategy()
        self.total_profit = self.F[1][1]

        return self._get_results()

    def _calculate_optimal_strategy(self):
        """Расчет оптимальной стратегии"""
        current_age = 1
        self.optimal_strategy = []

        for year in range(1, self.n + 1):
            if current_age < len(self.decision_table[year]):
                decision = self.decision_table[year][current_age]
                self.optimal_strategy.append({
                    'year': year,
                    'age': current_age,
                    'decision': decision,
                    'profit_if_keep': self.keep_table[year][current_age] if current_age < len(
                        self.keep_table[year]) else 0,
                    'profit_if_replace': self.replace_table[year][current_age] if current_age < len(
                        self.replace_table[year]) else 0
                })

                if decision == "зам.":
                    current_age = 1
                else:
                    current_age += 1
                    if current_age > self.max_age:
                        current_age = self.max_age

    def _get_results(self):
        """Получение результатов в структурированном виде"""
        return {
            'total_profit': self.total_profit,
            'optimal_strategy': self.optimal_strategy,
            'max_profit_table': self.F,
            'keep_table': self.keep_table,
            'replace_table': self.replace_table,
            'decision_table': self.decision_table
        }

    def get_strategy_table(self):
        """Получение таблицы стратегии в формате DataFrame"""
        strategy_data = []
        for step in self.optimal_strategy:
            # Годовая прибыль (не кумулятивная)
            if step['decision'] == 'сохр.':
                annual_profit = int(self.r[step['age']])  # Прибыль от текущего возраста
            else:
                annual_profit = int(self.s[step['age']] - self.P + self.r[0])  # Прибыль от замены

            strategy_data.append({
                'Год': step['year'],
                'Возраст автопарка': step['age'],
                'Решение': step['decision'],
                'Прибыль за год': f"{annual_profit}"
            })
        return pd.DataFrame(strategy_data)