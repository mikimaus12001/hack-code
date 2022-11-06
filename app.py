
''' В app.py создается flask-приложение, задаются первоначальные настройки для приложения,
    создаются таблицы users и autenticate_data в mysql базе данных.
'''
#from crypt import methods
from flask import Flask, render_template, make_response, jsonify, request, redirect, session
from flask_cors import CORS, cross_origin
import pymysql
import os
import json

from themes_analyz.data_worker import *

# создать сервер Flask. Подключиться к базе данных MySQL.
app = Flask(__name__)
app.secret_key = os.urandom(24)
# разрешить CORS для Flask-сервера
CORS(app)

# MySQL constants
USER_NAME = "root"
USER_PASSWORD = "Root2002"
MYSQL_PORT = 3306
MYSQL_HOST = "192.168.0.53"
DB_NAME = "users"

# Flask constants
PORT = 5000
HOST = '0.0.0.0'

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
                                "`user_type` VARCHAR(17) NOT NULL," \
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
            insert_query_autenticate_data = "INSERT INTO `innovators`.`autenticate_data` (login, password, user_type) VALUES" \
                                            "('pys99r2210kin', 'pyskin_password', 'молодой инноватор')," \
                                            "('nic56a2210ola', 'nicola_password', 'сотрудник ДПИР');"
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
    login = request.args['login']
    password = request.args['password']
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
                #login = request.form.get('login')
                #password = request.form.get('password')

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

                    # получить тип пользователя: молодой инноватор, сотрудник ДПИР
                    dict_user_type = users[0]
                    user_type = dict_user_type['user_type']
                    json_str = json.dumps(user_type, ensure_ascii=False).encode('utf8')
                    return (json_str)
                else:
                    return json.dumps('Нет', ensure_ascii=False).encode('utf8')
                
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
    login = request.args['login']
    password = request.args['password']
    user_type = request.args['user_type']
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
                #login = request.form.get('login')
                #password = request.form.get('password')
                print('params:')
                print(login)
                print(password)
                print(user_type)

                # проверка на существование пользователя в базе
                sql = "SELECT `login` FROM `innovators`.`autenticate_data` WHERE `login` LIKE %s;"
                cursor.execute(sql, login)
                user_verify = cursor.fetchall()

                # если пользователь существует, закрыть соединение с базой
                if len(user_verify) > 0:
                    return 'found user'
                    connection.close()
                    return 'found user'

                # заполнение таблицы `users`.`autenticate_data`
                sql = "INSERT INTO `innovators`.`autenticate_data` (login, password, user_type) VALUES" \
                      "(%s, %s, %s);"

                cursor.execute(sql, (login, password, user_type))
                connection.commit()
                print('print(cursor._last_executed):')
                print(cursor._last_executed)

                # заполнение таблицы  `users`.`users`
                # получить id пользователя по его логину и паролю
                sql = "SELECT `id` FROM `innovators`.`autenticate_data` WHERE `login` LIKE %s AND `password` LIKE %s;"
                cursor.execute(sql, (login, password))
                print('print(cursor._last_executed):')
                print(cursor._last_executed)

                users = cursor.fetchall()

                if len(users) > 0:
                    print(len(users))
                    print("len(users) > 0")
                    dict_id = users[0]
                    id = dict_id['id']

                    # создать строку с id = %s в таблице `users`.`users` и заполнить строку NULL-значениями
                    sql = "INSERT INTO `innovators`.`users` (id, name, surname, vatersname, email, telephone) VALUES" \
                          "(%s, 'NULL', 'NULL', 'NULL', 'NULL', 'NULL');"
                    cursor.execute(sql, id)
                    connection.commit()
                    print('print(cursor._last_executed):')
                    print(cursor._last_executed)

                # редирект на домашнюю страницу
                sql = "SELECT `id` FROM `innovators`.`autenticate_data` WHERE `login` LIKE %s AND `password` LIKE %s;"
                cursor.execute(sql, (login, password))
                myuser = cursor.fetchall()
                print('print(cursor._last_executed):')
                print(cursor._last_executed)
                dict_id = myuser[0]
                id = dict_id['id']
                session['id'] = id

                #return redirect('/home')
                return '1'
        finally:
            connection.close()
    
    except Exception as ex:
        print("connection refused...")
        print(ex)

@app.route('/logout')
def logout():
    session.pop('id')
    return '1'

# Список модерируемых идей молодых инноваторов
# http://127.0.0.1:3200/home/ideas/mod
app.route("/home/ideas/mod", methods=['GET'])
def get_ideas():
    if 'id' in session:
        if (request.method == 'GET'):
            return getAllModIdeas()
    else:
        return '0'

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
        return '0'

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
        return '0'





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
        return '0'

# ниже пути для тестов API

#@app.route("/tests")
#def tests():
#    return render_template("endpoints_tests.html")

#@app.route("/create_idea")
#def create_idea_test():
#   return render_template("post_idea.html")

''' Весь код, который расположен после if __name__ == "__main__": выполняться не будет!
'''

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    print(type(app))
    app.run(host=HOST, port=PORT)

