import sqlite3

class SQLither:
    def __init__(self, database):
        self.conn = sqlite3.connect(database)

        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, user_name TEXT, first_name TEXT, last_name TEXT, point INT)''')

    def create_user(self, user_id, user_name, first_name, last_name, point):
        self.c.execute(
            'INSERT INTO users (user_id, user_name, first_name, last_name, point) VALUES (?, ?, ?, ?, ?)',
            (user_id, user_name, first_name, last_name, point))
        print('xx%',user_id,user_name,)
        self.conn.commit()

    def get_user(self, user_id):
        return self.c.execute(f'SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()

    def get_user_by_user_name(self, user_name):
        return self.c.execute(f'SELECT * FROM users WHERE user_name = ?', (user_name, )).fetchone()


    def set_information_user(self, user_id, item, rewards):
        self.c.execute(f'UPDATE users SET {item} = ? WHERE user_id = ?', (rewards, user_id))
        self.conn.commit()

    def update_information_user(self, user_id, item, rewards):
        self.c.execute(f'UPDATE users SET {item} = {item}+ ? WHERE user_id = ?', (rewards, user_id))
        self.conn.commit()

    def get_users(self):
        return self.c.execute(f'SELECT * FROM users').fetchall()