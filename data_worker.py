import pandas
import pymysql
from flask import request
import json

# MySQL constants
USER_NAME = "root"
USER_PASSWORD = "Root2002"
MYSQL_PORT = 3306
MYSQL_HOST = "192.168.0.53"
DB_NAME = "users"

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