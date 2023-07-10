
import MySQLdb

db = MySQLdb.connect(host="хост", user="имя_позьзователя", passwd="пароль", db="название_бд", charset='utf8')

cursor = db.cursor()
print(cursor)
class DB:
    
    @staticmethod
    def get_by_id(user_id,phone,curier):
        sql =cursor.execute("""SELECT * FROM название_таблицы WHERE phone = ('%(phone)s')"""%{"phone":phone})
        result=cursor.fetchall()
        print(result)
        if len(result) == 0: 
            sql = """INSERT INTO название_таблицы (id_chat, phone, curier)  VALUES  ('%(id_chat)s', '%(phone)s', '%(curier)s')"""%{"id_chat":user_id,"phone":phone, "curier":curier}
            cursor.execute(sql)
            print(cursor.execute(sql))
            db.commit()
    
             
    @staticmethod
    def proverk_id(chat):
        sql =cursor.execute("""SELECT * FROM название_таблицы WHERE id_chat = ('%(id_chat)s')"""%{"id_chat":chat})
        #cursor.execute(sql)
        
        result=cursor.fetchall()        
        if len(result) == 0:
            return False
        else:
            for row in result:
                id_cur=row[3]
                return id_cur
       #print(cursor.execute(sql)) 
