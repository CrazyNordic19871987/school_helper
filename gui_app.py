import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
from datetime import datetime
from knowledge_base import get_topics_by_keywords, get_task_for_topic, get_topic_description
from student_progress import StudentProgress
from analytics import Analytics

class SchoolHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 ИИ-Помощник для Школьника")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f8ff')
        
        # Стили
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f8ff')
        self.style.configure('TLabel', background='#f0f8ff', font=('Arial', 10))
        self.style.configure('Title.TLabel', background='#4CAF50', foreground='white', font=('Arial', 14, 'bold'))
        self.style.configure('Custom.TButton', font=('Arial', 10), background='#2196F3')
        
        self.setup_ui()
        self.current_student = None
        self.progress_manager = None
        self.analytics = None
    
    def setup_ui(self):
        """Создает интерфейс приложения"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🎓 ИИ-ПОМОЩНИК ДЛЯ ШКОЛЬНИКА", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20), fill=tk.X)
        
        # Фрейм для ввода имени
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(name_frame, text="Введите ваше имя:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(name_frame, font=('Arial', 12), width=20)
        self.name_entry.pack(side=tk.LEFT, padx=10)
        self.name_entry.bind('<Return>', lambda e: self.start_session())
        
        ttk.Button(name_frame, text="Начать", command=self.start_session, 
                  style='Custom.TButton').pack(side=tk.LEFT, padx=5)
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Вкладка анализа работы
        self.setup_analysis_tab()
        
        # Вкладка тренировки
        self.setup_practice_tab()
        
        # Вкладка статистики
        self.setup_stats_tab()
        
        # Вкладка плана занятий
        self.setup_plan_tab()
        
        # Изначально отключаем вкладки до ввода имени
        self.disable_tabs()
    
    def setup_analysis_tab(self):
        """Создает вкладку анализа работы"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="📝 Анализ работы")
        
        # Текстовая область для ввода работы
        ttk.Label(analysis_frame, text="Введите текст вашей работы:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        self.work_text = scrolledtext.ScrolledText(analysis_frame, height=10, 
                                                  font=('Arial', 10), wrap=tk.WORD)
        self.work_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Загрузить демо-текст", 
                  command=self.load_demo_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Проанализировать", 
                  command=self.analyze_work, style='Custom.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", 
                  command=self.clear_text).pack(side=tk.LEFT, padx=5)
        
        # Область для результатов
        ttk.Label(analysis_frame, text="Результаты анализа:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(20, 5))
        
        self.results_text = scrolledtext.ScrolledText(analysis_frame, height=8, 
                                                     font=('Arial', 10), wrap=tk.WORD,
                                                     state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_practice_tab(self):
        """Создает вкладку тренировки"""
        practice_frame = ttk.Frame(self.notebook)
        self.notebook.add(practice_frame, text="📚 Тренировка")
        
        # Список слабых тем
        ttk.Label(practice_frame, text="Слабые темы для тренировки:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        self.topics_listbox = tk.Listbox(practice_frame, font=('Arial', 10), height=6)
        self.topics_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопки выбора темы
        topics_button_frame = ttk.Frame(practice_frame)
        topics_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(topics_button_frame, text="Выбрать тему", 
                  command=self.select_topic).pack(side=tk.LEFT, padx=5)
        ttk.Button(topics_button_frame, text="Случайная тема", 
                  command=self.random_topic).pack(side=tk.LEFT, padx=5)
        ttk.Button(topics_button_frame, text="Обновить список", 
                  command=self.update_topics_list).pack(side=tk.LEFT, padx=5)
        
        # Область для задания
        ttk.Label(practice_frame, text="Задание:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(20, 5))
        
        self.task_text = scrolledtext.ScrolledText(practice_frame, height=6, 
                                                  font=('Arial', 10), wrap=tk.WORD,
                                                  state=tk.DISABLED)
        self.task_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Оценка выполнения
        eval_frame = ttk.Frame(practice_frame)
        eval_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(eval_frame, text="Оцените выполнение:", 
                 font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        
        self.eval_var = tk.StringVar(value="2")
        ttk.Radiobutton(eval_frame, text="✅ Легко", variable=self.eval_var, 
                       value="1").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(eval_frame, text="🤔 Трудно", variable=self.eval_var, 
                       value="2").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(eval_frame, text="❌ Не смог", variable=self.eval_var, 
                       value="3").pack(side=tk.LEFT, padx=10)
        
        ttk.Button(eval_frame, text="Отправить оценку", 
                  command=self.submit_evaluation).pack(side=tk.LEFT, padx=20)
    
    def setup_stats_tab(self):
        """Создает вкладку статистики"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📈 Статистика")
        
        # Общая статистика
        stats_header = ttk.Label(stats_frame, text="Общая статистика", 
                                font=('Arial', 12, 'bold'))
        stats_header.pack(pady=10)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=12, 
                                                   font=('Arial', 10), wrap=tk.WORD,
                                                   state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Кнопка обновления
        ttk.Button(stats_frame, text="Обновить статистику", 
                  command=self.update_stats).pack(pady=10)
    
    def setup_plan_tab(self):
        """Создает вкладку плана занятий"""
        plan_frame = ttk.Frame(self.notebook)
        self.notebook.add(plan_frame, text="🎯 План занятий")
        
        ttk.Label(plan_frame, text="Индивидуальный план на неделю:", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.plan_text = scrolledtext.ScrolledText(plan_frame, height=15, 
                                                  font=('Arial', 10), wrap=tk.WORD,
                                                  state=tk.DISABLED)
        self.plan_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Button(plan_frame, text="Сгенерировать план", 
                  command=self.generate_plan).pack(pady=10)
    
    def disable_tabs(self):
        """Отключает вкладки до ввода имени"""
        for i in range(1, 4):  # Вкладки 1, 2, 3 (индексы 1, 2, 3)
            self.notebook.tab(i, state="disabled")
    
    def enable_tabs(self):
        """Включает все вкладки"""
        for i in range(4):  # Все 4 вкладки
            self.notebook.tab(i, state="normal")
    
    def start_session(self):
        """Начинает сессию для ученика"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Пожалуйста, введите ваше имя!")
            return
        
        self.current_student = name
        self.progress_manager = StudentProgress(name)
        self.analytics = Analytics(self.progress_manager)
        
        # Включаем вкладки
        self.enable_tabs()
        
        # Обновляем интерфейс
        self.update_topics_list()
        self.update_stats()
        self.generate_plan()
        
        messagebox.showinfo("Успех", f"Добро пожаловать, {name}! Сессия начата.")
    
    def load_demo_text(self):
        """Загружает демо-текст для анализа"""
        demo_text = """В контрольной по математике я ошибся в задаче на дроби. 
Не смог правильно сократить дробь 12/18, написал что ответ 6/9. 
Также были проблемы с нахождением периметра прямоугольника, перепутал формулу.
В русском языке постоянно ошибаюсь в правописании -тся и -ться."""
        
        self.work_text.delete(1.0, tk.END)
        self.work_text.insert(1.0, demo_text)
    
    def clear_text(self):
        """Очищает текстовые поля"""
        self.work_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def analyze_work(self):
        """Анализирует работу ученика"""
        if not self.current_student:
            messagebox.showwarning("Внимание", "Сначала введите ваше имя!")
            return
        
        work_text = self.work_text.get(1.0, tk.END).strip()
        if not work_text:
            messagebox.showwarning("Внимание", "Введите текст работы для анализа!")
            return
        
        try:
            # Сохраняем работу
            success = self.progress_manager.save_student_work(work_text)
            if not success:
                messagebox.showwarning("Внимание", "Не удалось сохранить работу, но анализ продолжается...")
            
            # Анализируем
            found_topics = get_topics_by_keywords(work_text)
            recommended_tasks = {}
            
            for topic in found_topics:
                difficulty = self.progress_manager.progress_data["topics"].get(topic, {}).get("difficulty_level", "medium")
                task = get_task_for_topic(topic, difficulty)
                if task:
                    recommended_tasks[topic] = task
            
            # Сохраняем сессию
            self.progress_manager.add_session(work_text, found_topics, recommended_tasks)
            
            # Показываем результаты
            self.show_results(found_topics, recommended_tasks)
            
            # Обновляем другие вкладки
            self.update_topics_list()
            self.update_stats()
            self.generate_plan()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при анализе: {str(e)}")
    
    def show_results(self, found_topics, recommended_tasks):
        """Показывает результаты анализа"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        if found_topics:
            self.results_text.insert(tk.END, "🔍 НАЙДЕНЫ ТЕМЫ ДЛЯ УЛУЧШЕНИЯ:\n\n")
            
            for topic in found_topics:
                self.results_text.insert(tk.END, f"📖 {topic}\n")
                self.results_text.insert(tk.END, f"   Описание: {get_topic_description(topic)}\n\n")
            
            self.results_text.insert(tk.END, "🎯 РЕКОМЕНДУЕМЫЕ ЗАДАНИЯ:\n\n")
            
            for topic, task in recommended_tasks.items():
                self.results_text.insert(tk.END, f"📝 {topic}:\n")
                self.results_text.insert(tk.END, f"   {task}\n\n")
        else:
            self.results_text.insert(tk.END, "✅ Отличная работа! Проблемных тем не обнаружено.")
        
        self.results_text.config(state=tk.DISABLED)
    
    def update_topics_list(self):
        """Обновляет список слабых тем"""
        if not self.current_student:
            return
        
        self.topics_listbox.delete(0, tk.END)
        weak_topics = self.progress_manager.get_weak_topics()
        
        if not weak_topics:
            self.topics_listbox.insert(tk.END, "🎉 Нет слабых тем для тренировки!")
            return
        
        for topic in weak_topics:
            topic_data = self.progress_manager.progress_data["topics"][topic]
            display_text = f"{topic} (mastery: {topic_data['mastery_score']:.1f}%)"
            self.topics_listbox.insert(tk.END, display_text)
    
    def select_topic(self):
        """Выбирает тему для тренировки из списка"""
        selection = self.topics_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите тему из списка!")
            return
        
        weak_topics = self.progress_manager.get_weak_topics()
        if not weak_topics:
            return
        
        selected_topic = weak_topics[selection[0]]
        self.show_task(selected_topic)
    
    def random_topic(self):
        """Выбирает случайную тему для тренировки"""
        weak_topics = self.progress_manager.get_weak_topics()
        if not weak_topics:
            messagebox.showinfo("Информация", "Нет слабых тем для тренировки!")
            return
        
        import random
        selected_topic = random.choice(weak_topics)
        self.show_task(selected_topic)
    
    def show_task(self, topic):
        """Показывает задание по выбранной теме"""
        difficulty = self.progress_manager.progress_data["topics"][topic]["difficulty_level"]
        task = get_task_for_topic(topic, difficulty)
        
        self.current_topic = topic
        
        self.task_text.config(state=tk.NORMAL)
        self.task_text.delete(1.0, tk.END)
        
        if task:
            self.task_text.insert(tk.END, f"📖 Тема: {topic}\n")
            self.task_text.insert(tk.END, f"📝 Описание: {get_topic_description(topic)}\n")
            self.task_text.insert(tk.END, f"🎯 Уровень сложности: {difficulty}\n\n")
            self.task_text.insert(tk.END, "ЗАДАНИЕ:\n")
            self.task_text.insert(tk.END, f"{task}")
        else:
            self.task_text.insert(tk.END, "Задание не найдено.")
        
        self.task_text.config(state=tk.DISABLED)
    
    def submit_evaluation(self):
        """Отправляет оценку выполнения задания"""
        if not hasattr(self, 'current_topic'):
            messagebox.showwarning("Внимание", "Сначала выберите тему и получите задание!")
            return
        
        rating = self.eval_var.get()
        if rating == "1":
            success_rate = 90
        elif rating == "2":
            success_rate = 60
        else:
            success_rate = 30
        
        self.progress_manager.update_mastery(self.current_topic, success_rate)
        
        messagebox.showinfo("Успех", 
                          f"Mastery темы '{self.current_topic}' обновлен: "
                          f"{self.progress_manager.progress_data['topics'][self.current_topic]['mastery_score']:.1f}%")
        
        # Обновляем интерфейс
        self.update_topics_list()
        self.update_stats()
        self.generate_plan()
    
    def update_stats(self):
        """Обновляет статистику"""
        if not self.current_student:
            return
        
        weekly_report = self.analytics.get_weekly_report()
        stats = self.progress_manager.get_progress_summary()
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        # Общая статистика
        self.stats_text.insert(tk.END, "📊 ОБЩАЯ СТАТИСТИКА:\n\n")
        self.stats_text.insert(tk.END, f"• Всего проанализировано работ: {stats['total_works_analyzed']}\n")
        self.stats_text.insert(tk.END, f"• Изучено тем: {stats['topics_worked']}\n")
        self.stats_text.insert(tk.END, f"• Всего сессий: {stats['total_sessions']}\n\n")
        
        # Недельный отчет
        self.stats_text.insert(tk.END, "📅 ОТЧЕТ ЗА НЕДЕЛЮ:\n\n")
        self.stats_text.insert(tk.END, f"• Сессий: {weekly_report['sessions_count']}\n")
        self.stats_text.insert(tk.END, f"• Активных тем: {weekly_report['active_topics']}\n\n")
        
        if weekly_report['most_problematic_topics']:
            self.stats_text.insert(tk.END, "📈 САМЫЕ ПРОБЛЕМНЫЕ ТЕМЫ:\n\n")
            for topic, count in weekly_report['most_problematic_topics']:
                self.stats_text.insert(tk.END, f"• {topic}: {count} раз(а)\n")
        
        # Прогресс по темам
        self.stats_text.insert(tk.END, "\n🎯 ПРОГРЕСС ПО ТЕМАМ:\n\n")
        for topic, data in self.progress_manager.progress_data["topics"].items():
            last_practiced = datetime.fromisoformat(data["last_practiced"]).strftime("%d.%m.%Y")
            self.stats_text.insert(tk.END, f"• {topic}:\n")
            self.stats_text.insert(tk.END, f"  Mastery: {data['mastery_score']:.1f}%\n")
            self.stats_text.insert(tk.END, f"  Встречалась: {data['encounter_count']} раз\n")
            self.stats_text.insert(tk.END, f"  Уровень: {data['difficulty_level']}\n\n")
        
        self.stats_text.config(state=tk.DISABLED)
    
    def generate_plan(self):
        """Генерирует индивидуальный план занятий"""
        if not self.current_student:
            return
        
        weak_topics = self.progress_manager.get_weak_topics()
        
        self.plan_text.config(state=tk.NORMAL)
        self.plan_text.delete(1.0, tk.END)
        
        if not weak_topics:
            self.plan_text.insert(tk.END, "🎉 У ВАС НЕТ СЛАБЫХ ТЕМ!\n\n")
            self.plan_text.insert(tk.END, "Продолжайте в том же духе! Вы отлично справляетесь!\n\n")
            self.plan_text.insert(tk.END, "Рекомендации для поддержания уровня:\n")
            self.plan_text.insert(tk.END, "1. Решайте задачи повышенной сложности\n")
            self.plan_text.insert(tk.END, "2. Помогайте одноклассникам\n")
            self.plan_text.insert(tk.END, "3. Изучайте смежные темы")
        else:
            self.plan_text.insert(tk.END, "📚 ИНДИВИДУАЛЬНЫЙ ПЛАН НА НЕДЕЛЮ:\n\n")
            
            days_plan = [
                "Понедельник", "Вторник", "Среда", "Четверг", 
                "Пятница", "Суббота", "Воскресенье"
            ]
            
            for i, day in enumerate(days_plan):
                if i < len(weak_topics):
                    topic = weak_topics[i]
                    mastery = self.progress_manager.progress_data["topics"][topic]["mastery_score"]
                    self.plan_text.insert(tk.END, f"📅 {day}: {topic}\n")
                    self.plan_text.insert(tk.END, f"   Текущий mastery: {mastery:.1f}%\n")
                    self.plan_text.insert(tk.END, f"   Цель: повысить до 80%\n\n")
                else:
                    self.plan_text.insert(tk.END, f"📅 {day}: Повторение пройденного материала\n\n")
            
            self.plan_text.insert(tk.END, f"🎯 ГЛАВНАЯ ЦЕЛЬ НЕДЕЛИ:\n")
            self.plan_text.insert(tk.END, f"Повысить mastery темы '{weak_topics[0]}' до 80%")
        
        self.plan_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = SchoolHelperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()