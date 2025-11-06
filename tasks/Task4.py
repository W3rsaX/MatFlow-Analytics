import numpy as np

r = [10, 9, 9, 8, 8, 7, 6]
s = [9, 8, 8, 7, 6, 6, 4]
P = 10
n = 6

F = np.zeros((n + 1, n + 1))
keep_table = np.zeros((n + 1, n + 1))
replace_table = np.zeros((n + 1, n + 1))
decision_table = np.empty((n + 1, n + 1), dtype=object)

# Для последнего года (год 6)
for t in range(1, n + 1):
    if t <= 6:
        keep_val = r[t]
        replace_val = s[t] - P + r[0]
        F[n][t] = max(keep_val, replace_val)
        keep_table[n][t] = keep_val
        replace_table[n][t] = replace_val
        decision_table[n][t] = "сохр." if keep_val >= replace_val else "зам."

# Для лет 5-1
for k in range(n - 1, 0, -1):
    for t in range(1, k + 1):
        if t <= 6:
            # Для Keep: прибыль этого года + F следующего года с возрастом t+1
            keep_val = r[t] + F[k + 1][t + 1]

            # Для Replace: продажа старого - покупка нового + прибыль нового + F след. года с возрастом 1
            replace_val = s[t] - P + r[0] + F[k + 1][1]

            keep_table[k][t] = keep_val
            replace_table[k][t] = replace_val
            F[k][t] = max(keep_val, replace_val)
            decision_table[k][t] = "сохр." if keep_val >= replace_val else "зам."

print("Таблица максимумов:")
for k in range(n, 0, -1):
    row = [f"{int(F[k][t])}" for t in range(1, k + 1)]
    print(f"Год {k}: {row}")

print("\nТаблица сохранения:")
for k in range(n, 0, -1):
    row = [f"{int(keep_table[k][t])}" for t in range(1, k + 1)]
    print(f"Год {k}: {row}")

print("\nТаблица замен:")
for k in range(n, 0, -1):
    row = [f"{int(replace_table[k][t])}" for t in range(1, k + 1)]
    print(f"Год {k}: {row}")

print("\nТаблица решений:")
for k in range(n, 0, -1):
    row = [f"{decision_table[k][t]}" for t in range(1, k + 1)]
    print(f"Год {k}: {row}")

print("\nОптимальная стратегия замены автопарка:")
current_age = 1
for year in range(1, n + 1):
    decision = decision_table[year][current_age]
    print(f"Год {year} (возраст автопарка: {current_age}): {decision}")
    if decision == "зам.":
        current_age = 1
    else:
        current_age += 1
        if current_age > 6:
            current_age = 6

print(f"\nОбщая прибыль составит: {int(F[1][1])} млн. руб.")