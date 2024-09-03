import sqlite3
import datetime

con = sqlite3.connect("Publisher.db")
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS publisher")
cur.execute("CREATE TABLE IF NOT EXISTS publisher (name TEXT, days INT, next_time TEXT, target_chat_id INT, postmail_chat_id INT, second_chatid INT, postmail_message_id INT, second_messageid INT, origin_userid INT)")
con.commit()

current_time = datetime.datetime.now()
now = datetime.datetime(current_time.year, current_time.month, current_time.day, 12, 30, current_time.second) + datetime.timedelta(days=1)
cur.execute(f"INSERT INTO publisher VALUES ('test', 1, '{now}', 69420, 123456789, 987654321, 123456789, 987654321, 123456789)")
con.commit()

cur.execute("SELECT * FROM publisher")
for row in cur:
    for elem in row:
        print(elem)
con.close()
