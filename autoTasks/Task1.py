import random
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.signal import correlate2d


class GrayScottSupplyModel:
    def __init__(self):
        self.supplier_parameters = {}
        self.delay_histories = {}

    def calculate_supplier_parameters(self, df: pd.DataFrame):
        """Рассчитывает параметры для каждого поставщика на основе исторических данных с датами"""

        # Преобразуем даты из строк в datetime
        df['Плановая_дата'] = pd.to_datetime(df['Плановая_дата'], format='%d.%m.%Y', errors='coerce')
        df['Фактическая_дата'] = pd.to_datetime(df['Фактическая_дата'], format='%d.%m.%Y', errors='coerce')

        # Проверяем корректность дат
        if df['Плановая_дата'].isna().any() or df['Фактическая_дата'].isna().any():
            raise ValueError("Некорректный формат дат. Ожидается формат: DD.MM.YYYY")

        # Вычисляем задержки в днях
        df['Задержка_дни'] = (df['Фактическая_дата'] - df['Плановая_дата']).dt.days

        # Группируем по поставщикам
        for supplier in df['Поставщик'].unique():
            supplier_data = df[df['Поставщик'] == supplier]
            delays = supplier_data['Задержка_дни'].tolist()

            # Группируем задержки
            grouped_delays = self.group_delays(delays)

            # Сохраняем параметры
            self.supplier_parameters[supplier] = {
                'delivery_history': delays,
                'grouped_delays': grouped_delays,
                'total_deliveries': len(delays),
                'on_time_deliveries': grouped_delays.get(0, 0),
                'avg_delay': np.mean(delays),
                'max_delay': max(delays) if delays else 0,
                'min_delay': min(delays) if delays else 0,
                'delay_std': np.std(delays) if len(delays) > 1 else 0,
                'early_deliveries': len([d for d in delays if d < 0]),
                'on_time_deliveries_count': len([d for d in delays if d == 0]),
                'late_deliveries': len([d for d in delays if d > 0])
            }

            self.delay_histories[supplier] = delays

    @staticmethod
    def group_delays(delivery_history):
        """Группирует задержки по категориям (в днях)"""
        grouped_counts = {0: 0, 1: 0, 3: 0, 5: 0, 7: 0}

        for delay in delivery_history:
            # Обрабатываем отрицательные задержки (досрочные поставки) как 0
            actual_delay = max(0, delay)

            if actual_delay == 0:
                grouped_counts[0] += 1
            elif actual_delay == 1:
                grouped_counts[1] += 1
            elif actual_delay == 2:
                grouped_counts[3] += 0.9
            elif actual_delay == 3:
                grouped_counts[3] += 1
            elif actual_delay == 4:
                grouped_counts[5] += 0.75
            elif actual_delay == 5:
                grouped_counts[5] += 1
            elif actual_delay == 6:
                grouped_counts[7] += 0.6
            elif actual_delay >= 7:
                grouped_counts[7] += 1

        return {k: round(v) for k, v in grouped_counts.items()}

    def get_supplier_parameters(self, supplier: str) -> Dict:
        """Возвращает параметры для конкретного поставщика"""
        return self.supplier_parameters.get(supplier, {})

    def get_all_suppliers(self) -> List[str]:
        """Возвращает список всех поставщиков"""
        return list(self.supplier_parameters.keys())

    def get_supplier_statistics(self, supplier: str) -> Dict:
        """Возвращает расширенную статистику для поставщика"""
        params = self.get_supplier_parameters(supplier)
        if not params:
            return {}

        delays = params['delivery_history']
        if not delays:
            return {}

        return {
            'total_deliveries': params['total_deliveries'],
            'avg_delay': params['avg_delay'],
            'max_delay': params['max_delay'],
            'min_delay': params['min_delay'],
            'reliability_score': self.calculate_reliability_score(params),
            'early_deliveries': params['early_deliveries'],
            'on_time_deliveries': params['on_time_deliveries_count'],
            'late_deliveries': params['late_deliveries'],
            'on_time_percentage': (params['on_time_deliveries_count'] / params['total_deliveries']) * 100
        }

    def calculate_reliability_score(self, params: Dict) -> float:
        """Вычисляет оценку надежности поставщика (0-100)"""
        total = params['total_deliveries']
        if total == 0:
            return 0

        # Штрафы за задержки
        delay_penalty = min(params['avg_delay'] * 5, 50)  # до 50 баллов штрафа
        consistency_penalty = params['delay_std'] * 2  # штраф за нестабильность

        base_score = 100 - delay_penalty - consistency_penalty
        return max(0, min(100, base_score))


class Diffusion:
    def __init__(self, n, r):
        self.r = r
        self.array = np.zeros((n, n), float)

    def add_cells(self, row, col, *strings):
        for i, s in enumerate(strings):
            self.array[row + i, col: col + len(s)] = np.array([int(b) for b in s])

    def step(self, kernel):
        c = correlate2d(self.array, kernel, mode='same')
        self.array += self.r * c

    def add_white_circles(self, positions, diameter=3):
        """Добавляет белые круги (нулевые значения) в указанных позициях"""
        n = self.array.shape[0]

        circle_patterns = {
            1: [(0, 0)],
            3: [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0)],
            6: [(-2, -1), (-2, 0), (-2, 1),
                (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
                (0, -2), (0, -1), (0, 0), (0, 1), (0, 2),
                (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
                (2, -1), (2, 0), (2, 1)]
        }

        for center_row, center_col in positions:
            if diameter in circle_patterns:
                for dr, dc in circle_patterns[diameter]:
                    i = int(center_row + dr)
                    j = int(center_col + dc)
                    if 0 <= i < n and 0 <= j < n:
                        self.array[i, j] = 0


class DiffusionSimulator:
    def __init__(self):
        # Определяем ядра для диффузии
        self.kernel3 = np.array([
            [0.1, 0.2, 0.2, 0.2, 0.1],
            [0.2, 0.4, 0.4, 0.4, 0.2],
            [0.2, 0.4, 0.5, 0.4, 0.2],
            [0.2, 0.4, 0.4, 0.4, 0.2],
            [0.1, 0.2, 0.2, 0.2, 0.1]
        ])

        self.kernel2 = np.array([
            [0.2, 0.3, 0.3, 0.2],
            [0.3, 0.4, 0.4, 0.3],
            [0.3, 0.4, 0.4, 0.3],
            [0.2, 0.3, 0.3, 0.2]
        ])

        self.kernel1 = np.array([
            [0.15, 0.2, 0.15],
            [0.2, 0.3, 0.2],
            [0.15, 0.2, 0.15]
        ])

        self.kernel0 = np.array([
            [0.2, 0.2],
            [0.2, 0.2],
        ])

    def calculate_percentages(self, array, threshold=0.01):
        """Вычисляет проценты заполнения"""
        total_pixels = array.size
        filled_pixels = np.sum(array > threshold)
        empty_pixels = total_pixels - filled_pixels

        filled_percent = (filled_pixels / total_pixels) * 100
        empty_percent = (empty_pixels / total_pixels) * 100

        return filled_percent, empty_percent

    def simulate_diffusion(self, delay_counts, steps=14, n=50):
        """Запускает симуляцию диффузии на основе истории задержек"""

        # Вычисляем randomsize на основе количества поставок вовремя
        total_deliveries = sum(delay_counts.values())
        on_time_deliveries = delay_counts.get(0, 0)

        if total_deliveries > 0:
            on_time_ratio = on_time_deliveries / total_deliveries
            randomsize = int(30 - (on_time_ratio * 28))
            randomsize = max(2, min(30, randomsize))
        else:
            randomsize = 30

        # Создаем начальную конфигурацию
        size = [str(1) * randomsize for _ in range(randomsize)]
        row = random.randint(3, n - randomsize - 2)
        col = random.randint(3, n - randomsize - 2)

        color_cmap = random.choice(['Purples'])

        diff = Diffusion(n, r=1)
        diff.add_cells(row, col, *size)
        frames = [diff.array.copy()]

        percentages = []
        percentages.append(self.calculate_percentages(diff.array))

        kernel_sequence = []
        available_delays = [0, 1, 3, 5, 7]

        # Строим последовательность ядер
        for step in range(steps):
            current_delay = available_delays[min(step, len(available_delays) - 1)]
            next_delay_index = min(step + 1, len(available_delays) - 1)
            next_delay = available_delays[next_delay_index]

            current_count = delay_counts.get(current_delay, 0)
            next_count = delay_counts.get(next_delay, 0)
            difference = next_count - current_count

            if difference >= 7:
                kernel = self.kernel0
            elif difference >= 3:
                kernel = self.kernel1
            elif difference <= -3:
                kernel = self.kernel3
            else:
                kernel = self.kernel2

            if step == 0:
                kernel_sequence.append(kernel)
            elif step == 7:
                kernel_sequence.extend([kernel] * 4)
            else:
                kernel_sequence.extend([kernel] * 2)

        # Выполняем симуляцию
        for i in range(steps):
            diff.step(kernel_sequence[i])

            # Добавляем белые точки на основе задержек
            current_delay = i
            if current_delay in delay_counts:
                deliveries_with_current_delay = delay_counts[current_delay]
                probability = min(deliveries_with_current_delay * 0.15, 0.8)

                while random.random() < probability:
                    if deliveries_with_current_delay >= 5:
                        diameter = 6
                    elif deliveries_with_current_delay >= 3:
                        diameter = 3
                    else:
                        diameter = 1

                    x = random.randint(i, n)
                    y = random.randint(i, n)
                    diff.add_white_circles([(y, x)], diameter=diameter)

            frames.append(diff.array.copy())
            percentages.append(self.calculate_percentages(diff.array))

        return {
            'frames': frames,
            'percentages': percentages,
            'color_cmap': color_cmap,
            'steps': steps,
            'delay_probabilities': self.calculate_delay_probabilities(percentages, steps)
        }

    def calculate_delay_probabilities(self, percentages, steps):
        """Вычисляет вероятности задержек на основе процентов заполнения"""
        probabilities = {}
        key_steps = [0, 1, 3, 5, 7]

        for step in key_steps:
            if step < len(percentages):
                filled, empty = percentages[step]
                probabilities[step] = empty

        return probabilities
