import os
import sys

# Добавляем путь для импорта
sys.path.append(os.path.dirname(__file__))

try:
    from src.main import ConstructionAIScout
    print("✅ Модули успешно загружены!")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Проверьте структуру файлов:")
    print(" - Папка src/ существует")
    print(" - Файл src/__init__.py существует") 
    print(" - Файл src/main.py существует")
    sys.exit(1)

def clear_screen():
    """Очистка экрана"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    """Показать баннер"""
    print("🚀 ИИ-РАЗВЕДЧИК ДЛЯ СТРОИТЕЛЬНЫХ ПОСТАВОК")
    print("🌐 С АВТОМАТИЧЕСКИМ ПАРСИНГОМ ЦЕН")
    print("=" * 55)

def main():
    """Основная функция запуска"""
    clear_screen()
    show_banner()
    
    try:
        scout = ConstructionAIScout()
        
        while True:
            print("\n📋 ГЛАВНОЕ МЕНЮ:")
            print("1 - 🔄 ЗАПУСТИТЬ АВТОПАРСИНГ ЦЕН (реальные данные)")
            print("2 - 🏆 ПОКАЗАТЬ ЛУЧШИЕ ЦЕНЫ (из последнего отчета)")
            print("3 - 📊 ПОСМОТРЕТЬ ИСТОРИЮ ЦЕН")
            print("4 - 🏪 ПРОВЕРИТЬ ПОСТАВЩИКА")
            print("5 - ⚙️  ТЕКУЩИЕ НАСТРОЙКИ")
            print("6 - 💾 ТЕСТОВЫЙ РЕЖИМ (заглушки)")
            print("7 - ❌ ВЫХОД")
            
            choice = input("\n🎯 Выберите команду (1-7): ").strip()
            
            if choice == "1":
                clear_screen()
                show_banner()
                print("\n🌐 ЗАПУСК АВТОМАТИЧЕСКОГО ПАРСИНГА...")
                print("⏳ Это может занять 2-3 минуты...")
                print("📡 Парсим реальные данные с сайтов магазинов...")
                
                # ИСПРАВЛЕННАЯ СТРОКА - добавлен use_parser=True
                report = scout.daily_scouting_report(use_parser=True)
                
                clear_screen()
                show_banner()
                print(f"\n✅ {report['summary']}")
                
                # Показываем детальные результаты
                if report['materials_analysis']:
                    print(f"\n🏆 РЕЗУЛЬТАТЫ ПАРСИНГА ({len(report['materials_analysis'])} товаров):")
                    print("=" * 55)
                    
                    total_economy = 0
                    for i, item in enumerate(report['materials_analysis'], 1):
                        print(f"\n{i}. 📦 {item['material']}:")
                        print(f"   🏪 Поставщик: {item['best_supplier']}")
                        print(f"   💰 Цена: {item['best_price']} руб.")
                        if item.get('product_name'):
                            print(f"   📝 Товар: {item['product_name']}")
                        if item.get('url'):
                            print(f"   🔗 Ссылка: {item['url'][:80]}...")
                        print(f"   💵 Экономия: {item['economy']} руб.")
                        total_economy += item['economy']
                    
                    print(f"\n💰 ОБЩАЯ ЭКОНОМИЯ: {total_economy:.2f} руб.")
                    print(f"💾 Данные сохранены в: data/scout_report.csv")
                
                input("\n↵ Нажмите Enter для возврата в меню...")
                clear_screen()
                show_banner()
                
            elif choice == "2":
                clear_screen()
                show_banner()
                print("\n🏆 ЛУЧШИЕ ЦЕНЫ ИЗ ПОСЛЕДНЕГО ОТЧЕТА:")
                print("=" * 55)
                
                try:
                    # Пробуем загрузить последний отчет
                    prices_df = scout.price_monitor.get_all_prices(use_parser=False)
                    best_prices = scout.price_monitor.find_best_prices()
                    
                    if best_prices:
                        total_economy = 0
                        for i, item in enumerate(best_prices, 1):
                            print(f"\n{i}. 📦 {item['material']}:")
                            print(f"   🏪 Лучший: {item['best_supplier']} - {item['best_price']} руб.")
                            if item.get('product_name'):
                                print(f"   📝 {item['product_name']}")
                            print(f"   💵 Экономия: {item['economy']} руб.")
                            
                            print(f"   📊 Все варианты:")
                            for opt in item['all_options']:
                                marker = " 🏆" if opt['supplier'] == item['best_supplier'] else ""
                                product_info = f" - {opt.get('product_name', '')}" if opt.get('product_name') else ""
                                print(f"      • {opt['supplier']}: {opt['price']} руб.{marker}{product_info}")
                            
                            total_economy += item['economy']
                        
                        print(f"\n💰 ОБЩАЯ ЭКОНОМИЯ: {total_economy:.2f} руб.")
                    else:
                        print("\n❌ Нет данных. Запустите сначала автопарсинг (команда 1).")
                        
                except Exception as e:
                    print(f"\n❌ Ошибка загрузки данных: {e}")
                    print("Запустите сначала автопарсинг (команда 1).")
                
                input("\n↵ Нажмите Enter для возврата в меню...")
                clear_screen()
                show_banner()
                
            elif choice == "3":
                clear_screen()
                show_banner()
                print("\n📊 ИСТОРИЯ ЦЕН:")
                print("=" * 55)
                
                materials = scout.get_available_materials()
                if materials:
                    print("\n📦 Доступные товары для анализа:")
                    for i, material in enumerate(materials, 1):
                        print(f"   {i}. {material}")
                    
                    try:
                        material_choice = input("\n🎯 Выберите номер товара: ").strip()
                        if material_choice.isdigit() and 1 <= int(material_choice) <= len(materials):
                            selected_material = materials[int(material_choice) - 1]
                            history = scout.price_monitor.get_price_history(selected_material, days=30)
                            
                            if not history.empty:
                                print(f"\n📈 История цен на '{selected_material}' (30 дней):")
                                print("-" * 55)
                                
                                # Группируем по поставщикам
                                suppliers = history['supplier'].unique()
                                for supplier in suppliers:
                                    supplier_data = history[history['supplier'] == supplier]
                                    min_price = supplier_data['price'].min()
                                    max_price = supplier_data['price'].max()
                                    last_price = supplier_data.iloc[-1]['price']
                                    print(f"\n🏪 {supplier}:")
                                    print(f"   📊 Мин: {min_price} руб.")
                                    print(f"   📊 Макс: {max_price} руб.") 
                                    print(f"   📊 Текущая: {last_price} руб.")
                                    print(f"   📅 Записей: {len(supplier_data)}")
                            else:
                                print(f"\n❌ Нет исторических данных для '{selected_material}'")
                        else:
                            print("❌ Неверный выбор")
                    except ValueError:
                        print("❌ Введите число")
                else:
                    print("❌ Нет доступных товаров. Проверьте настройки.")
                
                input("\n↵ Нажмите Enter для возврата в меню...")
                clear_screen()
                show_banner()
                
            elif choice == "4":
                clear_screen()
                show_banner()
                print("\n🏪 ПРОВЕРКА ПОСТАВЩИКА:")
                print("=" * 55)
                
                suppliers = scout.get_available_suppliers()
                if suppliers:
                    print(f"\n📋 Доступные поставщики:")
                    for i, supplier in enumerate(suppliers, 1):
                        print(f"   {i}. {supplier}")
                    
                    try:
                        supplier_choice = input("\n🎯 Выберите номер поставщика: ").strip()
                        if supplier_choice.isdigit() and 1 <= int(supplier_choice) <= len(suppliers):
                            selected_supplier = suppliers[int(supplier_choice) - 1]
                            result = scout.check_supplier(selected_supplier)
                            
                            if result:
                                print(f"\n🔍 АНАЛИЗ ПОСТАВЩИКА: {selected_supplier}")
                                print("-" * 55)
                                print(f"   📊 Рейтинг надежности: {result['reliability_score']}/100")
                                print(f"   🏷️ Статус: {result['status']}")
                                print(f"   📦 Товаров в базе: {result['materials_count']}")
                                print(f"   💡 Рекомендация: {result['recommendation']}")
                                print(f"   🌐 Сайт: {result['url']}")
                                
                                # Показываем товары этого поставщика
                                prices_df = scout.price_monitor.get_all_prices(use_parser=False)
                                supplier_prices = prices_df[prices_df['supplier'] == selected_supplier]
                                if not supplier_prices.empty:
                                    print(f"\n📦 Товары поставщика:")
                                    for _, row in supplier_prices.iterrows():
                                        print(f"   • {row['material']}: {row['price']} руб.")
                            else:
                                print(f"❌ Не удалось проанализировать поставщика {selected_supplier}")
                        else:
                            print("❌ Неверный выбор")
                    except ValueError:
                        print("❌ Введите число")
                else:
                    print("❌ Нет доступных поставщиков. Проверьте настройки.")
                
                input("\n↵ Нажмите Enter для возврата в меню...")
                clear_screen()
                show_banner()
                
            elif choice == "5":
                clear_screen()
                show_banner()
                print("\n⚙️ ТЕКУЩИЕ НАСТРОЙКИ:")
                print("=" * 55)
                
                materials = scout.get_available_materials()
                suppliers = scout.get_available_suppliers()
                
                print(f"\n📦 ОТСЛЕЖИВАЕМЫЕ ТОВАРЫ ({len(materials)}):")
                for i, material in enumerate(materials, 1):
                    print(f"   {i}. {material}")
                
                print(f"\n🏪 ОТСЛЕЖИВАЕМЫЕ МАГАЗИНЫ ({len(suppliers)}):")
                for i, supplier in enumerate(suppliers, 1):
                    print(f"   {i}. {supplier}")
                
                print(f"\n💡 ИНСТРУКЦИЯ:")
                print("   1. Для изменения товаров отредактируйте: config/config.yaml")
                print("   2. В разделе 'target_materials' добавьте свои товары")
                print("   3. В разделе 'suppliers' настройте магазины")
                print("   4. Для автопарсинга используйте команду 1")
                
                input("\n↵ Нажмите Enter для возврата в меню...")
                clear_screen()
                show_banner()
                
            elif choice == "6":
                clear_screen()
                show_banner()
                print("\n💾 ТЕСТОВЫЙ РЕЖИМ (ЗАГЛУШКИ):")
                print("=" * 55)
                print("🔧 Генерация тестовых данных без парсинга...")
                
                report = scout.daily_scouting_report(use_parser=False)
                
                print(f"\n✅ {report['summary']}")
                
                if report['materials_analysis']:
                    print(f"\n🏆 ТЕСТОВЫЕ РЕЗУЛЬТАТЫ ({len(report['materials_analysis'])} товаров):")
                    for item in report['materials_analysis']:
                        print(f"   📦 {item['material']}: {item['best_supplier']} - {item['best_price']} руб.")
                
                print("\n💡 Для реальных данных используйте команду 1 (Автопарсинг)")
                
                input("\n↵ Нажмите Enter для возврата в меню...")
                clear_screen()
                show_banner()
                
            elif choice == "7":
                print("\n👋 До свидания! Удачных закупок! 🛒")
                break
                
            else:
                print("❌ Неверная команда. Выберите от 1 до 7.")
                
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("Проверьте наличие файла config/config.yaml")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()