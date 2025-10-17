import pandas as pd
import yaml
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time

class SupplierAnalyzer:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def check_rusprofile(self, inn):
        """Проверка компании через Роспрофиль (пример)"""
        try:
            url = f"https://www.rusprofile.ru/search?query={inn}"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Здесь будет реальный парсинг данных
            # Для примера возвращаем mock-данные
            
            return {
                'inn': inn,
                'company_age': 5,
                'status': 'Действующее',
                'lawsuits_count': 2,
                'employees_range': '51-100',
                'revenue_category': 'средняя',
                'last_checked': datetime.now()
            }
            
        except Exception as e:
            print(f"Ошибка проверки ИНН {inn}: {e}")
            return None

    def calculate_reliability_score(self, company_data):
        """Расчет рейтинга надежности компании"""
        if not company_data:
            return 0
        
        score = 100
        
        # Возраст компании
        age = company_data.get('company_age', 0)
        if age >= 10:
            score += 20
        elif age >= 5:
            score += 10
        elif age < 2:
            score -= 15
        
        # Судебные дела
        lawsuits = company_data.get('lawsuits_count', 0)
        score -= lawsuits * 5
        
        # Статус компании
        status = company_data.get('status', '')
        if status != 'Действующее':
            score -= 30
        
        # Количество сотрудников
        employees = company_data.get('employees_range', '')
        if employees in ['101-250', '251-500', '501-1000', '1000+']:
            score += 15
        elif employees in ['11-50', '51-100']:
            score += 5
        
        return max(0, min(score, 100))

    def analyze_supplier(self, inn, company_name):
        """Полный анализ поставщика"""
        print(f"Анализ поставщика: {company_name} (ИНН: {inn})")
        
        company_data = self.check_rusprofile(inn)
        if not company_data:
            return None
        
        reliability_score = self.calculate_reliability_score(company_data)
        
        # Определяем статус
        if reliability_score >= 80:
            status = "Высокая надежность"
            recommendation = "Рекомендуется к сотрудничеству"
        elif reliability_score >= 60:
            status = "Средняя надежность"
            recommendation = "Требуется дополнительная проверка"
        else:
            status = "Низкая надежность"
            recommendation = "Не рекомендуется"
        
        analysis_result = {
            'company_name': company_name,
            'inn': inn,
            'reliability_score': reliability_score,
            'status': status,
            'recommendation': recommendation,
            **company_data
        }
        
        return analysis_result

    def check_suppliers_batch(self, suppliers_list):
        """Пакетная проверка списка поставщиков"""
        results = []
        
        for supplier in suppliers_list:
            inn = supplier.get('inn')
            name = supplier.get('name')
            
            if inn and name:
                result = self.analyze_supplier(inn, name)
                if result:
                    results.append(result)
            
            time.sleep(1)  # Пауза между запросами
        
        return pd.DataFrame(results)

if __name__ == "__main__":
    analyzer = SupplierAnalyzer()
    
    # Пример списка поставщиков для проверки
    test_suppliers = [
        {'inn': '7701234567', 'name': 'ООО СтройМастер'},
        {'inn': '7707654321', 'name': 'ООО БетонПрофи'}
    ]
    
    results = analyzer.check_suppliers_batch(test_suppliers)
    print(results[['company_name', 'reliability_score', 'status']])