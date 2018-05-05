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


def getAllHolidays(year=time.strftime("%Y"), lan="zh_cn"):
# def getAllHolidays(year=time.strftime("%Y%m%d"), lan="zh_cn"):
    data = {}
    pageUrl = "http://holidays-calendar.net/calendar_%s/china_%s.html" % (language, language)
    try:
        Response = urllib.request.urlopen(pageUrl, timeout=10)
        Html = Response.read()
    except Exception as e:
        sys.stdout.write('响应超时')
    if len(Html) > 5000:
        Html = Html.decode('utf-8')
        tableList = re.findall(rexTable, Html)
        for tableHtml in tableList:
            # print("table 长度：%s" % str(len(tableHtml)))
            # print(tableHtml[0])
            # print("%s 月" % tableHtml[1])
            tdList = re.findall(rexTd, tableHtml[0])
            months = {}
            month = "%s%s" % (year, tableHtml[1].zfill(2))
            for tdHtml in tdList:
                if tdHtml[2] != "&ensp;":
                    dayType = 1
                    if "n" == tdHtml[1]:
                        dayType = 0
                    if "suntop-hol" == tdHtml[1]:
                        dayType = 2
                    # print("%s 月 %s 日是 %s 日" % (tableHtml[1], tdHtml[2], tdHtml[1]))
                    # print("%s 月 %s 日是 %s 日" % (tableHtml[1], tdHtml[2], dayType))
                    day = "%s%s%s" % (year, tableHtml[1].zfill(2), tdHtml[2].zfill(2))
                    months[day] = dayType
            data[month] = months
        # print(data)
    return json.dumps(data)


print(getAllHolidays())
