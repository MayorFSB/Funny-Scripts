from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
import sqlite3
file_db = 'ozon_prices.db'
# Создаем приложение
app = QApplication([])
window = QMainWindow()
# Создаем таблицу
table = QTableWidget(window)
connection = sqlite3.connect(file_db)
data = connection.cursor()
name_db = 'ozon'
links = data.execute(f'SELECT link FROM {name_db}').fetchall()
cols = data.execute(f'PRAGMA table_info({name_db})').fetchall()
table.setRowCount(len(links))  # Устанавливаем количество строк
table.setColumnCount(len(cols))  # Устанавливаем количество столбцов
table.setHorizontalHeaderLabels([cols[x][1] for x in range(1, len(cols))])   # Называем столбцы своими именами
for i in range(1, len(links)+1):
    h = data.execute(f'SELECT * FROM {name_db} WHERE id = ?', (i, )).fetchall()[0]
    for j in range(len(h)):
        table.setItem(i-1, j-1, QTableWidgetItem(h[j]))

con = sqlite3.connect('ozon_prices.db')
cursor = con.cursor()
d = ', '.join([f'{cols[xx][1]} TEXT' for xx in range(1, len(cols))])
cursor.execute(f"CREATE TABLE IF NOT EXISTS ozon (id INTEGER PRIMARY KEY, {d})")

col_d = [cols[x][1] for x in range(1, len(cols))]
def update_cols():
    for row in range(table.rowCount()):
        for id,column in enumerate(col_d):
            new_value = table.item(row,id).text()
            #item = QTableWidgetItem(new_value)
            print(f'В колонке {column} и строке {row} новое значение: {new_value}')
            cursor.execute(f"UPDATE ozon SET {column} = ? WHERE id = ?", (new_value, row+1))
            con.commit()

# Добавляем таблицу в окно
window.setCentralWidget(table)
# Задаем размер окна
window.resize(800, 600)
# Отображаем окно
window.show()

# Запускаем главный цикл приложения
app.exec_()
update_cols()
con.close()
