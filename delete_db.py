import sqlite3


def clear_database():
    try:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("DELETE FROM Users")
        cursor.execute("DELETE FROM WantToVisit")
        cursor.execute("DELETE FROM Visited")

        connection.commit()
        connection.close()
        print("Записи успешно удалены из базы данных.")
    except Exception as e:
        print(f"Произошла ошибка при удалении записей: {str(e)}")


if __name__ == "__main__":
    clear_database()
