# coding:utf-8
import holidays
import pymysql
from datetime import datetime


def main():
    # Database information
    DB_HOST = "localhost"
    DB_USER = ""
    DB_PWD = ""
    DB_NAME = ""
    DB_CHARSET = "utf8mb4"
    db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
    cursor = db_connect.cursor()
    sql = "INSERT INTO holiday VALUES(%s, %s)"
    data = holidays.getYearHolidays(datetime.now().strftime('%Y'))
    for month in data:
        days = data[month]
        param = []
        for day in days:
            param.append([day, days[day]])
        # 批量插入
        cursor.executemany(sql, param)
    print("sf")
    db_connect.commit()
    db_connect.close()


if __name__ == '__main__':
    main()
