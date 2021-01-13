import sqlite3
from bot_types import Task, User


class DBController:
    """ A class for controlling the database"""

    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def get_user(self, user_id):
        self.cursor.execute(
            "SELECT * FROM users WHERE id = '{}';".format(user_id)
        )
        obj = self.cursor.fetchone()
        if obj:
            return User(*obj)
        else:
            return None

    def subscribe(self, user_id):
        self.cursor.execute(
            f"UPDATE users SET notifies = True where id = {user_id};"
        )
        self.connection.commit()

    def unsubscribe(self, user_id):
        self.cursor.execute(
            f"UPDATE users SET notifies = False WHERE id = {user_id};"
        )
        self.connection.commit()

    def add_account(self, user_id):
        self.cursor.execute(
            f"INSERT INTO users VALUES({user_id}, False, True, 0, 0);"
        )

        self.connection.commit()

    def add_task(self, user_id, name):
        self.cursor.execute(
            f"INSERT INTO tasks VALUES({user_id}, '{name}', False)"
        )
        self.connection.commit()

    def remove_task(self, user_id, name):
        self.cursor.execute(
            f"DELETE FROM tasks WHERE user_id = {user_id} AND taskname = '{name}';"
        )
        self.connection.commit()

    def get_tasks(self, user_id):
        self.cursor.execute(
            f"SELECT * FROM tasks WHERE user_id = {user_id}"
        )

        return [Task(*i) for i in self.cursor.fetchall()]

    def get_task(self, user_id, name):
        self.cursor.execute(f"SELECT * FROM tasks WHERE user_id = {user_id} and taskname = '{name}'")
        try:
            return Task(*self.cursor.fetchone())
        except TypeError:
            return None

    def change_task_status(self, user_id, name):
        status = str(False if self.get_task(user_id, name).is_completed else True)
        self.cursor.execute(
            f"UPDATE tasks SET completed = {status} WHERE user_id = {user_id} and taskname = '{name}';"
        )

        self.connection.commit()

    def change_notifies_status(self, user_id):
        user = self.get_user(user_id)
        status = "False" if user.notifies else "True"
        self.cursor.execute(f"UPDATE users SET notifies = {status} where id = {user_id}")
        self.connection.commit()

    def change_extend_status(self, user_id):
        user = self.get_user(user_id)
        status = "False" if user.extend_task else "True"
        self.cursor.execute(f"UPDATE users SET extend_task = {status} where id = {user_id}")
        self.connection.commit()

    def get_all_users(self):
        self.cursor.execute("SELECT * from users")
        return [User(*user) for user in self.cursor.fetchall()]

    def delete_all_tasks(self, user_id):
        self.cursor.execute(f"DELETE from tasks WHERE user_id = {user_id}")
        self.connection.commit()
