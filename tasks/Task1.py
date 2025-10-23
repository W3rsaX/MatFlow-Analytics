import random

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from scipy.signal import correlate2d


class Diffusion():

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
        """
        Добавляет белые круги (нулевые значения) в указанных позициях
        """
        n = self.array.shape[0]

        # Шаблоны кругов для маленьких диаметров
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


kernel3 = np.array([
    [0.1, 0.2, 0.2, 0.2, 0.1],
    [0.2, 0.4, 0.4, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.4, 0.2],
    [0.2, 0.4, 0.4, 0.4, 0.2],
    [0.1, 0.2, 0.2, 0.2, 0.1]
])

kernel2 = np.array([
    [0.2, 0.3, 0.3, 0.2],
    [0.3, 0.4, 0.4, 0.3],
    [0.3, 0.4, 0.4, 0.3],
    [0.2, 0.3, 0.3, 0.2]
])

kernel1 = np.array([
    [0.15, 0.2, 0.15],
    [0.2, 0.3, 0.2],
    [0.15, 0.2, 0.15]
])

kernel0 = np.array([
    [0.2, 0.2],
    [0.2, 0.2],
])


def draw_array(array, cmap, **options):
    n, m = array.shape
    options = underride(options,
                        cmap=cmap,
                        alpha=0.7,  # Прозрачность
                        vmin=0, vmax=1,  # Минимальное и максимальное значение для цветовой карты
                        interpolation='none',  # Интерполяция
                        origin='upper',  # Начало координат в верхнем левом углу
                        extent=[0, m, 0, n])  # Диапазон значений по осям Х и Y
    plt.axis([0, m, 0, n])  # Установка пределов осей
    plt.xticks([])  # Удаление делений по осям Х
    plt.yticks([])  # Удаление делений по осям Y

    return plt.imshow(array, **options)


def underride(d, **options):
    for key, val in options.items():
        d.setdefault(key, val)

    return d


def calculate_percentages(array, threshold=0.01):
    total_pixels = array.size
    # Считаем пиксели со значением выше порога как "закрашенные"
    filled_pixels = np.sum(array > threshold)
    empty_pixels = total_pixels - filled_pixels

    filled_percent = (filled_pixels / total_pixels) * 100
    empty_percent = (empty_pixels / total_pixels) * 100

    return filled_percent, empty_percent


def update(frame):
    plt.gca().clear()
    draw_array(frames[frame], color_cmap)

    plt.annotate(
        f"День {frame + 1}/{steps + 1}",
        xy=(0, 0),
        xytext=(0.98, 0.98),
        xycoords='axes fraction',
        fontsize=10,
        fontfamily='monospace',
        color='#2F2F2F',
        ha='right',
        va='top',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
    )
    plt.axis('off')
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    return []


def group_delays(delivery_history):
    grouped_counts = {0: 0, 1: 0, 3: 0, 5: 0, 7: 0}

    for delay in delivery_history:
        if delay == 0:
            grouped_counts[0] += 1
        elif delay == 1:
            grouped_counts[1] += 1
        elif delay == 2:  # задержка 2 дня считается как 3 дня с коэффициентом 0.8
            grouped_counts[3] += 0.9
        elif delay == 3:
            grouped_counts[3] += 1
        elif delay == 4:  # задержка 4 дня считается как 5 дней с коэффициентом 0.8
            grouped_counts[5] += 0.75
        elif delay == 5:
            grouped_counts[5] += 1
        elif delay == 6:  # задержка 6 дней считается как 7 дней с коэффициентом 0.8
            grouped_counts[7] += 0.6
        elif delay == 7:
            grouped_counts[7] += 1

    # Округляем до целых чисел для наглядности
    return {k: round(v) for k, v in grouped_counts.items()}


delivery_history = [0,1,1,0,3,1,0,5,0,1,3,3,5,0,1,0,3,7,0,1,0,5,0,2,0,0,0,2,0,1]

delay_counts = group_delays(delivery_history)

steps = 9

n = 50
# Вычисляем randomsize на основе количества поставок вовремя (0 дней)
total_deliveries = len(delivery_history)
on_time_deliveries = delay_counts[0]  # поставки с задержкой 0 дней

# Если все поставки вовремя -> randomsize = 2
# Если ни одной поставки вовремя -> randomsize = 30
# Линейная интерполяция между этими значениями
if total_deliveries > 0:
    on_time_ratio = on_time_deliveries / total_deliveries
    # Инвертируем: больше вовремя -> меньше randomsize
    randomsize = int(30 - (on_time_ratio * 28))  # от 30 до 2
    randomsize = max(2, min(30, randomsize))  # ограничиваем диапазон
else:
    randomsize = 30  # по умолчанию, если нет поставок

size = [str(1) * randomsize for _ in range(randomsize)]
row = random.randint(3, n - randomsize - 2)
col = random.randint(3, n - randomsize - 2)

color_cmap = random.choice(['Purples'])

diff = Diffusion(n, r=1)
diff.add_cells(row, col, *size)
frames = [diff.array.copy()]

# Создаем список для хранения процентов на каждом шагу
percentages = []

# Вычисляем проценты для начального состояния
percentages.append(calculate_percentages(diff.array))

kernel_sequence = []

available_delays = [0, 1, 3, 5, 7]

for step in range(steps):
    # Находим ближайшие доступные задержки для текущего и следующего шага
    current_delay = available_delays[min(step, len(available_delays) - 1)]
    next_delay_index = min(step + 1, len(available_delays) - 1)
    next_delay = available_delays[next_delay_index]

    current_count = delay_counts.get(current_delay, 0)
    next_count = delay_counts.get(next_delay, 0)

    difference = next_count - current_count

    if difference >= 7:
        kernel = kernel0  # Резкое ухудшение
    elif difference >= 3:
        kernel = kernel1  # Умеренное ухудшение
    elif difference <= -3:
        kernel = kernel3  # Умеренное улучшение
    else:
        kernel = kernel2  # Стабильность

    if (step == 0):
        kernel_sequence.append(kernel)
    elif (step == 7):
        kernel_sequence.append(kernel)
        kernel_sequence.append(kernel)
        kernel_sequence.append(kernel)
        kernel_sequence.append(kernel)
    else:
        kernel_sequence.append(kernel)
        kernel_sequence.append(kernel)

for i in range(steps):

    diff.step(kernel_sequence[i])
    # Проверяем, произошло ли событие генерации белой точки
    current_delay = i  # текущий день соответствует задержке
    if current_delay in delay_counts:
        deliveries_with_current_delay = delay_counts[current_delay]

        # Вероятность события зависит от количества поставок с такой задержкой
        # Максимальная вероятность, если много поставок с такой задержкой
        probability = min(deliveries_with_current_delay * 0.15, 0.8)  # до 80% макс

        while random.random() < probability:
            # Событие произошло! Генерируем белую точку

            # Определяем диаметр точки в зависимости от количества поставок
            if deliveries_with_current_delay >= 5:
                diameter = 6
            elif deliveries_with_current_delay >= 3:
                diameter = 3
            else:
                diameter = 1

            x = random.randint(i, n)
            y = random.randint(i, n)

            # Добавляем белую точку
            diff.add_white_circles([(y, x)], diameter=diameter)

    frames.append(diff.array.copy())
    percentages.append(calculate_percentages(diff.array))

    if i == 0 or i == 1 or i == 3 or i == 5 or i == 7:
        filled, empty = percentages[-1]
        if i == 0:
            print(f"Вероятность поставки вовремя:  {empty:.2f}%")
        elif i == 1:
            print(f"Вероятность задержки на {i} день:  {empty:.2f}%")
        elif i == 3:
            print(f"Вероятность задержки на {i} дня:  {empty:.2f}%")
        elif i == 5 or i == 7:
            print(f"Вероятность задержки на {i} дней:  {empty:.2f}%")

plt.rcParams['toolbar'] = 'None'
fig = plt.figure(figsize=(6, 6),
                 facecolor='white',
                 num="Модель диффузии")
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)


def on_close(event):
    plt.close('all')
    exit()


fig.canvas.mpl_connect('close_event', on_close)

anim = animation.FuncAnimation(fig, update, frames=steps + 1, interval=150, blit=False)

plt.show()
