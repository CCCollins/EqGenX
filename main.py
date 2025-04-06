import threading
import tkinter as tk
from tkinter import messagebox
from modules.generator import generate_and_write_to_excel
from editor import run_editor


def position_window_right(window):
    """Размещает окно в правой части экрана по центру по вертикали."""
    window.update_idletasks()
    width = window.winfo_width() or 300
    height = window.winfo_height() or 350
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = screen_width - width - 100
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_labeled_entry(parent, text, default_value, row):
    """Создает пару Label + Entry в указанной строке."""
    tk.Label(parent, text=text).grid(row=row, column=0, sticky="w")
    entry = tk.Entry(parent)
    entry.insert(tk.END, str(default_value))
    entry.grid(row=row, column=1)
    return entry


def create_gui():
    root = tk.Tk()
    root.title("Генерация уравнений")
    root.geometry("300x220")

    # Поля ввода
    entry_range = create_labeled_entry(root, "Диапазон коэффициентов:", 8, 0)
    entry_decimal_places = create_labeled_entry(root, "Кол-во знаков после запятой:", 1, 1)
    entry_num_equations = create_labeled_entry(root, "Кол-во уравнений:", 20, 2)
    entry_prob_fraction = create_labeled_entry(root, "Вероятность дробных чисел:", 0.5, 3)
    entry_max_attempts = create_labeled_entry(root, "Макс. попыток на решение:", 100, 4)
    entry_file_name = create_labeled_entry(root, "Имя файла:", "equations_solutions.xlsx", 5)

    progress_label = tk.Label(root, text="")
    progress_label.grid(row=6, column=0, columnspan=2, pady=(5, 0))

    def update_progress(done, total):
        progress_label.config(text=f"{done}/{total}")
        root.update_idletasks()

    def open_editor():
        try:
            run_editor()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть редактор:\n{e}")

    def on_generate_click():
        try:
            num_range = int(entry_range.get())
            decimal_places = int(entry_decimal_places.get())
            num_equations = int(entry_num_equations.get())
            prob_fraction = float(entry_prob_fraction.get())
            max_attempts = int(entry_max_attempts.get())
            file_name = entry_file_name.get().strip()

            # Простая валидация
            if num_equations <= 0 or num_range <= 0:
                raise ValueError("Диапазон и количество уравнений должны быть больше нуля.")
            if not file_name.endswith(".xlsx"):
                raise ValueError("Имя файла должно оканчиваться на .xlsx")

            def run_generation():
                generate_and_write_to_excel(
                    num_range, decimal_places, num_equations,
                    prob_fraction, max_attempts, file_name,
                    progress_callback=update_progress
                )

            threading.Thread(target=run_generation, daemon=True).start()

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный ввод: {e}")

    # Кнопки
    button_frame = tk.Frame(root)
    button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))

    tk.Button(button_frame, text="Редактор шаблонов", command=open_editor).pack(side=tk.LEFT, padx=(0, 10))
    tk.Button(button_frame, text="Сгенерировать уравнения", command=on_generate_click).pack(side=tk.LEFT)

    position_window_right(root)
    root.mainloop()


if __name__ == "__main__":
    create_gui()
