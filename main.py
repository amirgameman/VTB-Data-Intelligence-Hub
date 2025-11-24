import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText
import pandas as pd
import numpy as np
from datetime import datetime
import random


class VTBIntelligenceHub:
    def __init__(self, root):
        self.root = root
        self.root.title("ВТБ Data Intelligence Hub 📊")
        self.root.geometry("1400x900")
        self.is_dark_mode = False

        self.df = self.generate_sample_data(100)
        self.filtered_df = self.df.copy()

        self.setup_ui()
        self.update_dashboard()

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
                'last_activity': datetime(2024, random.randint(1, 12), random.randint(1, 28))
            })
        return pd.DataFrame(data)

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.root.style.theme_use("darkly" if self.is_dark_mode else "flatly")
        self.theme_btn.config(text="☀️ Тема" if self.is_dark_mode else "🌙 Тема")
        self.status_var.set("Темная тема включена" if self.is_dark_mode else "Светлая тема включена")

    def setup_ui(self):
        self.main_container = tb.Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = tb.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 10))
        tb.Label(header_frame, text="🎯 ВТБ Data Intelligence Hub", font=('Arial', 16, 'bold')).pack(side=LEFT)
        self.theme_btn = tb.Button(header_frame, text="🌙 Тема", bootstyle="info", command=self.toggle_dark_mode)
        self.theme_btn.pack(side=RIGHT)

        # Filters
        filter_frame = tb.Labelframe(self.main_container, text="🔍 Умные фильтры", padding=10)
        filter_frame.pack(fill=X, pady=(0,10))

        # Row 1 - search + buttons
        row1 = tb.Frame(filter_frame)
        row1.pack(fill=X, pady=5)
        tb.Label(row1, text="Поиск:").pack(side=LEFT)
        self.search_var = tb.StringVar()
        search_entry = tb.Entry(row1, textvariable=self.search_var, width=40)
        search_entry.pack(side=LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self.smart_search)

        tb.Button(row1, text="🎯 AI инсайты", bootstyle="success", command=self.generate_ai_insights).pack(side=LEFT, padx=5)
        tb.Button(row1, text="📈 Прогнозы", bootstyle="primary", command=self.show_predictions).pack(side=LEFT, padx=5)
        tb.Button(row1, text="📋 Данные", bootstyle="secondary", command=self.show_data_table).pack(side=LEFT, padx=5)
        tb.Button(row1, text="🔄 Сброс", bootstyle="warning", command=self.reset_filters).pack(side=LEFT, padx=5)

        # Row 2 - Combobox filters
        row2 = tb.Frame(filter_frame)
        row2.pack(fill=X, pady=5)

        tb.Label(row2, text="Возраст:").pack(side=LEFT)
        self.age_var = tb.StringVar(value="Все")
        age_combo = tb.Combobox(row2, textvariable=self.age_var, values=["Все","18-30","31-45","46-60","60+"], width=10, state="readonly")
        age_combo.pack(side=LEFT, padx=5)
        age_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        tb.Label(row2, text="Регион:").pack(side=LEFT, padx=(20,0))
        self.region_var = tb.StringVar(value="Все")
        region_combo = tb.Combobox(row2, textvariable=self.region_var, values=["Все"] + list(self.df['region'].unique()), width=15, state="readonly")
        region_combo.pack(side=LEFT, padx=5)
        region_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        tb.Label(row2, text="Продукт:").pack(side=LEFT, padx=(20,0))
        self.product_var = tb.StringVar(value="Все")
        product_combo = tb.Combobox(row2, textvariable=self.product_var, values=["Все"] + list(self.df['product'].unique()), width=15, state="readonly")
        product_combo.pack(side=LEFT, padx=5)
        product_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        # Dashboard
        self.dashboard_frame = tb.Frame(self.main_container)
        self.dashboard_frame.pack(fill=BOTH, expand=True)

        # Status bar
        self.status_var = tb.StringVar(value="Готово")
        tb.Label(self.main_container, textvariable=self.status_var, relief=SUNKEN).pack(fill=X, pady=(5,0))

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
            age_ranges = {"18-30":(18,30),"31-45":(31,45),"46-60":(46,60),"60+":(60,75)}
            low, high = age_ranges[self.age_var.get()]
            self.filtered_df = self.filtered_df[self.filtered_df['age'].between(low,high)]
        if self.region_var.get() != "Все":
            self.filtered_df = self.filtered_df[self.filtered_df['region']==self.region_var.get()]
        if self.product_var.get() != "Все":
            self.filtered_df = self.filtered_df[self.filtered_df['product']==self.product_var.get()]
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

    # ----------------- AI Insights -----------------
    def generate_ai_insights(self):
        if len(self.filtered_df)==0:
            tb.messagebox.showwarning("Предупреждение","Нет данных!")
            return
        insights = []
        # Age
        age_groups = pd.cut(self.filtered_df['age'], [18,30,45,60,75], labels=['18-30','31-45','46-60','60+'])
        insights.append(f"👥 Преобладающая возрастная группа: {age_groups.mode()[0]}")
        # Income
        high_income = len(self.filtered_df[self.filtered_df['income']>150000])
        if high_income>0:
            insights.append(f"💎 Клиентов с доходом >150k ₽: {high_income}")
        # Products
        popular_product = self.filtered_df['product'].mode()[0]
        insights.append(f"🏆 Самый популярный продукт: {popular_product}")
        # Regions
        top_region = self.filtered_df['region'].mode()[0]
        insights.append(f"🌍 Наиболее активный регион: {top_region}")
        # Loyalty
        avg_loyalty = self.filtered_df['loyalty_years'].mean()
        insights.append(f"⭐ Средняя лояльность: {avg_loyalty:.1f} лет")
        # Risk
        main_risk = self.filtered_df['risk_level'].mode()[0]
        insights.append(f"⚖️ Преобладающий уровень риска: {main_risk}")
        # Transactions
        avg_transactions = self.filtered_df['transactions'].mean()
        insights.append(f"💳 Среднее количество транзакций: {avg_transactions:.1f}")
        # Balance
        total_balance = self.filtered_df['balance'].sum()
        insights.append(f"💰 Общий баланс клиентов: {total_balance:,.0f} ₽")

        # Show window
        win = tb.Toplevel(self.root)
        win.title("🎯 AI Инсайты")
        win.geometry("700x500")
        tree_frame = tb.Frame(win)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        tree = tb.Treeview(tree_frame, columns=('Insight'), show='tree', height=15)
        tree.column('#0', width=50)
        tree.column('Insight', width=600)
        tree.heading('#0', text='#')
        tree.heading('Insight', text='Инсайт')
        for i, insight in enumerate(insights,1):
            tree.insert('',END,iid=str(i),text=str(i),values=(insight,))
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        tb.Button(win, text="Закрыть", bootstyle="danger", command=win.destroy).pack(pady=10)

    # ----------------- Predictions -----------------
    def show_predictions(self):
        if len(self.filtered_df)==0:
            tb.messagebox.showwarning("Предупреждение","Нет данных для прогнозирования!")
            return
        win = tb.Toplevel(self.root)
        win.title("📈 Прогнозы")
        win.geometry("600x400")
        tb.Label(win, text="📊 Прогнозные данные по клиентам", font=('Arial',14,'bold')).pack(pady=5)
        text_area = ScrolledText(win, width=70, height=20)
        text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)
        for i in range(min(10,len(self.filtered_df))):
            client = self.filtered_df.iloc[i]
            pred_balance = client['balance'] * np.random.uniform(1.02,1.2)
            text_area.insert(END,f"{client['name']} ({client['region']}) - прогноз баланса: {pred_balance:,.0f} ₽\n")
        text_area.config(state=DISABLED)
        tb.Button(win, text="Закрыть", bootstyle="danger", command=win.destroy).pack(pady=10)

    # ----------------- Data Table -----------------
    def show_data_table(self):
        if len(self.filtered_df)==0:
            tb.messagebox.showwarning("Предупреждение","Нет данных для отображения!")
            return
        win = tb.Toplevel(self.root)
        win.title("📋 Данные клиентов")
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
        tb.Button(win, text="Закрыть", bootstyle="danger", command=win.destroy).pack(pady=10)

    # ----------------- Dashboard -----------------
    def update_dashboard(self):
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        if len(self.filtered_df)==0:
            tb.Label(self.dashboard_frame, text="Нет данных для отображения", font=('Arial',14)).pack(expand=True)
            return
        self.create_financial_overview()
        self.create_demographic_analysis()
        self.create_product_analysis()
        self.create_recommendations_panel()

    def create_financial_overview(self):
        frame = tb.Labelframe(self.dashboard_frame, text="💼 Финансовый обзор", padding=10)
        frame.grid(row=0,column=0,padx=5,pady=5,sticky=NSEW)
        total_balance = self.filtered_df['balance'].sum()
        avg_income = self.filtered_df['income'].mean()
        avg_balance = self.filtered_df['balance'].mean()
        high_value_clients = len(self.filtered_df[self.filtered_df['balance']>1000000])
        total_assets = self.filtered_df['assets'].sum()
        total_transactions = self.filtered_df['transactions'].sum()
        metrics = [
            f"💰 Общий баланс: {total_balance:,.0f} ₽",
            f"📊 Средний доход: {avg_income:,.0f} ₽",
            f"💳 Средний баланс: {avg_balance:,.0f} ₽",
            f"⭐ Премиум-клиенты: {high_value_clients}",
            f"🏦 Активы под управлением: {total_assets:,.0f} ₽",
            f"📈 Всего транзакций: {total_transactions}",
            f"👥 Всего клиентов: {len(self.filtered_df)}"
        ]
        for m in metrics:
            tb.Label(frame,text=m,font=('Arial',10)).pack(anchor=W,pady=2)

    def create_demographic_analysis(self):
        frame = tb.Labelframe(self.dashboard_frame, text="👥 Демографический анализ", padding=10)
        frame.grid(row=0,column=1,padx=5,pady=5,sticky=NSEW)
        age_stats = self.filtered_df['age'].describe()
        age_groups = pd.cut(self.filtered_df['age'], [18,30,45,60,75])
        age_distribution = age_groups.value_counts().sort_index()
        region_stats = self.filtered_df['region'].value_counts().head(3)
        metrics = [
            f"📊 Средний возраст: {age_stats['mean']:.1f} лет",
            f"🎯 Медианный возраст: {age_stats['50%']:.1f} лет",
            f"👶 Самый молодой: {age_stats['min']} лет",
            f"👴 Самый старший: {age_stats['max']} лет",
            "\n📈 Распределение по возрастам:"
        ]
        for grp,count in age_distribution.items():
            metrics.append(f"   {grp}: {count} клиентов")
        metrics.append("\n🌍 Топ регионы:")
        for region,count in region_stats.items():
            metrics.append(f"   {region}: {count} клиентов")
        for m in metrics:
            tb.Label(frame,text=m,font=('Arial',9)).pack(anchor=W,pady=1)

    def create_product_analysis(self):
        frame = tb.Labelframe(self.dashboard_frame, text="📊 Анализ продуктов", padding=10)
        frame.grid(row=1,column=0,padx=5,pady=5,sticky=NSEW)
        product_stats = self.filtered_df['product'].value_counts()
        risk_stats = self.filtered_df['risk_level'].value_counts()
        metrics = ["🏆 Распределение по продуктам:"]
        for p,count in product_stats.items():
            metrics.append(f"   {p}: {count} ({count/len(self.filtered_df)*100:.1f}%)")
        metrics.append("\n⚖️ Уровни риска:")
        for r,count in risk_stats.items():
            metrics.append(f"   {r}: {count} ({count/len(self.filtered_df)*100:.1f}%)")
        avg_loyalty = self.filtered_df['loyalty_years'].mean()
        max_loyalty = self.filtered_df['loyalty_years'].max()
        metrics.append(f"\n⭐ Средняя лояльность: {avg_loyalty:.1f} лет")
        metrics.append(f"🎖️ Максимальная лояльность: {max_loyalty} лет")
        for m in metrics:
            tb.Label(frame,text=m,font=('Arial',9)).pack(anchor=W,pady=1)

    def create_recommendations_panel(self):
        frame = tb.Labelframe(self.dashboard_frame, text="🤖 AI Рекомендации", padding=10)
        frame.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')

        recs = self.generate_recommendations()
        text_area = ScrolledText(frame, width=40, height=12, autohide=True)
        text_area.pack(fill='both', expand=True)

        for r in recs:
            text_area.insert('end', f"• {r}\n")

        # Убираем любые строки с state, ScrolledText работает без них

    def generate_recommendations(self):
        recs = []
        if len(self.filtered_df)==0:
            recs.append("Нет данных для анализа")
            return recs
        # High balance clients
        high_balance_clients = self.filtered_df[self.filtered_df['balance']>1000000]
        if len(high_balance_clients)>0:
            recs.append(f"💼 Рассмотреть персонализированные предложения для {len(high_balance_clients)} премиум клиентов")
        # Low activity
        low_activity_clients = self.filtered_df[self.filtered_df['transactions']<5]
        if len(low_activity_clients)>0:
            recs.append(f"📉 Активировать маркетинговую кампанию для {len(low_activity_clients)} малоактивных клиентов")
        # Popular products
        popular_product = self.filtered_df['product'].mode()[0]
        recs.append(f"🏆 Продвигать продукт '{popular_product}' в регионах с высокой концентрацией клиентов")
        # Risk mitigation
        high_risk_clients = self.filtered_df[self.filtered_df['risk_level']=='Высокий']
        if len(high_risk_clients)>0:
            recs.append(f"⚖️ Мониторинг рисков для {len(high_risk_clients)} клиентов с высоким риском")
        return recs


if __name__ == "__main__":
    root = tb.Window(themename="flatly")
    app = VTBIntelligenceHub(root)
    root.mainloop()
