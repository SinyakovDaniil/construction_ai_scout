import csv
import os
import sys
import yaml
import json
from datetime import datetime

# Добавляем путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.price_monitor import PriceMonitor
from src.supplier_analyzer import SupplierAnalyzer

class ConstructionAIScout:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        self.load_config()
        
        self.price_monitor = PriceMonitor(config_path)
        self.supplier_analyzer = SupplierAnalyzer(config_path)
        
        # Создаем папки
        os.makedirs("data/reports", exist_ok=True)

    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            print(f"❌ Ошибка загрузки конфига: {e}")
            self.config = {'scout': {'target_materials': [], 'suppliers': {}}}

    def daily_scouting_report(self, use_parser=False):
        """Ежедневный отчет по ценам"""
        print("🤖 ИИ-разведчик анализирует цены...")
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'materials_analysis': [],
            'summary': '',
            'total_economy': 0
        }
        
        try:
            # Получаем цены (реальные или тестовые)
            if use_parser:
                print("🌐 Используем реальный парсинг...")
                prices_data = self.price_monitor.get_all_prices(use_parser=True)
            else:
                print("🔧 Используем тестовые данные...")
                prices_data = self.price_monitor.get_all_prices(use_parser=False)
            
            # Сохраняем цены
            self.price_monitor.save_prices(prices_data)
            
            # Находим лучшие цены
            best_prices = self.price_monitor.find_best_prices()
            
            # Формируем отчет
            economy = 0
            for item in best_prices:
                economy += item['economy']
                
                report['materials_analysis'].append({
                    'material': item['material'],
                    'best_supplier': item['best_supplier'],
                    'best_price': item['best_price'],
                    'product_name': item.get('product_name', ''),
                    'url': item.get('url', ''),
                    'economy': item['economy'],
                    'all_options': item['all_options']
                })
            
            report['total_economy'] = round(economy, 2)
            report['summary'] = f"Проанализировано {len(best_prices)} материалов. Экономия: {report['total_economy']} руб."
            
            # Сохраняем отчет
            self.save_report(report)
            print("✅ Отчет успешно сгенерирован!")
            
        except Exception as e:
            print(f"❌ Ошибка при генерации отчета: {e}")
            report['summary'] = f"Ошибка: {e}"
        
        return report

    def save_report(self, report):
        """Сохранение отчета в CSV"""
        if report['materials_analysis']:
            with open("data/scout_report.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['material', 'best_supplier', 'best_price', 'economy', 'date'])
                
                for item in report['materials_analysis']:
                    writer.writerow([
                        item['material'],
                        item['best_supplier'],
                        item['best_price'],
                        item['economy'],
                        report['date']
                    ])
        
        # Сохраняем полный отчет как JSON
        report_file = f"data/reports/report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    def check_supplier(self, supplier_name):
        """Проверка поставщика"""
        return self.supplier_analyzer.analyze_supplier(supplier_name)

    def get_available_suppliers(self):
        """Получение списка доступных поставщиков"""
        return list(self.config['scout']['suppliers'].keys())

    def get_available_materials(self):
        """Получение списка доступных материалов"""
        return self.config['scout']['target_materials']

if __name__ == "__main__":
    scout = ConstructionAIScout()
    report = scout.daily_scouting_report()
    print(f"Отчет: {report['summary']}")