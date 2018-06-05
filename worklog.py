# coding:utf-8
import requests
import json
import pytz
import random
import time
import holidays
import logging
from datetime import datetime


LOGIN_URL = "http://your_ipworklog/app/common/welcome?username={}&password={}"
ADD_LOG_URL = "http://your_ipworklog/app/worklog/myself/log/add?workTime={}&projectId={}&isWorkday=0&hours=8.0&content="
LOGOUT_URL = "http://your_ipworklog/app/common/logout"
DELETE_LOG_URL = "http://your_ipworklog/app/worklog/myself/log/del?ids={}&_={}"
LAST_3_LOG_URL = "http://your_ipworklog/app/worklog/myself/log/manage?page=1&rows=3"
TIME_ZONE = pytz.timezone('Asia/Shanghai')
TODAY = datetime.now(TIME_ZONE).strftime('%Y-%m-%d')

logging.basicConfig(
    filename='app.log',
    format='%(asctime)s - %(module)s - %(levelname)s :  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %p',
    level=logging.DEBUG
)


# 是否下午
def off_duty():
    hour = datetime.now(TIME_ZONE).strftime('%H')
    if int(hour) < 12:
        return False
    else:
        return True


class User:
    start_flag = False
    end_flag = False

    def __init__(self, name, pwd, agent, projectid, start, end):
        self.name = name
        self.pwd = pwd
        self.headers = {'Content-Type': 'text/html;charset=utf-8', 'User-Agent': agent}
        self.project_id = projectid
        self.work_start = TODAY + ' ' + start
        self.work_end = TODAY + ' ' + end
        self.start_time = time.mktime(time.strptime(self.work_start, '%Y-%m-%d %H:%M:%S')) - (
            int(random.uniform(500, 1800)))
        self.end_time = time.mktime(time.strptime(self.work_end, '%Y-%m-%d %H:%M:%S')) + (
            int(random.uniform(500, 1800)))
        self.start_flag = False
        self.end_flag = False
        self.session = requests.Session()
        self.ids = []

    # 登录系统
    def log_in(self):
        try:
            response = self.session.post(LOGIN_URL.format(self.name, self.pwd), headers=self.headers, timeout=20)
            return True
        except Exception as e:
            logging.error("登陆报错:")
            logging.error(e)
            return False

    # 登出系统
    def log_out(self):
        try:
            response = self.session.get(LOGOUT_URL, headers=self.headers, timeout=20)
            return True
        except Exception as e:
            logging.error("登出报错:")
            logging.error(e)
            return False

    # 添加日志
    def add_log(self):
        try:
            response = self.session.post(ADD_LOG_URL.format(TODAY, self.project_id), headers=self.headers, timeout=20)
            response.encoding = 'utf-8'
            result = json.loads(response.text)
            if result['result'] == 'success':
                logging.info(result['message'])
                return True
            return False
        except Exception as e:
            logging.error("添加日志报错:")
            logging.error(e)
            return False

    # 删除日志
    def delete_log(self, delete_id):
        tamp = str(int(round(time.time() * 1000)))
        try:
            response = self.session.get(DELETE_LOG_URL.format(delete_id, tamp), headers=self.headers, timeout=20)
            response.encoding = 'utf-8'
            result = json.loads(response.text)
            if result['result'] == 'success':
                logging.info(result['message'])
                return True
            logging.warning("删除日志 " + delete_id + " 失败")
            return False
        except Exception as e:
            logging.error("删除日志报错:")
            logging.error(e)
            return False

    # 检查最后三个日志,删除任意一条空日志则返回成功
    def check_last_3_log(self):
        try:
            response = self.session.post(LAST_3_LOG_URL, headers=self.headers, timeout=20)
            response.encoding = 'utf-8'
            result = json.loads(response.text)
            rows = result['rows']
            for i in rows:
                content = i['content']
                if len(content) == 0:
                    logging.info("删除空日志 %s: %s" % (i['id'], content))
                    if self.delete_log(i['id']):
                        return True
            return False
        except Exception as e:
            logging.error("获取日志报错:")
            logging.error(e)
            return False

    # 打卡
    def punch_clock(self):
        afternoon = off_duty()
        cur_time = time.mktime(
            time.strptime(datetime.now(TIME_ZONE).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
        if afternoon:
            if cur_time > self.end_time:
                if not self.log_in():
                    return False
                if not self.add_log():
                    self.log_out()
                    return False
                if not self.check_last_3_log():
                    self.log_out()
                    return False
                self.log_out()
                return True
            else:
                return False
        else:
            if cur_time > self.start_time:
                if not self.log_in():
                    return False
                self.log_out()
                return True
            else:
                return False


def main():
    bjj = User("user1_name", "user1_pwd",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
               "4384d4d379d24c7fb536694590fe33a8", '09:00:00', '18:00:00')
    mjx = User("user2_name", "user2_pwd",
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
               "85b1937d8d2b4e458f2bffc37638146a", '09:00:00', '18:00:00')

    user_list = {bjj, mjx}

    # 判断是否工作日，0:工作日；1:休息日；2:法定节假日
    cur_day = holidays.getDayHoliday(TODAY.replace('-', ''))
    while cur_day is None:
        logging.warning("工作日信息获取失败，重新获取")
        cur_day = holidays.getDayHoliday(TODAY.replace('-', ''))

    if cur_day != 0:
        logging.info("不是工作日，直接退出")
        return

        # 退出标记
    is_exit = False

    while not is_exit:
        is_exit = True
        for u in user_list:
            # logging.debug(u.start_time)
            # logging.debug(u.end_time)
            if not u.end_flag and u.punch_clock():
                u.end_flag = True

            if not u.end_flag:
                is_exit = False

        time.sleep(int(random.uniform(40, 80)))

    if off_duty():
        logging.info("下班签退完成")
    else:
        logging.info("上班签到完成")


if __name__ == '__main__':
    main()

# print(pytz.country_timezones('cn'))
# a = datetime.now(TIME_ZONE).strftime("%Y-%m-%d %H:%M:%S")
