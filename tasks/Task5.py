import pandas as pd
import math


def calculate_optimal_order_size(quarterly_consumption, order_cost, storage_cost_per_ton_per_year):
    # Переводим квартальный расход в годовой (умножаем на 4)
    annual_consumption = quarterly_consumption * 4

    # Расчет оптимального размера заказа с округлением ВВЕРХ
    optimal_order = math.sqrt((2 * annual_consumption * order_cost) / storage_cost_per_ton_per_year)

    return math.ceil(optimal_order)


# Входные данные забиты в переменные
materials_data = [
    {"name": "Песок", "quarterly_consumption": 300, "order_cost": 5000, "storage_cost": 1500},
    {"name": "Цемент", "quarterly_consumption": 450, "order_cost": 8000, "storage_cost": 3200},
    {"name": "Щебень", "quarterly_consumption": 600, "order_cost": 7000, "storage_cost": 1200},
    {"name": "Известь", "quarterly_consumption": 15, "order_cost": 3000, "storage_cost": 5000}
]

print("Расчет оптимального размера заказа по формуле Уилсона")

# Расчет и вывод результатов для каждого вида сырья
for material in materials_data:
    optimal_order = calculate_optimal_order_size(
        material["quarterly_consumption"],
        material["order_cost"],
        material["storage_cost"]
    )

    print(f"{material['name']}: {optimal_order} т")


