import numpy as np # Импорт библиотеки для работы с массивами и обозначение её как пр
import matplotlib.pyplot as plt # Импорт библиотеки для создания графиков и обозначение её как plt
from time import sleep # Импорт функции з1еер из библиотеки time для управления задержками
from IPython.display import clear_output # Импорт функции clear_output из IPython.display для очистки вывода
from utils.utils_1 import underride # Импорт функции underride из модуля utils

class Cell2D(): # Определение класса Cell2D
    """Родительский класс для 2D-клеточного автомата"""

    def __init__(self, n, m=None):
        """Объявление атрибутов.
        n: number of rows
        m: number of columns"""
        m = n if m is None else m # Создание двумерного массива из нулей с размерами n x m
        self.array = np.zeros((n, m), np.uint8)

    def add_cells(self, row, col, *strings):
        """Добавление ячеек заданные места
        row: top row index
        col: left col index
        strings: список строк 0s и 1s"""
        for i, s in enumerate (strings):
            self.array[row+i, col:col+len(s)] = np.array([int(b) for b in s]) # Преобразование строки из 0 и 1 в массив целых чисел и добавление в массив

    def loop(self, iters=1):
        """Отрабатывает заданное количество шагов"""
        for i in range(iters):
            self.step()

    def draw(self, **options):
        """Отображает массив ячеек"""
        draw_array(self.array, **options)

    def animate(self, frames, interval=None, step=None):
        """Анимация работы автомата
        frames: количество кадров для отображения
        interval: время между кадрами в секундах
        step: функция для выполнения одного шага"""
        if step is None:
            self.step = step

        plt.figure()
        try:
            for i in range(frames-1):
                self.draw()
                plt.show()
                if interval:
                    sleep (interval)
                step()
                clear_output(wait=True) # Очистка вывода между кадрами https://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html#IPython.display.clear_output
            self.draw()
            plt.show()
        except KeyboardInterrupt:
            pass

def draw_array(array,cmap, **options):
    """Отображает ячейки клеточного автомата"""
    n, m = array.shape
    options = underride(options,
                        cmap=cmap, # Цветовая карта для отображения (зеленый)
                        alpha=0.7, # Прозрачность
                        vmin=0, vmax=1, # Минимальное и максимальное значение для цветовой карты
                        interpolation='none', # Интерполяция
                        origin='upper', # Начало координат в верхнем левом углу
                        extent=[0, m, 0, n]) # Диапазон значений по осям Х и Y
    plt.axis([0, m, 0, n]) # Установка пределов осей
    plt.xticks([]) # Удаление делений по осям Х
    plt.yticks([]) # Удаление делений по осям Y

    return plt.imshow(array, **options)
