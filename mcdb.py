import sqlite3
import uuid

class MinecraftDB():
    def __init__(self) -> None:
        self.conn = sqlite3.connect('./db/minecraft.db')
        self.cur = self.conn.cursor()


    def close(self) -> None:
        self.conn.close()
        self.cur.close()


    def init_db(self) -> None:
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users
                        (key TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, user_id INTEGER UNIQUE)''')
        
        self.conn.commit()


    def add_user(self, key: str, username: str) -> None:
        self.cur.execute('''INSERT INTO users (key, username)
                        VALUES (?, ?)''', (key, username))
        self.conn.commit()

    
    def link_account(self, key: str, user_id: int) -> None:
        self.cur.execute('''SELECT * from users
                        WHERE key = ?''', (key,))
        assert self.cur.fetchone()

        self.cur.execute('''UPDATE users
                        SET user_id = ?
                        WHERE key = ?''', (user_id, key))
        self.conn.commit()


    def get_key(self, username: str) -> str:
        self.cur.execute('''SELECT key from users
                        WHERE username = ?''', (username,))
        username = self.cur.fetchone()
        assert username, 'User does not exist'
        return username[0]


    def select_all(self):
        self.cur.execute('''SELECT * FROM users''')
        for e in self.cur:
            print(e)


mcdb = MinecraftDB()
mcdb.init_db()
key = str(uuid.uuid4())

#mcdb.add_user(key, 'PapaPaco')
#mcdb.link_account('aa1bbf08', 12325)
mcdb.select_all()
#print(mcdb.get_key('PapaP'))
