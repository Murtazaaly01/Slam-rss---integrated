import psycopg2
from psycopg2 import Error
from bot import AUTHORIZED_CHATS, SUDO_USERS, DB_URI, LOGGER

rss_dict = {}

class DbManager:
    def __init__(self):
        self.err = False

    def connect(self):
        try:
            self.conn = psycopg2.connect(DB_URI)
            self.cur = self.conn.cursor()
        except psycopg2.DatabaseError as error :
            LOGGER.error("Error in dbMang : ", error)
            self.err = True

    def disconnect(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def db_auth(self,chat_id: int):
        self.connect()
        if self.err:
            return "There's some error check log for details"
        sql = 'INSERT INTO users VALUES ({});'.format(chat_id)
        self.cur.execute(sql)
        self.disconnect()
        AUTHORIZED_CHATS.add(chat_id)
        return 'Authorized successfully'

    def db_unauth(self,chat_id: int):
        self.connect()
        if self.err:
            return "There's some error check log for details"
        sql = 'DELETE from users where uid = {};'.format(chat_id)
        self.cur.execute(sql)
        self.disconnect()
        AUTHORIZED_CHATS.remove(chat_id)
        return 'Unauthorized successfully'

    def db_addsudo(self,chat_id: int):
        self.connect()
        if self.err:
            return "There's some error check log for details"
        if chat_id in AUTHORIZED_CHATS:
            sql = 'UPDATE users SET sudo = TRUE where uid = {};'.format(chat_id)
            self.cur.execute(sql)
            self.disconnect()
            SUDO_USERS.add(chat_id)
            return 'Successfully promoted as Sudo'
        else:
            sql = 'INSERT INTO users VALUES ({},TRUE);'.format(chat_id)
            self.cur.execute(sql)
            self.disconnect()
            SUDO_USERS.add(chat_id)
            return 'Successfully Authorized and promoted as Sudo'

    def db_rmsudo(self,chat_id: int):
        self.connect()
        if self.err:
            return "There's some error check log for details"
        sql = 'UPDATE users SET sudo = FALSE where uid = {};'.format(chat_id)
        self.cur.execute(sql)
        self.disconnect()
        SUDO_USERS.remove(chat_id)
        return 'Successfully removed from Sudo'

    def init(self):
        try:
            self.connect()
            self.cur.execute("CREATE TABLE rss (name text, link text, last text, title text)")
            self.disconnect()
            LOGGER.info("Database Created.")
        except psycopg2.errors.DuplicateTable:
            LOGGER.info("Database already exists.")
            self.rss_load()

    def load_all(self):
        self.connect()
        self.cur.execute("SELECT * FROM rss")
        rows = self.cur.fetchall()
        self.disconnect()
        return rows

    def write(self, name, link, last, title):
        self.connect()
        q = [(name), (link), (last), (title)]
        self.cur.execute("INSERT INTO rss (name, link, last, title) VALUES(%s, %s, %s, %s)", q)
        self.disconnect()
        self.rss_load()

    def update(self, last, name, title):
        self.connect()
        q = [(last), (title), (name)]
        self.cur.execute("UPDATE rss SET last=%s, title=%s WHERE name=%s", q)
        self.disconnect()

    def find(self, q):
        self.connect()
        # check the database for the latest feed
        self.cur.execute("SELECT link FROM rss WHERE name = %s", q)
        feed_url = self.cur.fetchone()
        self.disconnect()
        return feed_url

    def delete(self, q):
        try:
            self.connect()
            self.cur.execute("DELETE FROM rss WHERE name = %s", q)
            self.disconnect()
        except psycopg2.errors.UndefinedTable:
            pass
        self.rss_load()

    def deleteall(self):
        self.connect()
        # clear database & dictionary
        self.cur.execute("TRUNCATE TABLE rss")
        self.disconnect()
        rss_dict.clear()
        LOGGER.info('Database deleted.')

    def rss_load(self):
        # if the dict is not empty, empty it.
        if bool(rss_dict):
            rss_dict.clear()

        for row in self.load_all():
            rss_dict[row[0]] = (row[1], row[2], row[3])
postgres = DbManager()
