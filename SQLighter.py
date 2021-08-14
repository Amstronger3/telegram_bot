import sqlite3
from datetime import datetime, timedelta


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def exist_user(self, user_id):
        user_exist = self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        if user_exist:
            return True
        return

    def get_list_currency(self, user_id):
        with self.connection:
            data_for_user = self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()[2]
            list_currency = "\n".join((data_for_user[2:-2]).split("', '"))
        return list_currency

    def save_person_data(self, user_id, list_currencies_from_json):
        sql_request = "INSERT INTO users (user_id, json_currency, last_request) " \
                      "VALUES (?, ?, ?)"
        request_param = (int(user_id), str(list_currencies_from_json), str(datetime.now()))

        self.cursor.execute(sql_request, request_param)
        self.connection.commit()

    def update_last_request_data(self, user_id, list_currencies_from_response_json=None):

        if list_currencies_from_response_json:
            self.cursor.execute(
                "UPDATE users SET json_currency = ?, last_request = ? WHERE user_id = ?",
                (str(list_currencies_from_response_json), str(datetime.now()), user_id)
            )
        else:
            self.cursor.execute(
                "UPDATE users SET last_request = ? WHERE user_id = ?",
                (str(datetime.now()), user_id)
            )
        self.connection.commit()

    def get_last_request_time(self, user_id):
        last_time = self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()[3]
        if last_time:
            return last_time

    def is_update_currency_or_not(self, user_id):
        last_request_time = datetime.strptime(self.get_last_request_time(user_id), format("%Y-%m-%d %H:%M:%S.%f"))
        return datetime.now() > (last_request_time + timedelta(minutes=10))

    def close(self):
        self.connection.close()
