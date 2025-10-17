import yaml
from datetime import datetime

class SupplierAnalyzer:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path

    def analyze_supplier(self, supplier_name):
        """Анализ поставщика по имени"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            suppliers = config['scout']['suppliers']
            if supplier_name not in suppliers:
                return None
            
            supplier_data = suppliers[supplier_name]
            materials_count = len(supplier_data['materials'])
            
            # Расчет рейтинга на основе количества товаров и цен
            reliability_score = min(80 + (materials_count * 2), 100)
            
            if reliability_score >= 85:
                status = "Высокая надежность"
                recommendation = "Рекомендуется"
            elif reliability_score >= 70:
                status = "Средняя надежность" 
                recommendation = "Под контролем"
            else:
                status = "Требует проверки"
                recommendation = "Осторожно"
            
            return {
                'supplier_name': supplier_name,
                'materials_count': materials_count,
                'reliability_score': reliability_score,
                'status': status,
                'recommendation': recommendation,
                'url': supplier_data['url']
            }
            
        except Exception as e:
            print(f"Ошибка анализа поставщика: {e}")
            return None