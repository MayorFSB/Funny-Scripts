from win10toast import ToastNotifier
import time
import webbrowser


# функция для создания уведомлений
def notification(string, a, b):
    toaster = ToastNotifier()
    toaster.show_toast(title=f"Сегодня у товара минимальная цена",
                       msg=f"Сегодня можно выгодно купить {string[0]}. Дешевле чем вчера на {round(b - a,2)} BYN",
                       icon_path=None,
                       duration=5,
                       threaded=True, )
    while toaster.notification_active():
        time.sleep(0.1)


# функция для открытия в браузере ссылок упавших в цене товаров
def open_in_browser(db_string):
    chrome_browser = webbrowser.get('chrome')
    print(f'ПРОДУКТ {db_string[0]} СТАЛ ДЕШЕВЛЕ')
    chrome_browser.open(f'https://ozon.by/product/{db_string[0]}/')