import csv
import os
import yaml
import random
from datetime import datetime
from .web_parser import WebPriceParser

class PriceMonitor:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        self.load_config()
        self.parser = WebPriceParser(self.config)
        
        # Создаем папку для данных
        os.makedirs("data", exist_ok=True)
        self.data_file = "data/historical_prices.csv"

    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            print(f"❌ Ошибка загрузки конфига: {e}")
            self.config = {'scout': {'target_materials': [], 'suppliers': {}}}

    def get_all_prices(self, use_parser=True):
        """Получение всех цен"""
        if use_parser:
            print("🌐 Запуск автоматического парсинга цен...")
            return self.parser.parse_all_prices()
        else:
            return self.get_mock_prices()

    def get_mock_prices(self):
        """Заглушка для тестирования"""
        base_prices = {
            "бетон M300": 4500,
            "арматура 12мм": 85, 
            "цемент M500": 420,
            "кирпич красный": 25,
            "гипсокартон 12мм": 410,
            "краска белая интерьерная": 1800,
            "плитка напольная керамическая": 850,
            "утеплитель пенопласт 50мм": 2800,
            "профнастил С8": 350,
            "доска обрезная 50x100": 12000
        }
        
        prices_data = []
        for supplier_name in self.config['scout']['suppliers']:
            for material in self.config['scout']['target_materials']:
                base_price = base_prices.get(material, 1000)
                price_variation = base_price * random.uniform(-0.1, 0.1)
                price = round(base_price + price_variation, 2)
                
                prices_data.append({
                    'material': material,
                    'supplier': supplier_name,
                    'price': price,
                    'product_name': f"{material} ({supplier_name})",
                    'url': f"https://example.com/{material.replace(' ', '-')}",
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return prices_data

    def save_prices(self, prices_data):
        """Сохранение цен в CSV"""
        file_exists = os.path.exists(self.data_file)
        
        with open(self.data_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow(['material', 'supplier', 'price', 'product_name', 'url', 'date'])
            
            for item in prices_data:
                writer.writerow([
                    item['material'],
                    item['supplier'],
                    item['price'],
                    item.get('product_name', ''),
                    item.get('url', ''),
                    item.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                ])
        
        print(f"💾 Цены сохранены: {len(prices_data)} записей")

    def find_best_prices(self):
        """Поиск лучших цен по каждому материалу"""
        prices_data = self.get_all_prices(use_parser=False)  # Пока используем заглушки
        best_prices = []
        
        # Группируем по материалам
        materials_dict = {}
        for item in prices_data:
            material = item['material']
            if material not in materials_dict:
                materials_dict[material] = []
            materials_dict[material].append(item)
        
        # Находим лучшие цены
        for material, items in materials_dict.items():
            if items:
                best_item = min(items, key=lambda x: x['price'])
                all_prices = [item['price'] for item in items]
                avg_price = sum(all_prices) / len(all_prices)
                economy = avg_price - best_item['price']
                
                best_prices.append({
                    'material': material,
                    'best_supplier': best_item['supplier'],
                    'best_price': best_item['price'],
                    'product_name': best_item.get('product_name', ''),
                    'url': best_item.get('url', ''),
                    'economy': round(economy, 2),
                    'all_options': [{'supplier': item['supplier'], 'price': item['price']} for item in items]
                })
        
        return best_prices

    def get_price_history(self, material, days=30):
        """Получение истории цен по материалу"""
        if not os.path.exists(self.data_file):
            return []
        
        history = []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['material'] == material:
                    history.append({
                        'supplier': row['supplier'],
                        'price': float(row['price']),
                        'date': row['date']
                    })
        
        return history