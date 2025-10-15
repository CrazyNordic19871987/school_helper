from datetime import datetime, timedelta

class Analytics:
    def __init__(self, progress_manager):
        self.progress_manager = progress_manager
    
    def get_weekly_report(self):
        """Генерирует недельный отчет"""
        week_ago = datetime.now() - timedelta(days=7)
        recent_sessions = []
        
        for session in self.progress_manager.progress_data["sessions"]:
            session_date = datetime.fromisoformat(session["date"])
            if session_date >= week_ago:
                recent_sessions.append(session)
        
        # Анализ активных тем
        topic_activity = {}
        for session in recent_sessions:
            for topic in session["found_topics"]:
                topic_activity[topic] = topic_activity.get(topic, 0) + 1
        
        return {
            "sessions_count": len(recent_sessions),
            "active_topics": len(topic_activity),
            "most_problematic_topics": sorted(topic_activity.items(), key=lambda x: x[1], reverse=True)[:3],
            "total_topics_worked": self.progress_manager.progress_data["statistics"]["topics_worked"]
        }
    
    def get_recommendations(self):
        """Выдает рекомендации для ученика"""
        weak_topics = self.progress_manager.get_weak_topics()
        summary = self.progress_manager.get_progress_summary()
        
        recommendations = []
        
        if not weak_topics:
            recommendations.append("🎉 Отличный прогресс! Все темы усвоены хорошо.")
        else:
            recommendations.append(f"💡 Рекомендуем повторить: {', '.join(weak_topics[:2])}")
        
        if summary["total_sessions"] < 3:
            recommendations.append("📚 Загрузите больше работ для более точного анализа")
        
        # Рекомендация по частоте занятий
        if summary["total_sessions"] > 5:
            last_session_date = datetime.fromisoformat(
                self.progress_manager.progress_data["sessions"][-1]["date"]
            )
            days_since_last = (datetime.now() - last_session_date).days
            
            if days_since_last > 7:
                recommendations.append("⏰ Вы не занимались больше недели. Рекомендуем регулярные тренировки!")
        
        return recommendations