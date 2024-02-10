import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QLabel, \
    QLineEdit, QPushButton


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
        self.links = self.data.execute(f'SELECT link FROM {self.name_db}').fetchall()
        self.cols = self.data.execute(f'PRAGMA table_info({self.name_db})').fetchall()

        # Получаем количество строк и столбцов с именами в таблице для отрисовки
        self.table.setRowCount(len(self.links))
        self.table.setColumnCount(len(self.cols))
        self.col_names = [self.cols[x][1] for x in range(1, len(self.cols))]
        self.table.setHorizontalHeaderLabels(self.col_names)

        # Построчно отрисовываем таблицу получая данные из базы
        for i in range(1, len(self.links) + 1):
            db_string = self.data.execute(f'SELECT * FROM {self.name_db} WHERE id = ?', (i,)).fetchall()[0]
            for j in range(len(db_string)):
                self.table.setItem(i - 1, j - 1, QTableWidgetItem(db_string[j]))

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
        self.save_button.clicked.connect(self.save_value)   # noqa Cannot find reference 'connect' in 'pyqtSignal \
        self.update_button.clicked.connect(self.update_value)   # noqa | pyqtSignal | function'
        self.delete_button.clicked.connect(self.delete_value)   # noqa не знаю как исправить

    def save_value(self):
        pass

    def update_cols(self):
        for row in range(self.table.rowCount()):
            for i, column in enumerate(self.col_names):
                new_value = self.table.item(row, i).text()
                db_value = self.data.execute(
                    f'SELECT {column} FROM {self.name_db} WHERE id = ?', (row + 1,)
                ).fetchall()[0][0]
                if new_value == db_value:
                    pass
                else:
                    print(f'В колонке {column} и строке {row} новое значение: {new_value}')
                    self.data.execute(f"UPDATE {self.name_db} SET {column} = ? WHERE id = ?", (new_value, row + 1))
                    self.connection.commit()

    def update_value(self):
        pass

    def delete_value(self):
        pass

    def closeEvent(self, event):
        self.update_cols()
        event.accept()


if __name__ == '__main__':
    file_db = 'ozon_prices.db'
    app = QApplication([])
    window = DatabaseApp(file_db)
    window.resize(800, 600)
    window.show()
    app.exec_()
