import pandas as pd
import math


class Task5:
    """
    Класс для решения задачи оптимизации управления запасами сырья
    с использованием модели Уилсона (EOQ - Economic Order Quantity)
    """

    @staticmethod
    def calculate_optimal_order_size(quarterly_consumption, order_cost, storage_cost_per_ton_per_year):
        """
        Расчет оптимального размера заказа по формуле Уилсона

        Args:
            quarterly_consumption (float): Квартальный расход сырья, т
            order_cost (float): Затраты на поставку, руб.
            storage_cost_per_ton_per_year (float): Затраты на хранение 1 т. сырья в год, руб.

        Returns:
            int: Оптимальный размер заказа, т (округленный вверх)
        """
        # Переводим квартальный расход в годовой (умножаем на 4)
        annual_consumption = quarterly_consumption * 4

        # Расчет оптимального размера заказа по формуле Уилсона
        # EOQ = √(2 * годовой_спрос * затраты_на_заказ / затраты_на_хранение)
        optimal_order = math.sqrt((2 * annual_consumption * order_cost) / storage_cost_per_ton_per_year)

        # Округляем вверх до целого числа
        return math.ceil(optimal_order)

    def solve(self, data):
        """
        Решение задачи оптимизации для всех видов сырья

        Args:
            data (pd.DataFrame): DataFrame с исходными данными

        Returns:
            dict: Словарь с результатами {название_сырья: оптимальный_размер_поставки}
        """
        results = {}

        # Проверяем структуру данных
        required_columns = ['Сырье', 'Квартальный расход сырья, т.',
                            'Затраты на поставку, руб.', 'Затраты на хранение 1 т. сырья в год, руб.']

        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Отсутствует обязательная колонка: {col}")

        # Обрабатываем каждую строку данных
        for index, row in data.iterrows():
            material_name = row['Сырье']
            quarterly_consumption = row['Квартальный расход сырья, т.']
            order_cost = row['Затраты на поставку, руб.']
            storage_cost = row['Затраты на хранение 1 т. сырья в год, руб.']

            # Проверяем корректность данных
            if pd.isna(quarterly_consumption) or pd.isna(order_cost) or pd.isna(storage_cost):
                raise ValueError(f"Неполные данные для сырья: {material_name}")

            # Рассчитываем оптимальный размер заказа
            optimal_order = self.calculate_optimal_order_size(
                quarterly_consumption, order_cost, storage_cost
            )

            results[material_name] = optimal_order

        return results

    def get_description(self):
        """
        Возвращает описание задачи и метода решения
        """
        return {
            'name': 'Оптимизация управления запасами сырья',
            'description': 'Расчет оптимального размера заказа сырья по модели Уилсона (EOQ)',
            'formula': 'EOQ = √(2 * Годовой_спрос * Затраты_на_заказ / Затраты_на_хранение)',
            'parameters': {
                'Годовой_спрос': 'Квартальный расход × 4',
                'Затраты_на_заказ': 'Постоянные затраты на одну поставку',
                'Затраты_на_хранение': 'Годовые затраты на хранение 1 тонны'
            }
        }