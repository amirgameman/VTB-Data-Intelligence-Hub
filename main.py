import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText
import pandas as pd
import numpy as np
from datetime import datetime
import random
import os
import sys

# Попытка импорта matplotlib с обработкой ошибок
try:
    import matplotlib

    matplotlib.use('Agg')  # Используем бэкенд без GUI для избежания конфликтов
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"Matplotlib не доступен: {e}")
    MATPLOTLIB_AVAILABLE = False
except Exception as e:
    print(f"Ошибка при импорте matplotlib: {e}")
    MATPLOTLIB_AVAILABLE = False


class VTBIntelligenceHub:
    def __init__(self, root):
        self.root = root
        self.root.title("ВТБ Data Intelligence Hub")
        self.root.geometry("1400x900")
        self.is_dark_mode = False

        # Загрузка данных
        self.df = self.load_or_generate_data()
        self.filtered_df = self.df.copy()

        self.setup_ui()
        self.update_dashboard()

    def load_or_generate_data(self):
        """Загружает данные из CSV или генерирует новые"""
        csv_file = "data/clients_data.csv"

        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                print(f"Данные загружены из {csv_file}")
                return df
            except Exception as e:
                print(f"Ошибка загрузки CSV: {e}. Генерирую новые данные.")

        # Генерация новых данных
        df = self.generate_sample_data(100)
        # Создаем папку data если её нет
        os.makedirs("data", exist_ok=True)
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"Новые данные сохранены в {csv_file}")
        return df

    def generate_sample_data(self, n=100):
        np.random.seed(42)
        random.seed(42)

        regions = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 'Нижний Новгород']
        products = ['Кредит', 'Вклад', 'Инвестиции', 'Ипотека', 'Страхование', 'Дебетовая карта']

        data = []
        for i in range(n):
            age = int(np.clip(np.random.normal(45, 15), 18, 75))
            income = int(np.clip(np.random.lognormal(11, 0.5), 20000, 500000))
            balance = max(5000, int(income * np.random.uniform(0.5, 12)))
            data.append({
                'id': i + 1,
                'name': f'Клиент_{i + 1}',
                'age': age,
                'region': random.choice(regions),
                'income': income,
                'balance': balance,
                'assets': balance * np.random.uniform(0.5, 3),
                'transactions': np.random.poisson(15),
                'product': random.choice(products),
                'loyalty_years': np.random.randint(0, 25),
                'risk_level': random.choices(['Низкий', 'Средний', 'Высокий'], weights=[0.6, 0.3, 0.1])[0],
                'last_activity': datetime(2024, random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d')
            })
        return pd.DataFrame(data)

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.root.style.theme_use("darkly" if self.is_dark_mode else "flatly")
        self.theme_btn.config(text="Светлая тема" if self.is_dark_mode else "Темная тема")
        self.status_var.set("Темная тема включена" if self.is_dark_mode else "Светлая тема включена")

    def setup_ui(self):
        self.main_container = tb.Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = tb.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 10))
        tb.Label(header_frame, text="ВТБ Data Intelligence Hub", font=('Arial', 16, 'bold')).pack(side=LEFT)
        self.theme_btn = tb.Button(header_frame, text="Темная тема", bootstyle="info", command=self.toggle_dark_mode)
        self.theme_btn.pack(side=RIGHT)

        # Filters
        filter_frame = tb.Labelframe(self.main_container, text="Умные фильтры", padding=10)
        filter_frame.pack(fill=X, pady=(0, 10))

        # Row 1 - search + buttons
        row1 = tb.Frame(filter_frame)
        row1.pack(fill=X, pady=5)
        tb.Label(row1, text="Поиск:").pack(side=LEFT)
        self.search_var = tb.StringVar()
        search_entry = tb.Entry(row1, textvariable=self.search_var, width=40)
        search_entry.pack(side=LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self.smart_search)

        tb.Button(row1, text="AI инсайты", bootstyle="success", command=self.generate_ai_insights).pack(side=LEFT,
                                                                                                        padx=5)
        tb.Button(row1, text="Прогнозы", bootstyle="primary", command=self.show_predictions).pack(side=LEFT, padx=5)

        # Кнопка графиков только если matplotlib доступен
        if MATPLOTLIB_AVAILABLE:
            tb.Button(row1, text="Графики", bootstyle="info", command=self.show_charts).pack(side=LEFT, padx=5)
        else:
            tb.Button(row1, text="Графики (недоступно)", bootstyle="secondary",
                      command=lambda: tb.messagebox.showwarning("Внимание", "Matplotlib не установлен")).pack(side=LEFT,
                                                                                                              padx=5)

        tb.Button(row1, text="Данные", bootstyle="secondary", command=self.show_data_table).pack(side=LEFT, padx=5)
        tb.Button(row1, text="Сброс", bootstyle="warning", command=self.reset_filters).pack(side=LEFT, padx=5)

        # Row 2 - Combobox filters
        row2 = tb.Frame(filter_frame)
        row2.pack(fill=X, pady=5)

        tb.Label(row2, text="Возраст:").pack(side=LEFT)
        self.age_var = tb.StringVar(value="Все")
        age_combo = tb.Combobox(row2, textvariable=self.age_var, values=["Все", "18-30", "31-45", "46-60", "60+"],
                                width=10, state="readonly")
        age_combo.pack(side=LEFT, padx=5)
        age_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        tb.Label(row2, text="Регион:").pack(side=LEFT, padx=(20, 0))
        self.region_var = tb.StringVar(value="Все")
        region_combo = tb.Combobox(row2, textvariable=self.region_var,
                                   values=["Все"] + list(self.df['region'].unique()), width=15, state="readonly")
        region_combo.pack(side=LEFT, padx=5)
        region_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        tb.Label(row2, text="Продукт:").pack(side=LEFT, padx=(20, 0))
        self.product_var = tb.StringVar(value="Все")
        product_combo = tb.Combobox(row2, textvariable=self.product_var,
                                    values=["Все"] + list(self.df['product'].unique()), width=15, state="readonly")
        product_combo.pack(side=LEFT, padx=5)
        product_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        # Dashboard
        self.dashboard_frame = tb.Frame(self.main_container)
        self.dashboard_frame.pack(fill=BOTH, expand=True)

        # Status bar
        self.status_var = tb.StringVar(value="Готово")
        if not MATPLOTLIB_AVAILABLE:
            self.status_var.set("Готово (Matplotlib не доступен)")
        tb.Label(self.main_container, textvariable=self.status_var, relief=SUNKEN).pack(fill=X, pady=(5, 0))

    def smart_search(self, event=None):
        query = self.search_var.get().lower()
        if query:
            mask = (self.df['name'].str.lower().str.contains(query) |
                    self.df['region'].str.lower().str.contains(query) |
                    self.df['product'].str.lower().str.contains(query) |
                    self.df['risk_level'].str.lower().str.contains(query))
            self.filtered_df = self.df[mask]
        else:
            self.filtered_df = self.df.copy()
        self.update_dashboard()
        self.status_var.set(f"Найдено клиентов: {len(self.filtered_df)}")

    def apply_filters(self, event=None):
        self.filtered_df = self.df.copy()
        if self.age_var.get() != "Все":
            age_ranges = {"18-30": (18, 30), "31-45": (31, 45), "46-60": (46, 60), "60+": (60, 75)}
            low, high = age_ranges[self.age_var.get()]
            self.filtered_df = self.filtered_df[self.filtered_df['age'].between(low, high)]
        if self.region_var.get() != "Все":
            self.filtered_df = self.filtered_df[self.filtered_df['region'] == self.region_var.get()]
        if self.product_var.get() != "Все":
            self.filtered_df = self.filtered_df[self.filtered_df['product'] == self.product_var.get()]
        self.update_dashboard()
        self.status_var.set(f"Отфильтровано клиентов: {len(self.filtered_df)}")

    def reset_filters(self):
        self.search_var.set("")
        self.age_var.set("Все")
        self.region_var.set("Все")
        self.product_var.set("Все")
        self.filtered_df = self.df.copy()
        self.update_dashboard()
        self.status_var.set("Фильтры сброшены")

    def generate_ai_insights(self):
        if len(self.filtered_df) == 0:
            tb.messagebox.showwarning("Предупреждение", "Нет данных!")
            return

        insights = []
        # Age
        age_groups = pd.cut(self.filtered_df['age'], [18, 30, 45, 60, 75], labels=['18-30', '31-45', '46-60', '60+'])
        insights.append(f"Преобладающая возрастная группа: {age_groups.mode()[0]}")
        # Income
        high_income = len(self.filtered_df[self.filtered_df['income'] > 150000])
        if high_income > 0:
            insights.append(f"Клиентов с доходом >150k ₽: {high_income}")
        # Products
        popular_product = self.filtered_df['product'].mode()[0]
        insights.append(f"Самый популярный продукт: {popular_product}")
        # Regions
        top_region = self.filtered_df['region'].mode()[0]
        insights.append(f"Наиболее активный регион: {top_region}")
        # Loyalty
        avg_loyalty = self.filtered_df['loyalty_years'].mean()
        insights.append(f"Средняя лояльность: {avg_loyalty:.1f} лет")
        # Risk
        main_risk = self.filtered_df['risk_level'].mode()[0]
        insights.append(f"Преобладающий уровень риска: {main_risk}")
        # Transactions
        avg_transactions = self.filtered_df['transactions'].mean()
        insights.append(f"Среднее количество транзакций: {avg_transactions:.1f}")
        # Balance
        total_balance = self.filtered_df['balance'].sum()
        insights.append(f"Общий баланс клиентов: {total_balance:,.0f} ₽")

        # Show window
        win = tb.Toplevel(self.root)
        win.title("AI Инсайты")
        win.geometry("700x500")
        tree_frame = tb.Frame(win)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        tree = tb.Treeview(tree_frame, columns=('Insight'), show='tree', height=15)
        tree.column('#0', width=50)
        tree.column('Insight', width=600)
        tree.heading('#0', text='#')
        tree.heading('Insight', text='Инсайт')
        for i, insight in enumerate(insights, 1):
            tree.insert('', END, iid=str(i), text=str(i), values=(insight,))
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        tb.Button(win, text="Закрыть", bootstyle="danger", command=win.destroy).pack(pady=10)

    def show_predictions(self):
        if len(self.filtered_df) == 0:
            tb.messagebox.showwarning("Предупреждение", "Нет данных для прогнозирования!")
            return

        win = tb.Toplevel(self.root)
        win.title("Прогнозы")
        win.geometry("600x400")
        tb.Label(win, text="Прогнозные данные по клиентам", font=('Arial', 14, 'bold')).pack(pady=5)
        text_area = ScrolledText(win, width=70, height=20)
        text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)

        for i in range(min(10, len(self.filtered_df))):
            client = self.filtered_df.iloc[i]
            pred_balance = client['balance'] * np.random.uniform(1.02, 1.2)
            text_area.insert(END, f"{client['name']} ({client['region']}) - прогноз баланса: {pred_balance:,.0f} ₽\n")

        text_area.config(state=DISABLED)
        tb.Button(win, text="Закрыть", bootstyle="danger", command=win.destroy).pack(pady=10)

    def show_charts(self):
        """Показывает окно с графиками"""
        if not MATPLOTLIB_AVAILABLE:
            tb.messagebox.showerror("Ошибка", "Matplotlib не установлен или не доступен")
            return

        if len(self.filtered_df) == 0:
            tb.messagebox.showwarning("Предупреждение", "Нет данных для построения графиков!")
            return

        win = tb.Toplevel(self.root)
        win.title("Аналитические графики")
        win.geometry("1000x700")

        # Создаем notebook для вкладок
        notebook = tb.Notebook(win)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        try:
            # График 1: Распределение по продуктам
            frame1 = tb.Frame(notebook)
            notebook.add(frame1, text="Распределение по продуктам")

            fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Круговая диаграмма продуктов
            product_counts = self.filtered_df['product'].value_counts()
            ax1.pie(product_counts.values, labels=product_counts.index, autopct='%1.1f%%')
            ax1.set_title('Распределение клиентов по продуктам')

            # Столбчатая диаграмма регионов
            region_counts = self.filtered_df['region'].value_counts().head(5)
            ax2.bar(region_counts.index, region_counts.values)
            ax2.set_title('Топ-5 регионов по количеству клиентов')
            ax2.tick_params(axis='x', rotation=45)

            plt.tight_layout()
            canvas1 = FigureCanvasTkAgg(fig1, frame1)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=BOTH, expand=True)

            # График 2: Финансовые показатели
            frame2 = tb.Frame(notebook)
            notebook.add(frame2, text="Финансовые показатели")

            fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 5))

            # Распределение доходов
            ax3.hist(self.filtered_df['income'], bins=20, alpha=0.7, edgecolor='black')
            ax3.set_title('Распределение доходов клиентов')
            ax3.set_xlabel('Доход (руб)')
            ax3.set_ylabel('Количество клиентов')

            # Распределение балансов
            ax4.hist(self.filtered_df['balance'], bins=20, alpha=0.7, edgecolor='black', color='orange')
            ax4.set_title('Распределение балансов клиентов')
            ax4.set_xlabel('Баланс (руб)')
            ax4.set_ylabel('Количество клиентов')

            plt.tight_layout()
            canvas2 = FigureCanvasTkAgg(fig2, frame2)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=BOTH, expand=True)

            # График 3: Демографический анализ
            frame3 = tb.Frame(notebook)
            notebook.add(frame3, text="Демографический анализ")

            fig3, (ax5, ax6) = plt.subplots(1, 2, figsize=(12, 5))

            # Распределение по возрастам
            age_bins = [18, 25, 35, 45, 55, 65, 75]
            age_labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '66-75']
            age_groups = pd.cut(self.filtered_df['age'], bins=age_bins, labels=age_labels)
            age_counts = age_groups.value_counts().sort_index()

            ax5.bar(age_counts.index, age_counts.values, color='green', alpha=0.7)
            ax5.set_title('Распределение клиентов по возрастам')
            ax5.set_xlabel('Возрастные группы')
            ax5.set_ylabel('Количество клиентов')
            ax5.tick_params(axis='x', rotation=45)

            # Уровни риска
            risk_counts = self.filtered_df['risk_level'].value_counts()
            ax6.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%',
                    colors=['lightgreen', 'yellow', 'red'])
            ax6.set_title('Распределение по уровням риска')

            plt.tight_layout()
            canvas3 = FigureCanvasTkAgg(fig3, frame3)
            canvas3.draw()
            canvas3.get_tk_widget().pack(fill=BOTH, expand=True)

        except Exception as e:
            tb.messagebox.showerror("Ошибка", f"Ошибка при построении графиков: {e}")
            win.destroy()
            return

        tb.Button(win, text="Закрыть", bootstyle="danger", command=win.destroy).pack(pady=10)

    def show_data_table(self):
        if len(self.filtered_df) == 0:
            tb.messagebox.showwarning("Предупреждение", "Нет данных для отображения!")
            return

        win = tb.Toplevel(self.root)
        win.title("Данные клиентов")
        win.geometry("1000x600")

        tree_frame = tb.Frame(win)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        columns = list(self.filtered_df.columns)
        tree = tb.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=CENTER)

        for _, row in self.filtered_df.iterrows():
            tree.insert('', END, values=list(row))

        tree.pack(side=LEFT, fill=BOTH, expand=True)

        vsb = tb.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=RIGHT, fill=Y)

        tb.Button(win, text="Экспорт в CSV", bootstyle="success",
                  command=lambda: self.export_to_csv()).pack(side=LEFT, padx=10, pady=10)
        tb.Button(win, text="Закрыть", bootstyle="danger", command=win.destroy).pack(side=RIGHT, padx=10, pady=10)

    def export_to_csv(self):
        """Экспортирует отфильтрованные данные в CSV"""
        filename = f"exported_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.filtered_df.to_csv(filename, index=False, encoding='utf-8')
        self.status_var.set(f"Данные экспортированы в {filename}")
        tb.messagebox.showinfo("Экспорт", f"Данные успешно экспортированы в {filename}")

    def update_dashboard(self):
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()

        if len(self.filtered_df) == 0:
            tb.Label(self.dashboard_frame, text="Нет данных для отображения", font=('Arial', 14)).pack(expand=True)
            return

        self.create_financial_overview()
        self.create_demographic_analysis()
        self.create_product_analysis()
        self.create_recommendations_panel()

    def create_financial_overview(self):
        frame = tb.Labelframe(self.dashboard_frame, text="Финансовый обзор", padding=10)
        frame.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW)

        total_balance = self.filtered_df['balance'].sum()
        avg_income = self.filtered_df['income'].mean()
        avg_balance = self.filtered_df['balance'].mean()
        high_value_clients = len(self.filtered_df[self.filtered_df['balance'] > 1000000])
        total_assets = self.filtered_df['assets'].sum()
        total_transactions = self.filtered_df['transactions'].sum()

        metrics = [
            f"Общий баланс: {total_balance:,.0f} ₽",
            f"Средний доход: {avg_income:,.0f} ₽",
            f"Средний баланс: {avg_balance:,.0f} ₽",
            f"Премиум-клиенты: {high_value_clients}",
            f"Активы под управлением: {total_assets:,.0f} ₽",
            f"Всего транзакций: {total_transactions}",
            f"Всего клиентов: {len(self.filtered_df)}"
        ]

        for m in metrics:
            tb.Label(frame, text=m, font=('Arial', 10)).pack(anchor=W, pady=2)

    def create_demographic_analysis(self):
        frame = tb.Labelframe(self.dashboard_frame, text="Демографический анализ", padding=10)
        frame.grid(row=0, column=1, padx=5, pady=5, sticky=NSEW)

        age_stats = self.filtered_df['age'].describe()
        age_groups = pd.cut(self.filtered_df['age'], [18, 30, 45, 60, 75])
        age_distribution = age_groups.value_counts().sort_index()
        region_stats = self.filtered_df['region'].value_counts().head(3)

        metrics = [
            f"Средний возраст: {age_stats['mean']:.1f} лет",
            f"Медианный возраст: {age_stats['50%']:.1f} лет",
            f"Самый молодой: {age_stats['min']} лет",
            f"Самый старший: {age_stats['max']} лет",
            "\nРаспределение по возрастам:"
        ]

        for grp, count in age_distribution.items():
            metrics.append(f"   {grp}: {count} клиентов")

        metrics.append("\nТоп регионы:")
        for region, count in region_stats.items():
            metrics.append(f"   {region}: {count} клиентов")

        for m in metrics:
            tb.Label(frame, text=m, font=('Arial', 9)).pack(anchor=W, pady=1)

    def create_product_analysis(self):
        frame = tb.Labelframe(self.dashboard_frame, text="Анализ продуктов", padding=10)
        frame.grid(row=1, column=0, padx=5, pady=5, sticky=NSEW)

        product_stats = self.filtered_df['product'].value_counts()
        risk_stats = self.filtered_df['risk_level'].value_counts()

        metrics = ["Распределение по продуктам:"]
        for p, count in product_stats.items():
            metrics.append(f"   {p}: {count} ({count / len(self.filtered_df) * 100:.1f}%)")

        metrics.append("\nУровни риска:")
        for r, count in risk_stats.items():
            metrics.append(f"   {r}: {count} ({count / len(self.filtered_df) * 100:.1f}%)")

        avg_loyalty = self.filtered_df['loyalty_years'].mean()
        max_loyalty = self.filtered_df['loyalty_years'].max()
        metrics.append(f"\nСредняя лояльность: {avg_loyalty:.1f} лет")
        metrics.append(f"Максимальная лояльность: {max_loyalty} лет")

        for m in metrics:
            tb.Label(frame, text=m, font=('Arial', 9)).pack(anchor=W, pady=1)

    def create_recommendations_panel(self):
        frame = tb.Labelframe(self.dashboard_frame, text="AI Рекомендации", padding=10)
        frame.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')

        recs = self.generate_recommendations()
        text_area = ScrolledText(frame, width=40, height=12, autohide=True)
        text_area.pack(fill='both', expand=True)

        for r in recs:
            text_area.insert('end', f"• {r}\n")

    def generate_recommendations(self):
        recs = []
        if len(self.filtered_df) == 0:
            recs.append("Нет данных для анализа")
            return recs

        high_balance_clients = self.filtered_df[self.filtered_df['balance'] > 1000000]
        if len(high_balance_clients) > 0:
            recs.append(f"Рассмотреть персонализированные предложения для {len(high_balance_clients)} премиум клиентов")

        low_activity_clients = self.filtered_df[self.filtered_df['transactions'] < 5]
        if len(low_activity_clients) > 0:
            recs.append(f"Активировать маркетинговую кампанию для {len(low_activity_clients)} малоактивных клиентов")

        popular_product = self.filtered_df['product'].mode()[0]
        recs.append(f"Продвигать продукт '{popular_product}' в регионах с высокой концентрацией клиентов")

        high_risk_clients = self.filtered_df[self.filtered_df['risk_level'] == 'Высокий']
        if len(high_risk_clients) > 0:
            recs.append(f"Мониторинг рисков для {len(high_risk_clients)} клиентов с высоким риском")

        return recs


if __name__ == "__main__":
    root = tb.Window(themename="flatly")
    app = VTBIntelligenceHub(root)
    root.mainloop()