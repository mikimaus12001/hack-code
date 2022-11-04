
''' В app.py создается flask-приложение, задаются первоначальные настройки для приложения,
    создаются таблицы users и autenticate_data в mysql базе данных.
'''
#from crypt import methods
from flask import Flask, render_template, make_response, jsonify, request, redirect, session
from flask_cors import CORS, cross_origin
import pymysql
import os


# _________________________________________________________________________________________________________________
# ___________________________________________________data_worker.py________________________________________________
# ________________________________________________________START____________________________________________________

import json
import pandas

# MySQL constants
USER_NAME = "root"
USER_PASSWORD = "root"
MYSQL_PORT = 3306
MYSQL_HOST = "127.0.0.1"
DB_NAME = "users"

# Flask constants
PORT = 5000
HOST = '0.0.0.0'

# путь до хранилища данных
data_store = 'E:/python_project/test_project/themes_analyz/excel_data/Датасет. Задача 1.xlsx'
#column = 'Проект'
#key = 'Хакатоны и цифровые конкурсы'

# write data into CSV file
#read_file.to_csv (data_store, index = None, header=True)

# getData вытаскивает определенные данные из Excel-файла, преобразует данные в json
# param: column
# param: key
def getExcelData(column, key):
    # Convert Excel file to CSV file using the pandas library
    # read and store content of Excel file
    read_file = pandas.read_excel (data_store)

    # получить все строки excel-файла, где Проект = Хакатоны и цифровые конкурсы, где param в head(param) отвечает
    # за количество строк, которое хотим получить
    sheet = (read_file[read_file[column] == key].head(100))
    #print(sheet)

    # convert data to json
    # force_ascii=False поддерживает utf-8
    # orient='split' разбивает данные на json-объекты
    json_str = sheet.to_json(orient='split', force_ascii=False)
    #print(json_str)

    return json_str

#getExcelData(column, key)

# Получить все идеи молодых инноваторов на модерации
# /home/ideas/mod

def getAllModIdeas():
    try:
        connection = pymysql.connect(
            host = MYSQL_HOST,
            port = MYSQL_PORT,
            user = USER_NAME,
            password = USER_PASSWORD,
            #database = DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
        )

        print("successfully connected...")
        print("#" * 20)

        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `innovators`.`contests`"
                cursor.execute(sql)
                list_contests = cursor.fetchall()
                print(list_contests)

                sql = "SELECT * FROM `innovators`.`nominations`"
                cursor.execute(sql)
                list_nominations = cursor.fetchall()
                print(list_nominations)

                sql = "SELECT * FROM `innovators`.`ideas`"
                cursor.execute(sql)
                list_ideas = cursor.fetchall()
                print(list_ideas)

                sql = "SELECT * FROM `innovators`.`ideas_has_nominations`"
                cursor.execute(sql)
                list_ideas_has_nominations = cursor.fetchall()
                print(list_ideas_has_nominations)

                sql = "SELECT * FROM `innovators`.`status`"
                cursor.execute(sql)
                list_ideas_status = cursor.fetchall()
                print(list_ideas_status)

                return (json_str)

        finally:
            connection.close()

    except Exception as ex:
        print("connection refused...")
        print(ex)

# Фильтр идей молодых инноваторов
# get data from MySQL database
# REST API endpoint:
# /home/ideas/mod/filter
def getMySQLData(contest, nomination):
    try:
        connection = pymysql.connect(
            host = MYSQL_HOST,
            port = MYSQL_PORT,
            user = USER_NAME,
            password = USER_PASSWORD,
            #database = DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
        )

        print("successfully connected...")
        print("#" * 20)

        try:
            with connection.cursor() as cursor:
                #contest = request.form.get('contest')
                #nomination = request.form.get('nomination')

                ''' SQL Queries
                '''
                # Get ID of Contest
                # Получаем словарь {}
                # Например: {'id_Contests': 1}
                sql_query_01 = "SELECT `id_Contests` FROM `innovators`.`contests` WHERE `name_Contests` LIKE %s;"
                
                cursor.execute(sql_query_01, contest)

                id_contest = cursor.fetchone()

                # Get ID of Nomination
                # Получаем список
                # Например: [{'id_Nominations': 1}]
                sql_query_02 = "SELECT `id_Nominations` FROM `innovators`.`nominations` WHERE `name_Nominations` LIKE %s;"
                cursor.execute(sql_query_02, nomination)

                list_id_nomination = cursor.fetchall()
                dict_id_nomination = list_id_nomination[0]
                id_nomination = dict_id_nomination['id_Nominations']

                # Get List of ideas' IDs
                sql_query_03 = "SELECT * FROM `innovators`.`ideas_has_nominations` WHERE `Nominations_id_Nominations` LIKE %s;"
                cursor.execute(sql_query_03, id_nomination)

                # Получаем список словарей: [{...}, {...}, {...}, ...]
                # Например: [{'Ideas_id_Ideas': 1, 'Nominations_id_Nominations': 1}, {'Ideas_id_Ideas': 2, 'Nominations_id_Nominations': 1}, {'Ideas_id_Ideas': 3, 'Nominations_id_Nominations': 1}]
                list_id_ideas = cursor.fetchall()
                
                # Список ID идей
                # Получить список с ID идей
                # Например: [1, 2, 3]
                list_ids_ideas_values = []

                for i in range(len(list_id_ideas)):
                    dict_i = list_id_ideas[i]
                    idea_id = dict_i['Ideas_id_Ideas']
                    list_ids_ideas_values.append(idea_id)

                # Получить идеи по их ID
                # ORM: сформировать структуру, удобную для отправки в json
                # [{contest, nomination, idea},
                #  {contest, nomination, idea},
                #  {contest, nomination, idea},
                # ]
                # Например: [{'name_Ideas': 'Экологический мониторинг атмосферного воздуха'},
                #            {'name_Ideas': 'Облачный сервис мониторинга и управления бортовыми системами транспортных средств'},
                #            {'name_Ideas': 'Платформа тестирования и повышения уровня цифровой грамотности'}
                #           ]
                list_mod_ideas = []

                for i in list_ids_ideas_values:
                    sql = "SELECT `name_Ideas` FROM `innovators`.`ideas` WHERE `id_Ideas` LIKE %s;"
                    cursor.execute(sql, i)
                    dict_with_idea = cursor.fetchone()
                    list_mod_ideas.append(dict_with_idea)
                
                # сериализация данных в json в UTF-8
                json_str = json.dumps(list_mod_ideas, ensure_ascii=False).encode('utf8')

                return(json_str)

        finally:
            connection.close()

    except Exception as ex:
        print("connection refused...")
        print(ex)

# получить список категорий
def getCategories():
    try:
        connection = pymysql.connect(
            host = MYSQL_HOST,
            port = MYSQL_PORT,
            user = USER_NAME,
            password = USER_PASSWORD,
            #database = DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
        )

        print("successfully connected...")
        print("#" * 20)

        try:
            with connection.cursor() as cursor:
                ''' SQL Queries
                '''
                sql = "SELECT `name_Category` FROM innovators.category;"
                cursor.execute(sql)
                list_of_categories = cursor.fetchall()

                # сериализация данных в json в UTF-8
                json_str = json.dumps(list_of_categories, ensure_ascii=False).encode('utf8')

                return (json_str)
        finally:
            connection.close()

    except Exception as ex:
        print("connection refused...")
        print(ex)

# добавить новую категорию
def createCategory(category):
    try:
        connection = pymysql.connect(
            host = MYSQL_HOST,
            port = MYSQL_PORT,
            user = USER_NAME,
            password = USER_PASSWORD,
            #database = DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
        )

        print("successfully connected...")
        print("#" * 20)

        try:
            with connection.cursor() as cursor:
                ''' SQL Queries
                '''
                sql = "INSERT INTO `innovators`.`category` (name_Category) VALUES" \
                      "(%s);"
                cursor.execute(sql, category)
                connection.commit()

                # сериализация данных в json в UTF-8
                json_str = json.dumps("data to table `innovators`.`category` INSERT successfully", ensure_ascii=False).encode('utf8')

                return (json_str)
        finally:
            connection.close()

    except Exception as ex:
        print("connection refused...")
        print(ex)

# удалить категорию
def deleteCategory(category):
    try:
        connection = pymysql.connect(
            host = MYSQL_HOST,
            port = MYSQL_PORT,
            user = USER_NAME,
            password = USER_PASSWORD,
            #database = DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
        )

        print("successfully connected...")
        print("#" * 20)

        try:
            with connection.cursor() as cursor:
                ''' SQL Queries
                '''
                sql = "DELETE FROM `innovators`.`category` WHERE `name_Category` LIKE %s;"
                cursor.execute(sql, category)
                connection.commit()

                # сериализация данных в json в UTF-8
                json_str = json.dumps("Category in `innovators`.`category` DELETE successfully", ensure_ascii=False).encode('utf8')

                return (json_str)
        finally:
            connection.close()

    except Exception as ex:
        print("connection refused...")
        print(ex)

# создать идею
def createIdea(innovator_id, name, contest, nomination):
    try:
        connection = pymysql.connect(
            host = MYSQL_HOST,
            port = MYSQL_PORT,
            user = USER_NAME,
            password = USER_PASSWORD,
            #database = DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
        )

        print("successfully connected...")
        print("#" * 20)

        try:
            with connection.cursor() as cursor:
                ''' SQL Queries
                '''
                # вставить имя идеи и ID молодого инноватора
                sql = "INSERT INTO `innovators`.`ideas` (name_Ideas, id_innovator) VALUES" \
                      "(%s, %s);"
                cursor.execute(sql, (name, innovator_id))
                connection.commit()

                # получить ID идеи
                sql = "SELECT `id_Ideas` FROM `innovators`.`ideas` WHERE `name_Ideas` LIKE %s AND `id_innovator` LIKE %s;"
                cursor.execute(sql, (name, innovator_id))
                dict_idea_id = cursor.fetchone() # {id_Ideas': '34'}
                value_idea_id = dict_idea_id['id_Ideas']
                print(type(value_idea_id))

                # получить ID номинации по ее имени
                sql = "SELECT `id_Nominations` FROM `innovators`.`nominations` WHERE `name_Nominations` LIKE %s;"
                cursor.execute(sql, nomination)
                dict_nomination_id = cursor.fetchone() # {'id_Nominations': '1'}
                value_nomination_id = dict_nomination_id['id_Nominations']
                print(type(value_nomination_id))


                # вставить ID идеи и ID номинации
                sql = "INSERT INTO `innovators`.`ideas_has_nominations` (Ideas_id_Ideas, Nominations_id_Nominations) VALUES" \
                      "(%s, %s);"
                cursor.execute(sql, (value_idea_id, value_nomination_id))
                connection.commit()

        finally:
            connection.close()

    except Exception as ex:
        print("connection refused...")
        print(ex)


# _________________________________________________________________________________________________________________
# ___________________________________________________data_worker.py________________________________________________
# ________________________________________________________END______________________________________________________





#from themes_analyz.data_worker import *

# создать сервер Flask. Подключиться к базе данных MySQL.
app = Flask(__name__)
app.secret_key = os.urandom(24)
# разрешить CORS для Flask-сервера
CORS(app)



# App path
#APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#TEMPLATE_PATH = os.path.join(APP_PATH, 'templates/')

try:
    connection = pymysql.connect(
        #host = "flask_db",
        host = MYSQL_HOST,
        port = MYSQL_PORT,
        user = USER_NAME,
        password = USER_PASSWORD,
 #       database = DB_NAME,
        cursorclass = pymysql.cursors.DictCursor
    )

    print("successfully connected...")
    print("#" * 20)

    try:
        with connection.cursor() as cursor:
            #connection.cursor().execute("CREATE SCHEMA `users` ;")
            create_table_query ="CREATE TABLE `innovators`.`autenticate_data` (" \
                                "`id` INT NOT NULL AUTO_INCREMENT," \
                                "`login` VARCHAR(32) NOT NULL," \
                                "`password` VARCHAR(32) NOT NULL," \
                                "PRIMARY KEY (`id`));"
            cursor.execute(create_table_query)
            print(cursor._last_executed)
            print("table `innovators`.`autenticate_data` created successfully")

            create_table_query ="CREATE TABLE `innovators`.`users` (" \
                                "`id` INT NOT NULL AUTO_INCREMENT," \
                                "`name` VARCHAR(32)," \
                                "`surname` VARCHAR(32)," \
                                "`vatersname` VARCHAR(32)," \
                                "`email` VARCHAR(50)," \
                                "`telephone` VARCHAR(20)," \
                                "FOREIGN KEY (id) REFERENCES `autenticate_data` (`id`));"
            cursor.execute(create_table_query)
            print(cursor._last_executed)
            print("table `innovators`.`users` created successfully")

            # INSERT DATA
            insert_query_autenticate_data = "INSERT INTO `innovators`.`autenticate_data` (login, password) VALUES" \
                                            "('pys99r2210kin', 'pyskin_password')," \
                                            "('nic56a2210ola', 'nicola_password');"
            cursor.execute(insert_query_autenticate_data)
            connection.commit()
            print("data to table `innovators`.`autenticate_data` INSERT successfully")

            insert_query_users ="INSERT INTO `innovators`.`users` (name, surname, vatersname, email, telephone) VALUES" \
                                "('Александр', 'Пушкин', 'Сергеевич', 'alekpyskin@mail.ru', '+7(916)564-06-47')," \
                                "('Никола', 'Тесла', 'Милутинович', 'nicolatecla@mail.ru', '+49(455)544-09-06');"
            cursor.execute(insert_query_users)
            connection.commit()
            print("data to table `innovators`.`users` INSERT successfully")

    finally:
        connection.close()
except Exception as ex:
    print("connection refused...")
    print(ex)


# GET METHOD
@app.route("/")
def index():
    #return render_template('index.html')
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login_page.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/home")
def home():
    if 'id' in session:
        return render_template('home.html')
    else:
        return redirect('/')

@app.route("/login_validation", methods=['POST'])
def login_validation():
    try:
        connection = pymysql.connect(
            #host = "flask_db",
            host = MYSQL_HOST,
            port = MYSQL_PORT,
            user = USER_NAME,
            password = USER_PASSWORD,
            #database = DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
        )

        print("successfully connected...")
        print("#2" * 20)

        try:
            with connection.cursor() as cursor:
                login = request.form.get('login')
                password = request.form.get('password')

                #cursor.execute("SELECT * FROM `users`.`autenticate_data`;")
                #cursor.execute("SELECT * FROM `users`.`autenticate_data` WHERE `login` LIKE '{}' AND `password` LIKE '{}';").format(login, password)
                #cursor.execute("SELECT * FROM `users`.`autenticate_data` WHERE `login` LIKE '{login}' AND `password` LIKE '{password}';")
                sql = "SELECT * FROM `innovators`.`autenticate_data` WHERE `login` LIKE %s AND `password` LIKE %s;"
                #cursor.execute(sql % login % password)
                #cursor.execute(sql, {"login": login, "password": password})
                cursor.execute(sql, (login, password))

                users = cursor.fetchall()

                if len(users) > 0:
                    # создание сессии
                    dict_id = users[0]
                    id = dict_id['id']
                    session['id'] = id
                    return redirect('/home')
                else:
                    return redirect('/')
                
                #print(users)
                #str_users = str(users)
                #return str_users
                #return "SELECT * FROM `users`.`autenticate_data` WHERE `login` LIKE {} AND `password` LIKE {};".format(login, password)
        finally:
            connection.close()

    except Exception as ex:
        print("connection refused...")
        print(ex)

@app.route('/add_user', methods=['POST'])
def add_user():
    ''' Таблица `innovators`.`users` заполняется после таблицы `innovators`.`autenticate_data`, т.к.
    таблица `innovators`.`users` содержит FOREIGN KEY [id] на PRIMARY KEY [id] в таблице `innovators`.`autenticate_data`
    '''
    try:
        connection = pymysql.connect(
            #host = "flask_db",
            host = MYSQL_HOST,
            port = MYSQL_PORT,
            user = USER_NAME,
            password = USER_PASSWORD,
            #database = DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
        )

        print("successfully connected...")
        print("#3" * 20)

        try:
            with connection.cursor() as cursor:
                login = request.form.get('login')
                password = request.form.get('password')

                # заполнение таблицы `users`.`autenticate_data`
                sql = "INSERT INTO `innovators`.`autenticate_data` (login, password) VALUES" \
                      "(%s, %s);"

                cursor.execute(sql, (login, password))
                connection.commit()

                # заполнение таблицы  `users`.`users`
                # получить id пользователя по его логину и паролю
                sql = "SELECT `id` FROM `innovators`.`autenticate_data` WHERE `login` LIKE %s AND `password` LIKE %s;"
                cursor.execute(sql, (login, password))

                users = cursor.fetchall()

                if len(users) > 0:
                    dict_id = users[0]
                    id = dict_id['id']

                    # создать строку с id = %s в таблице `users`.`users` и заполнить строку NULL-значениями
                    sql = "INSERT INTO `innovators`.`users` (id, name, surname, vatersname, email, telephone) VALUES" \
                          "(%s, 'NULL', 'NULL', 'NULL', 'NULL', 'NULL');"
                    cursor.execute(sql, id)
                    connection.commit()

                # редирект на домашнюю страницу
                sql = "SELECT `id` FROM `innovators`.`autenticate_data` WHERE `login` LIKE %s AND `password` LIKE %s;"
                cursor.execute(sql, (login, password))
                myuser = cursor.fetchall()
                dict_id = myuser[0]
                id = dict_id['id']
                session['id'] = id

                return redirect('/home')
        finally:
            connection.close()
    
    except Exception as ex:
        print("connection refused...")
        print(ex)

@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')

# Список модерируемых идей молодых инноваторов
# http://127.0.0.1:3200/home/ideas/mod
app.route("/home/ideas/mod", methods=['GET'])
def get_ideas():
    if 'id' in session:
        if (request.method == 'GET'):
            return getAllModIdeas()
    else:
        return redirect('/')

# Фильтр идей молодых инноваторов
# http://127.0.0.1:3200/home/ideas/mod/filter?contest=Новатор Москвы&nomination=Лидеры инноваций
@app.route("/home/ideas/mod/filter", methods=['GET'])
def ideas_data():
    if 'id' in session:
        if (request.method == 'GET'):
            arg1 = request.args['contest']
            arg2 = request.args['nomination']
            return getMySQLData(arg1, arg2)
    else:
        return redirect('/')

# получить список категорий / создать категорию / удалить категорию
# [GET] http://127.0.0.1:3200/home/ideas/category
# Пример response body: [{"name_Category": "инновационная"},
#                        {"name_Category": "неинновационная"},
#                        {"name_Category": "плагиат"},
#                        {"name_Category": "нецензурная речь"},
#                        {"name_Category": "шлак"}]
@app.route("/home/ideas/category", methods = ['GET', 'POST', 'DELETE'])
def category():
    if 'id' in session:
        if (request.method == 'GET'):
            return getCategories()
        if (request.method == 'POST'):
            arg = request.args['create']
            return createCategory(arg)
        if (request.method == 'DELETE'):
            arg = request.args['delete']
            return deleteCategory(arg)
    else:
        return redirect('/')





''' =--------------------- МОЛОДОЙ ИННОВАТОР -------------------------------
'''

# Создать идею
# ID инноватора отправляется серверу как параметр запроса POST, поэтому, при входе в ЛК,
# ID инноватора должен сохраняться на стороне клиента.
# http://127.0.0.1:3200/home/ideas/create?innovator_id=1&name=супер идея космического дирижабля&contest=Новатор Москвы&nomination=Лидеры инноваций
@app.route("/home/ideas/create", methods = ['POST'])
def create_idea():
    if 'id' in session:
        if (request.method == 'POST'):
            arg1 = request.args['innovator_id']
            arg2 = request.args['name']
            arg3 = request.args['contest']
            arg4 = request.args['nomination']
            return (createIdea(arg1, arg2, arg3, arg4))
    else:
        return redirect('/')

# ниже пути для тестов API

@app.route("/tests")
def tests():
    return render_template("endpoints_tests.html")

@app.route("/create_idea")
def create_idea_test():
    return render_template("post_idea.html")

''' Весь код, который расположен после if __name__ == "__main__": выполняться не будет!
'''

if __name__ == "__main__":
    print("Server running in host %s"%(HOST))
    print("Server running in port %s"%(PORT))
    print(type(app))
    app.run(host=HOST, port=PORT)

