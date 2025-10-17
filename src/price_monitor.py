import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import yaml
from datetime import datetime
import os

class PriceMonitor:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Создаем файл для хранения исторических данных, если его нет
        self.data_file = "data/historical_prices.csv"
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.data_file):
            pd.DataFrame(columns=['material', 'supplier', 'price', 'date']).to_csv(self.data_file, index=False)

    def parse_petrovich(self, material):
        """Парсинг цен с Петровича"""
        # Заглушка для примера - в реальности нужно настроить под структуру сайта
        try:
            # Эмуляция поиска и парсинга
            mock_prices = {
                "бетон M300": 4500,
                "арматура 12mm": 85,
                "цемент M500": 420,
                "песок строительный": 350,
                "кирпич керамический": 25
            }
            
            return {
                'supplier': 'Петрович',
                'material': material,
                'price': mock_prices.get(material, 0),
                'date': datetime.now()
            }
        except Exception as e:
            print(f"Ошибка парсинга Петрович: {e}")
            return None

    def parse_leroy(self, material):
        """Парсинг цен с Леруа Мерлен"""
        try:
            mock_prices = {
                "бетон M300": 4700,
                "арматура 12mm": 88,
                "цемент M500": 440,
                "песок строительный": 380,
                "кирпич керамический": 27
            }
            
            return {
                'supplier': 'Леруа Мерлен',
                'material': material,
                'price': mock_prices.get(material, 0),
                'date': datetime.now()
            }
        except Exception as e:
            print(f"Ошибка парсинга Леруа Мерлен: {e}")
            return None

    def get_all_prices(self):
        """Получение цен по всем материалам у всех поставщиков"""
        all_prices = []
        
        for material in self.config['scout']['target_materials']:
            print(f"Сбор цен на: {material}")
            
            # Парсим у разных поставщиков
            suppliers_data = [
                self.parse_petrovich(material),
                self.parse_leroy(material),
                # Добавьте другие поставщики здесь
            ]
            
            # Фильтруем None значения
            valid_data = [data for data in suppliers_data if data is not None]
            all_prices.extend(valid_data)
            
            # Пауза между запросами
            time.sleep(2)
        
        return pd.DataFrame(all_prices)

    def save_prices(self, prices_df):
        """Сохранение цен в исторический файл"""
        if os.path.exists(self.data_file):
            historical_data = pd.read_csv(self.data_file)
            updated_data = pd.concat([historical_data, prices_df], ignore_index=True)
        else:
            updated_data = prices_df
        
        updated_data.to_csv(self.data_file, index=False)
        print(f"Цены сохранены в {self.data_file}")

    def get_price_history(self, material, days=30):
        """Получение исторических цен по материалу"""
        if not os.path.exists(self.data_file):
            return pd.DataFrame()
        
        data = pd.read_csv(self.data_file)
        data['date'] = pd.to_datetime(data['date'])
        
        # Фильтруем по материалу и дате
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        filtered_data = data[
            (data['material'] == material) & 
            (data['date'] >= cutoff_date)
        ]
        
        return filtered_data

if __name__ == "__main__":
    monitor = PriceMonitor()
    prices = monitor.get_all_prices()
    print(prices)
    monitor.save_prices(prices)