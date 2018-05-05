# coding:utf-8
import urllib.request
import re
import sys
import time
import json

language = "zh_cn"
rexBody = r'(<tbody>.*</tbody>)'
rexTable = r'(colspan="7">[A-Z]{3} \((\d{1,2}).{100,1600}</table>)'
rexTd = r'(<td class="td\-([akrsuntophl\-]{1,10})">((\&ensp;)|(\d{1,6}))</td>)'
rexYear = r'(\d{4})'


def getYearHolidays(year=time.strftime("%Y"), lan="zh_cn"):
# def getMonthHolidays(year=time.strftime("%Y%m"), lan="zh_cn"):
# def getDayHolidays(year=time.strftime("%Y%m"), lan="zh_cn"):
    data = {}
    if int(time.strftime(("%Y"))) - int(year) > 2 or int(time.strftime(("%Y"))) - int(year) < 2:
        data['error'] = "只等查 %s、%s 和 %s 年的节假日" % (
        time.strftime("%Y"), str(int(time.strftime("%Y")) - 1), str(int(time.strftime("%Y")) - 2))
        return json.dumps(data)
    url_year = "%s/" % year if time.strftime("%Y") != year else ""
    page_url = "http://holidays-calendar.net/%scalendar_%s/china_%s.html" % (url_year, lan, lan)
    print(page_url)
    try:
        response = urllib.request.urlopen(page_url, timeout=10)
        html = response.read()
    except Exception as e:
        sys.stdout.write('响应超时')
    if len(html) > 5000:
        html = html.decode('utf-8')
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
        # print(data)
    return json.dumps(data)


print(getYearHolidays("2019"))
print(getYearHolidays())
print(getYearHolidays("2017"))
print(getYearHolidays("2016"))
print(getYearHolidays("2015"))
