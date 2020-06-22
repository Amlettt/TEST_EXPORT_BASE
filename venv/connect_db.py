import psycopg2

# настройки подключенния
con = psycopg2.connect(dbname="dbplan",
                       user="user",
                       password="admin",
                       host="127.0.0.1",
                       port="5432")
cur = con.cursor()
