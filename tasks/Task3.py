import sys
from pulp import *


def solve_transportation_with_table():
    # Матрица затрат
    costs = [
        [200, 600, 250],
        [180, 720, 1100],
        [580, 250, 150],
        [350, 320, 400]
    ]

    # Мощности поставщиков
    supply = [80, 60, 100, 120]
    supply_names = ["Песок-Строй", "Строй-Ресурс", "Песок-М", "Золотой песок"]

    # Потребности потребителей
    demand = [100, 130, 85]
    demand_names = ["Производство на Озерной", "Производство на Черкизовской", "Производство на Беговой"]

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

    # Формируем таблицу результатов
    results = [[0 for _ in range(len(modified_demand))] for _ in range(len(modified_supply))]
    for i in range(len(modified_supply)):
        for j in range(len(modified_demand)):
            results[i][j] = vars_dict[(i, j)].varValue

    return (results, modified_supply_names, modified_demand_names,
            modified_supply, modified_demand, value(problem.objective))


def print_beautiful_table(results, supply_names, demand_names, supply, demand, total_cost):
    # Заголовок таблицы
    print("\n" + "=" * 189)
    # Заголовки потребителей
    print("|" + " " * 27 + "| ", end="")
    for name in demand_names:
        print(f"{name:<30} | ", end="")

    print("Мощность поставщиков, т.  |")
    print("-" * 189)

    # Данные по поставщикам
    for i in range(len(supply_names)):
        print(f"| {supply_names[i]:<25} | ", end="")
        for j in range(len(demand_names)):
            if results[i][j] > 0:
                print(f"{results[i][j]:<30} | ", end="")
            else:
                print(f"{'0':<30} | ", end="")
        print(f"{supply[i]:<25} |")

    # Строка с спросом
    print("|" + "-" * 187 + "|")
    print(f"| {'Спрос производств, т.':<25} | ", end="")
    for j in range(len(demand_names)):
        print(f"{demand[j]:<30} | ", end="")
    print(f"{'':<25} |")

    print("=" * 189)
    print(f"Общая стоимость доставки: {total_cost} руб.")


# Запускаем решение и выводим результат
results, supply_names, demand_names, supply, demand, total_cost = solve_transportation_with_table()
print_beautiful_table(results, supply_names, demand_names, supply, demand, total_cost)

# Дополнительная информация
print(f"\nДетализация поставок:")
for i in range(len(supply_names)):
    for j in range(len(demand_names)):
        if results[i][j] > 0:
            print(f"{supply_names[i]} -> {demand_names[j]}: {results[i][j]} т.")

print(f"\nОбщая стоимость доставки: {total_cost} руб.")