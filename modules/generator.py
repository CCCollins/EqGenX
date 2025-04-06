import os
import platform
import json
import random
import re
import sympy as sp
import subprocess
from openpyxl import Workbook
from scipy.optimize import fsolve


def load_enabled_templates(file_path="tasks.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            templates = json.load(f)
            enabled_templates = []

            for t in templates:
                if t.get("enabled", False):
                    template = t["template"]
                    # Извлекаем все переменные внутри фигурных скобок
                    variables = re.findall(r"\{(.*?)\}", template)
                    enabled_templates.append({
                        "template": template,
                        "variables": variables
                    })

            return enabled_templates
    except Exception as e:
        print("Ошибка при загрузке tasks.json:", e)
        return []


def format_equation_for_display(equation):
    # Убираем * в "2*x" → "2x"
    equation = equation.replace('*x', 'x')
    equation = equation.replace('*(', '(')

    # Убираем -1x и -1(
    equation = equation.replace('-1x', '-x')
    equation = equation.replace('+1x', '+x')
    equation = equation.replace('-1(', '-(')
    equation = equation.replace('+1(', '+(')

    # Заменяем точки на запятые
    equation = equation.replace('.', ',')

    return equation


# Функция для генерации уравнений
def generate_random_number(num_range, decimal_places, prob_fraction):
    while True:
        if random.random() < prob_fraction:
            num = random.randint(-num_range, num_range)
            if num != 0 and num != 1:
                return num
        else:
            num = round(random.uniform(-num_range, num_range), decimal_places)
            if num != int(num):  # Убедимся, что это не целое число
                return num


x = sp.symbols('x')


# Решение уравнения с использованием fsolve
def solve_equation_numeric(equation):
    try:
        lhs, rhs = equation.split('=')
        lhs_expr = sp.lambdify(x, sp.sympify(lhs), "numpy")
        rhs_expr = sp.lambdify(x, sp.sympify(rhs), "numpy")

        def func(x_val):
            return lhs_expr(x_val) - rhs_expr(x_val)

        # Предполагаем начальное приближение (это можно настраивать по вашему усмотрению)
        initial_guess = 0.0
        solution = fsolve(func, initial_guess)[0]

        # Проверяем, имеет ли решение два знака после запятой
        if abs(solution) != int(solution):  # если решение не целое
            str_solution = str(solution)
            if len(str_solution.split('.')[1]) <= 2:
                return round(solution, 2)
            else:
                return None
        else:
            return int(solution)  # целое число возвращаем как int
    except Exception as ex:
        print(f"Ошибка при решении уравнения: {ex}")
        return None


# Функция генерации уравнений
def generate_equation(num_range, decimal_places, prob_fraction):
    # Загружаем шаблоны
    templates = load_enabled_templates()

    if not templates:
        print("Нет доступных шаблонов!")
        return None, None

    # Выбираем случайный шаблон
    template_data = random.choice(templates)
    template = template_data["template"]
    variables = template_data["variables"]

    # Генерация случайных значений для переменных
    values = {var: generate_random_number(num_range, decimal_places, prob_fraction) for var in variables}

    # Подставляем значения переменных в шаблон
    equation = template.format(**values)
    equation = equation.replace(' - -', ' + ').replace(' + -', ' - ')

    # Проверяем уравнение сразу после генерации
    solution = solve_equation_numeric(equation)

    if solution is not None:
        formatted_equation = format_equation_for_display(equation)
        return formatted_equation, solution

    # Попробуем перегенерировать, если решение не найдено
    attempts = 0
    while solution is None and attempts < 100:
        # Перегенерируем случайные значения
        values = {var: generate_random_number(num_range, decimal_places, prob_fraction) for var in variables}
        equation = template.format(**values)
        equation = equation.replace(' - -', ' + ').replace(' + -', ' - ')

        solution = solve_equation_numeric(equation)
        attempts += 1

    if solution is None:
        return None, None
    else:
        formatted_equation = format_equation_for_display(equation)
        return formatted_equation, solution


# Функция для генерации и записи уравнений в файл Excel
def generate_and_write_to_excel(num_range, decimal_places, num_equations, prob_fraction, max_attempts, file_name, progress_callback=None):
    equations_written = 0

    wb = Workbook()
    ws = wb.active
    ws.append(["Уравнение", "Решение"])

    while equations_written < num_equations:
        equation, solution = generate_equation(num_range, decimal_places, prob_fraction)
        if equation and solution is not None and solution != 0:
            if isinstance(solution, float) and solution.is_integer():
                solution = int(solution)

            ws.append([equation, solution])
            equations_written += 1
            print(f"{equation} | {solution}")

            if progress_callback:
                progress_callback(equations_written, num_equations)
        else:
            print("Не удалось найти решение в 100 попытках для этого уравнения.")

    wb.save(file_name)
    print(f"Записано {equations_written} уравнений в файл {file_name}")

    # Автоматически открыть файл
    try:
        if platform.system() == "Windows":
            os.startfile(file_name)
        elif platform.system() == "Darwin":
            subprocess.run(["open", file_name])
        else:
            subprocess.run(["xdg-open", file_name])
    except Exception as e:
        print("Ошибка при открытии файла:", e)