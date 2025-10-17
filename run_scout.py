import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import ConstructionAIScout
import schedule
import time
from datetime import datetime

def daily_report():
    """Ежедневный отчет"""
    print(f"\n{'='*50}")
    print(f"ЗАПУСК ЕЖЕДНЕВНОГО ОТЧЕТА - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")
    
    scout = ConstructionAIScout()
    report = scout.daily_scouting_report()
    
    print(f"\nОтчет сгенерирован и сохранен в: data/scout_report.csv")
    print(f"Графики сохранены в: data/reports/")

def main():
    """Основная функция запуска"""
    print("🚀 ИИ-разведчик для строительных поставок запущен!")
    print("Режимы работы:")
    print("1 - Единоразовый отчет")
    print("2 - Запуск по расписанию (ежедневно в 09:00)")
    print("3 - Проверка конкретного поставщика")
    
    choice = input("\nВыберите режим (1-3): ").strip()
    
    scout = ConstructionAIScout()
    
    if choice == "1":
        print("\nГенерация отчета...")
        report = scout.daily_scouting_report()
        
    elif choice == "2":
        print("\nЗапуск по расписанию...")
        print("Отчеты будут генерироваться ежедневно в 09:00")
        print("Для остановки нажмите Ctrl+C")
        
        schedule.every().day.at("09:00").do(daily_report)
        
        # Первый запуск сразу
        daily_report()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Проверка каждую минуту
            
    elif choice == "3":
        inn = input("Введите ИНН поставщика: ").strip()
        name = input("Введите название компании: ").strip()
        
        result = scout.check_supplier(inn, name)
        if result:
            print(f"\nРезультат проверки:")
            print(f"Компания: {result['company_name']}")
            print(f"ИНН: {result['inn']}")
            print(f"Рейтинг надежности: {result['reliability_score']}/100")
            print(f"Статус: {result['status']}")
            print(f"Рекомендация: {result['recommendation']}")
        else:
            print("Не удалось проверить поставщика")
    
    else:
        print("Неверный выбор")

if __name__ == "__main__":
    main()