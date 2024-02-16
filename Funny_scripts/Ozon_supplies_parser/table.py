import sqlite3, requests, re, time
from datetime import datetime
from bs4 import BeautifulSoup as bsf4
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QLabel, \
    QLineEdit, QPushButton, QAbstractItemView
import config
from functions import notification, open_in_browser


class DatabaseApp(QMainWindow):
    def __init__(self, file_db_):
        super().__init__()
        self.file_db = file_db_

        # Создаем таблицу
        self.table = QTableWidget()
        self.setCentralWidget(self.table)

        # Подключаемся к базе
        self.connection = sqlite3.connect(self.file_db)
        self.data = self.connection.cursor()
        self.name_db = 'ozon'
        self.data.execute(f'CREATE TABLE IF NOT EXISTS {self.name_db} (link TEXT)')
        self.links = self.data.execute(f'SELECT link FROM {self.name_db}').fetchall()
        self.cols = self.data.execute(f'PRAGMA table_info({self.name_db})').fetchall()
        self.col_names = [self.cols[x][1] for x in range(len(self.cols))]
        print(f'ссылки {self.links}')
        print(f"колонки {self.cols}")

        # Построчно отрисовываем таблицу получая данные из базы
        self.update_table()

        # Создаем описание кнопок и окна ввода
        self.input_label = QLabel("Новое значение:")
        self.input_text = QLineEdit()
        self.save_button = QPushButton("Сохранить ссылку на новый товар")
        self.update_button = QPushButton("Обновить цены за сегодня")
        self.delete_button = QPushButton("Удалить выбранную строку")

        # Создаем виджет для поля ввода и кнопок
        self.input_widget = QWidget()
        self.input_layout = QVBoxLayout()
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_text)
        self.input_layout.addWidget(self.save_button)
        self.input_layout.addWidget(self.update_button)
        self.input_layout.addWidget(self.delete_button)
        self.input_widget.setLayout(self.input_layout)

        # Создаем главный виждет и добавляем в него  кнопки и таблицу
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.table)
        self.main_widget.setLayout(self.main_layout)

        # Отрисовываем виджет с кнопками по центру
        self.setCentralWidget(self.main_widget)

        # Подключаем нажатия кнопок к функциям
        self.save_button.clicked.connect(self.save_data)  # noqa Cannot find reference 'connect' in 'pyqtSignal \
        self.update_button.clicked.connect(self.update_data)  # noqa | pyqtSignal | function'
        self.delete_button.clicked.connect(self.delete_data)  # noqa не знаю как исправить

    # функция обновления базы в случае закрытия программы
    def closeEvent(self, event):
        self.update_until_close()
        event.accept()
        self.connection.close()
        print('CLOSE EVENT')

    # функция обновления виджета таблицы
    def update_table(self):
        self.table.clearContents()
        # Получаем количество строк и столбцов с именами в таблице для отрисовки
        self.table.setRowCount(len(self.links))
        self.table.setColumnCount(len(self.cols))
        self.col_names = [self.cols[x][1] for x in range(len(self.cols))]
        print(f'Имена колонок {self.col_names}')
        self.table.setHorizontalHeaderLabels(self.col_names)
        try:
            for row, i in enumerate(self.links):
                db_string = self.data.execute(f'SELECT * FROM {self.name_db} WHERE link = ?', (i[0],)).fetchall()[0]
                self.less_price(db_string)
                for col in range(len(db_string)):
                    self.table.setItem(row, col, QTableWidgetItem(db_string[col]))
        except Exception as e:
            print('update_table error', e)
        print('UPDATE WORK')

    # Функция сохраняет новый товар в базу данных в позицию link и получает актуальную цену обновлением в текущий день
    def save_data(self):
        link = self.input_text.text()
        try:
            tovar = re.findall(r'([a-zA-Z0-9-]+\d+)', link)[0]
            link = tovar
        except Exception as e:
            print('СОХРАНЕНИЕ ERROR', e)
            pass
        links = [self.links[x][0] for x in range(len(self.links))]
        if link not in links:
            self.table.setItem(len(self.links), 0, QTableWidgetItem(link))
            self.input_text.clear()
            sql_query = f'INSERT INTO {self.name_db} (link) VALUES(?)'
            print(f'СОХРАНЕНИЕ запрос: {sql_query} | ссылка: {link}')
            self.data.execute(sql_query, (link,))
            self.connection.commit()
            self.links = self.data.execute(f'SELECT link FROM {self.name_db}').fetchall()
            self.cols = self.data.execute(f'PRAGMA table_info({self.name_db})').fetchall()
            self.parsed_l(link)
        else:
            print('Такой товар уже есть в базе')

        print('сохранение работает')

    # функция создания новой колонки даты в формате y%Ym%md%d
    # возвращает значение текущей даты
    # так как вектор времени идет в одном направлении
    # сравнение дат происходит только с последнией колонкой в таблице и запись данных будет осуществляться ТОЛЬКО туда
    def get_new_conumn(self):
        format_ = 'y%Ym%md%d'
        last_col = self.data.execute(f'PRAGMA table_info({self.name_db})').fetchall()[-1][1]
        date_now = datetime.now().date()
        date_now_str = datetime.strftime(date_now, format_)
        td = datetime.strptime(date_now_str, format_).strftime(format_)
        try:
            if datetime.strptime(last_col, format_).date() == datetime.now().date():
                print('Дата сего дня уже есть в базе')
            else:
                print('GEN NEW COL td=', td)
                try:
                    self.data.execute(f'ALTER TABLE {self.name_db} ADD COLUMN {td} TEXT')
                    self.connection.commit()
                    last_col = td
                    for j in self.links:
                        print('GEN NEW COL j[0]:', j[0])
                        self.parsed_l(j[0])
                except Exception as e:
                    print('GEN NEW COL ERROR 1', e)
        except Exception as e:
            print('GEN NEW COL ERROR 2', e)
            last_col = td
            self.data.execute(f'ALTER TABLE {self.name_db} ADD COLUMN {td} TEXT')
            self.connection.commit()
            self.update_table()
            print('comm+')
        self.cols = self.data.execute(f'PRAGMA table_info({self.name_db})').fetchall()
        print('GEN NEW COL get new col', last_col)
        return last_col

    # функция получения цены о товаре с обновлением значения в базе
    def parsed_l(self, link):
        true_data = self.get_new_conumn()
        price = '-1,'
        url = f'https://ozon.by/product/{link}/'
        time.sleep(1)
        responce = requests.get(url)
        print(responce.status_code)
        soup = bsf4(responce.text, 'html.parser')
        try:
            if config.available_ozon_card is True:
                ozon_card_yes = soup.find(string='c Ozon Картой').parent.parent.parent.text.split('BYN')[0]
                price = ozon_card_yes
                print(price, 'yes')
            elif config.available_ozon_card is False:
                ozon_card_no = soup.find(string='без Ozon Карты').parent.parent.parent.text.split('BYN')[0]
                price = ozon_card_no
                print(price, 'no card')
            else:
                price = '-1,'
                print("Не продается или продукт недоступен")
        except requests.exceptions.RequestException as e:
            print(print(f"Ошибка при выполнении запроса: {e}"))
            price = '-1,'
        except Exception as e:
            print(e)
            phrase = r'(\d{1,4}(?:,\d{1,})*(?:\.\d{1,})?)\s*BYN'
            find_ph = re.findall(phrase, str(soup))
            if find_ph:
                price = f'same {find_ph[0]}'
                print(f"Такой товар сейчас не продается, цена аналогичного: {find_ph[0]}")
            else:
                price = '-1,'
        self.data.execute(f'UPDATE {self.name_db} SET {true_data} = ? WHERE link = ?', (price, link))
        self.connection.commit()
        # self.update_table()
        print(f'PARSED  URL: {url}, DATA: {true_data}')

    # функция обновления всех данных на текущий день
    def update_data(self):
        for i in self.links:
            print('update +', i[0])
            self.parsed_l(i[0])

    # функция удаления всей строки из таблицы
    def delete_data(self):
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        selected_items = self.table.selectedItems()
        selected_string = self.table.row(selected_items[0])
        print('del string', selected_string)
        for item in selected_items:
            print(item.text())
            row = self.table.row(item)
            col = self.table.column(item)
            print(row, col)
            self.table.takeItem(row, col)
            self.connection.execute(F'DELETE FROM {self.name_db} WHERE link = ?', (item.text(),))
            self.connection.commit()
        print('удаление работает')
        self.links = self.data.execute(f'SELECT link FROM {self.name_db}').fetchall()
        self.update_table()

    # функция сохранения изменений в базу перед закрытием программы
    def update_until_close(self):
        print('UPDATE UNTIL CLOSE')
        for row in range(len(self.links)):
            for i, column in enumerate(self.col_names):
                new_value = self.table.item(row, i).text()
                db_value = self.data.execute(
                    f'SELECT {column} FROM {self.name_db} WHERE link = ?', (self.links[row][0],)
                ).fetchall()[0][0]
                if new_value == db_value:
                    pass
                else:
                    print(f'В колонке {column} и строке {row} новое значение: {new_value}')
                    sql_query = f"UPDATE {self.name_db} SET {column} = ? WHERE link = ?"
                    self.data.execute(sql_query, (new_value, self.links[row][0]))
                    self.connection.commit()

    # функция для отображения уведомления в случае снижения цены в сравнении с предыдущим днем
    def less_price(self, string):
        if len(self.col_names) >= 3:
            try:
                print('LESS PRICE', string)
                a = float(re.findall(pattern=r'\d{0,4},\d{2}', string=string[-1])[0].replace(',', '.'))
                b = float(re.findall(pattern=r'\d{0,4},\d{2}', string=string[-2])[0].replace(',', '.'))
                if a < b:
                    print(f'Сегодня {a}. Вчера {b}')
                    if config.available_notifications is True:
                        notification(string, a, b)
                    if config.open_in_browser is True:
                        open_in_browser(string)
            except Exception as e:
                print('NOTIFICATION ERROR', e)


if __name__ == '__main__':
    file_db = 'ozon_prices.db'
    app = QApplication([])
    window = DatabaseApp(file_db)
    window.resize(800, 600)
    window.show()
    app.exec_()
