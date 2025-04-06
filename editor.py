import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os

TASKS_FILE = "tasks.json"


class EquationEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор шаблонов уравнений")
        self.equations = []

        # Основной фрейм и холст для прокрутки
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.pack(fill="both", expand=True)

        self.load_tasks()  # Загружаем задачи при инициализации
        self.render_list()

        # Привязка события прокрутки колесика мыши
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Добавить шаблон", command=self.add_template).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сохранить", command=self.save_tasks).pack(side=tk.LEFT, padx=5)

    def load_tasks(self):
        """Загружает задачи из файла tasks.json, если он существует."""
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    self.equations = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить шаблоны:\n{e}")
                self.equations = []
        else:
            self.equations = []

    def save_tasks(self):
        """Сохраняет задачи в файл tasks.json."""
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.equations, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить шаблоны:\n{e}")

    def render_list(self):
        """Отображает список шаблонов уравнений."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for idx, eq in enumerate(self.equations):
            self.render_equation(eq, idx)

        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def render_equation(self, eq, idx):
        """Отображает отдельный шаблон уравнения."""
        row = tk.Frame(self.scrollable_frame)
        row.pack(fill="x", pady=2)

        var_enabled = tk.BooleanVar(value=eq.get("enabled", True))
        chk = tk.Checkbutton(row, variable=var_enabled,
                             command=lambda i=idx, v=var_enabled: self.update_enabled(i, v))
        chk.pack(side=tk.LEFT)

        lbl = tk.Label(row, text=eq["template"], anchor="w")
        lbl.pack(side=tk.LEFT, fill="x", expand=True)

        btn_delete = tk.Button(row, text="🗑", command=lambda: self.delete_equation(idx))
        btn_delete.pack(side=tk.RIGHT)

        btn_edit = tk.Button(row, text="Редактировать", command=lambda: self.edit_equation(idx))
        btn_edit.pack(side=tk.RIGHT, padx=5)

    def update_enabled(self, idx, var):
        """Обновляет состояние 'enabled'."""
        self.equations[idx]["enabled"] = var.get()

    def delete_equation(self, idx):
        """Удаляет шаблон уравнения по индексу."""
        del self.equations[idx]
        self.render_list()

    def add_template(self):
        """Добавляет новый шаблон уравнения."""
        new_template = simpledialog.askstring("Новый шаблон", "Введите шаблон, например:\n{a}*x + {b} = {c}*x + {d}")
        if new_template:
            self.equations.append({
                "template": new_template,
                "enabled": True
            })
            self.render_list()

    def edit_equation(self, idx):
        """Редактирует шаблон уравнения по индексу."""
        new_template = simpledialog.askstring("Редактирование шаблона", "Введите новый шаблон:",
                                              initialvalue=self.equations[idx]["template"])
        if new_template:
            self.equations[idx]["template"] = new_template
            self.render_list()

    def on_mouse_wheel(self, event):
        """Обработчик прокрутки колесика мыши."""
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")


def run_editor():
    """Запускает редактор шаблонов уравнений."""
    try:
        root = tk.Toplevel()
    except:
        root = tk.Tk()

    editor = EquationEditor(root)
    root.geometry("380x520")
    root.mainloop()
