# coding:utf-8
import urllib.request
import re
import time
import logging

language = "zh_cn"
rexTable = r'(colspan="7">[A-Z]{3} \((\d{1,2}).{100,1600}</table>)'
rexTd = r'(<td class="td\-([akrsuntophl\-]{1,10})">((\&ensp;)|(\d{1,6}))</td>)'

logging.basicConfig(
    filename='app.log',
    format='%(asctime)s - %(module)s - %(levelname)s :  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %p',
    level=logging.ERROR
)


def getHtmlTxt(year=time.strftime("%Y"), lan="zh_cn"):
    if int(time.strftime(("%Y"))) - int(year) > 2 or int(time.strftime(("%Y"))) - int(year) < 0:
        logging.warning("只等查 %s、%s 和 %s 年的节假日" % (
            time.strftime("%Y"), str(int(time.strftime("%Y")) - 1), str(int(time.strftime("%Y")) - 2)))
        return
    url_year = "%s/" % year if time.strftime("%Y") != year else ""
    page_url = "http://holidays-calendar.net/%scalendar_%s/china_%s.html" % (url_year, lan, lan)
    logging.debug("爬取地址: %s" % page_url)
    try:
        response = urllib.request.urlopen(page_url, timeout=10)
        html = response.read()
    except Exception as e:
        logging.error(e)
        return
    if len(html) > 5000:
        return html.decode('utf-8')
    return


def getYearHolidays(year=time.strftime("%Y"), lan="zh_cn"):
    data = {}
    html = getHtmlTxt(year, lan)
    if html is None:
        return
    table_list = re.findall(rexTable, html)
    for tableHtml in table_list:
        td_list = re.findall(rexTd, tableHtml[0])
        months = {}
        month = "%s%s" % (year, tableHtml[1].zfill(2))
        for tdHtml in td_list:
            if tdHtml[2] != "&ensp;":
                day_type = 1
                if "n" == tdHtml[1]:
                    day_type = 0
                if "suntop-hol" == tdHtml[1]:
                    day_type = 2
                day = "%s%s%s" % (year, tableHtml[1].zfill(2), tdHtml[2].zfill(2))
                months[day] = day_type
        data[month] = months
    return data


def getMonthHolidays(month=time.strftime("%Y%m"), lan="zh_cn"):
    year = month[0:4]
    data = getYearHolidays(year, lan)
    if len(data) == 0:
        return
    return data[month]


def getDayHoliday(day=time.strftime("%Y%m%d"), lan="zh_cn"):
    month = day[0:6]
    data = getMonthHolidays(month, lan)
    if data is None:
        return
    return data[day]
