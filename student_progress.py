import json
import os
from datetime import datetime, timedelta

# Используем абсолютные пути относительно расположения файлов
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(BASE_DIR, "data", "progress.json")
STUDENT_WORKS_DIR = os.path.join(BASE_DIR, "data", "student_data")

class StudentProgress:
    def __init__(self, student_name):
        self.student_name = student_name
        self.progress_file = PROGRESS_FILE
        self.works_dir = STUDENT_WORKS_DIR
        self.load_progress()
    
    def load_progress(self):
        """Загружает прогресс ученика из файла"""
        # Создаем директорию для данных, если ее нет
        os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
        
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.progress_data = data.get(self.student_name, {})
            except (json.JSONDecodeError, FileNotFoundError):
                self.progress_data = {}
        else:
            self.progress_data = {}
        
        # Инициализация структуры данных
        if "topics" not in self.progress_data:
            self.progress_data["topics"] = {}
        if "sessions" not in self.progress_data:
            self.progress_data["sessions"] = []
        if "statistics" not in self.progress_data:
            self.progress_data["statistics"] = {
                "total_sessions": 0,
                "total_works_analyzed": 0,
                "topics_worked": 0
            }
    
    def save_progress(self):
        """Сохраняет прогресс ученика в файл"""
        # Создаем директории, если их нет
        os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
        
        # Загружаем существующие данные
        all_data = {}
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    all_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                all_data = {}
        
        # Обновляем данные текущего ученика
        all_data[self.student_name] = self.progress_data
        
        # Сохраняем
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении прогресса: {e}")
    
    def add_session(self, analyzed_text, found_topics, recommended_tasks):
        """Добавляет информацию о сессии"""
        session = {
            "date": datetime.now().isoformat(),
            "analyzed_text": analyzed_text[:100] + "..." if len(analyzed_text) > 100 else analyzed_text,
            "found_topics": found_topics,
            "recommended_tasks": recommended_tasks
        }
        
        self.progress_data["sessions"].append(session)
        self.progress_data["statistics"]["total_sessions"] += 1
        self.progress_data["statistics"]["total_works_analyzed"] += 1
        
        # Обновляем статистику по темам
        for topic in found_topics:
            if topic not in self.progress_data["topics"]:
                self.progress_data["topics"][topic] = {
                    "first_encounter": datetime.now().isoformat(),
                    "encounter_count": 0,
                    "last_practiced": datetime.now().isoformat(),
                    "difficulty_level": "medium",
                    "mastery_score": 0  # 0-100 баллов
                }
                self.progress_data["statistics"]["topics_worked"] += 1
            
            self.progress_data["topics"][topic]["encounter_count"] += 1
            self.progress_data["topics"][topic]["last_practiced"] = datetime.now().isoformat()
        
        self.save_progress()
    
    def save_student_work(self, work_text, work_type="homework"):
        """Сохраняет работу ученика в отдельный файл"""
        # Создаем директории, если их нет
        os.makedirs(self.works_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Убираем проблемные символы из имени файла
        safe_name = "".join(c for c in self.student_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = os.path.join(self.works_dir, f"{safe_name}_{work_type}_{timestamp}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(work_text)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении работы: {e}")
            return False
    
    def get_weak_topics(self, min_encounters=2):
        """Возвращает темы, которые требуют повторения"""
        weak_topics = []
        for topic, data in self.progress_data["topics"].items():
            if data["encounter_count"] >= min_encounters and data["mastery_score"] < 70:
                weak_topics.append(topic)
        return weak_topics
    
    def update_mastery(self, topic, success_rate):
        """Обновляет уровень mastery темы на основе успешности выполнения заданий"""
        if topic in self.progress_data["topics"]:
            # Простая формула для расчета mastery
            current_mastery = self.progress_data["topics"][topic]["mastery_score"]
            new_mastery = min(100, current_mastery + (success_rate - 50) * 0.5)
            self.progress_data["topics"][topic]["mastery_score"] = max(0, new_mastery)
            
            # Обновляем уровень сложности
            if new_mastery > 80:
                self.progress_data["topics"][topic]["difficulty_level"] = "hard"
            elif new_mastery > 50:
                self.progress_data["topics"][topic]["difficulty_level"] = "medium"
            else:
                self.progress_data["topics"][topic]["difficulty_level"] = "easy"
            
            self.save_progress()
    
    def get_progress_summary(self):
        """Возвращает сводку по прогрессу"""
        return self.progress_data["statistics"]