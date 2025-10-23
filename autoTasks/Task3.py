import pandas as pd
from pulp import *


def read_transportation_data_from_dataframe(df):
    """
    Чтение данных транспортной задачи из DataFrame
    """
    costs = []
    supply = []
    demand = []
    supply_names = []
    demand_names = []

    # Преобразуем DataFrame в список для обработки
    data = df.values.tolist()
    headers = df.columns.tolist()

    # Извлекаем названия потребителей из заголовков (столбцы 2-4)
    demand_names = headers[2:5]

    for row in data:
        data_type = row[0]  # Тип данных: Затраты, Мощность, Потребность
        name = str(row[1])  # Название поставщика/потребителя

        if data_type == 'Стоимость':
            supply_names.append(name)
            # Преобразуем затраты в числа, игнорируя пустые значения
            cost_row = []
            for x in row[2:5]:
                try:
                    cost_row.append(int(float(x)) if pd.notna(x) and x != '' else 0)
                except (ValueError, TypeError):
                    cost_row.append(0)
            costs.append(cost_row)

        elif data_type == 'Мощность':
            try:
                supply_value = int(float(row[5])) if pd.notna(row[5]) and row[5] != '' else 0
                supply.append(supply_value)
            except (ValueError, TypeError):
                supply.append(0)

        elif data_type == 'Спрос':
            try:
                demand_value = int(float(row[5])) if pd.notna(row[5]) and row[5] != '' else 0
                demand.append(demand_value)
            except (ValueError, TypeError):
                demand.append(0)

    return costs, supply_names, demand_names, supply, demand


def solve_transportation_problem(dataframe=None):
    # Чтение данных из переданного источника
    if dataframe is not None:
        costs, supply_names, demand_names, supply, demand = read_transportation_data_from_dataframe(dataframe)
    else:
        raise ValueError("Необходимо указать либо csv_filename, либо dataframe")

    total_supply = sum(supply)
    total_demand = sum(demand)

    # Создаем копии для модификации
    modified_costs = [row[:] for row in costs]
    modified_supply = supply[:]
    modified_supply_names = supply_names[:]
    modified_demand = demand[:]
    modified_demand_names = demand_names[:]

    # Добавляем фиктивного потребителя если нужно
    if total_supply > total_demand:
        for i in range(len(modified_costs)):
            modified_costs[i].append(0)
        modified_demand.append(total_supply - total_demand)
        modified_demand_names.append("Фиктивное производство")
    elif total_supply < total_demand:
        new_row = [0] * len(modified_costs[0])
        modified_costs.append(new_row)
        modified_supply.append(total_demand - total_supply)
        modified_supply_names.append("Фиктивный поставщик")

    # Создаем и решаем задачу
    problem = LpProblem('Transportation_Problem', LpMinimize)

    vars_dict = {}
    for i in range(len(modified_supply)):
        for j in range(len(modified_demand)):
            var_name = f'x_{i}_{j}'
            vars_dict[(i, j)] = LpVariable(var_name, 0, None, LpContinuous)

    # Целевая функция
    problem += lpSum(vars_dict[(i, j)] * modified_costs[i][j]
                     for i in range(len(modified_supply))
                     for j in range(len(modified_demand))), "Total_Cost"

    # Ограничения
    for i in range(len(modified_supply)):
        problem += lpSum(vars_dict[(i, j)] for j in range(len(modified_demand))) == modified_supply[i], f"Supply_{i}"

    for j in range(len(modified_demand)):
        problem += lpSum(vars_dict[(i, j)] for i in range(len(modified_supply))) == modified_demand[j], f"Demand_{j}"

    problem.solve()

    # Формируем результаты
    results = [[0 for _ in range(len(modified_demand))] for _ in range(len(modified_supply))]
    for i in range(len(modified_supply)):
        for j in range(len(modified_demand)):
            results[i][j] = vars_dict[(i, j)].varValue

    # Собираем все данные в словарь
    solution_data = {
        'results': results,
        'supply_names': modified_supply_names,
        'demand_names': modified_demand_names,
        'supply': modified_supply,
        'demand': modified_demand,
        'total_cost': value(problem.objective),
        'original_costs': costs,  # Сохраняем оригинальные затраты для анализа
        'status': LpStatus[problem.status],
        'total_supply': total_supply,
        'total_demand': total_demand
    }

    return solution_data
