#用于发送 HTTP 请求以获取数据和向微信接口发送消息
from requests import get, post
#用于系统交互和错误处理，比如在出现错误时暂停程序并输出错误信息。
import sys, os
#用于处理日期和时间相关的操作，如获取当前日期、计算日期差值等。
from datetime import datetime, date
#用于获取本地时间信息
from time import localtime

#作用：从微信公众平台获取访问令牌（access_token）。
def get_access_token():
    app_id = config["app_id"]
    app_secret = config["app_secret"]
    url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    return access_token

#作用：获取指定地区的天气信息。
def get_weather(region):
    #实现方式：首先，使用和风天气的城市查询接口，
    # 根据传入的地区名和 API 密钥构建 URL，发送请求获取城市信息。
    # 如果响应状态码为404，表示地区名有误；如果为401，
    # 表示和风天气的 API 密钥不正确。否则，从响应中提取城市 ID。
    # 然后，使用城市 ID 和 API 密钥再次构建 URL，向和风天气的天气接口发送请求，
    # 获取该地区的天气信息，包括白天和晚上的天气描述、图标以及最高和最低温度。
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/3d?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    weather_day_text = response["daily"][0]["textDay"]
    weather_night_text = response["daily"][0]["textNight"]
    weather_day_icon = response["daily"][0]["iconDay"]
    weather_night_icon = response["daily"][0]["iconNight"]
    temp_max = response["daily"][0]["tempMax"] + u"\N{DEGREE SIGN}" + "C"
    temp_min = response["daily"][0]["tempMin"] + u"\N{DEGREE SIGN}" + "C"
    return weather_day_text, weather_day_icon, weather_night_text, weather_night_icon, temp_max, temp_min

#作用：计算给定日期距离当前日期的天数。
# 实现方式：将输入的日期字符串解析为年、月、日，
# 根据当前日期与给定日期的大小关系，确定下一个该日期的时间，
# 然后计算两个日期之间的天数差。
def get_day_left(day, year, today):
    day_year = day.split("-")[0]
    day_month = int(day.split("-")[1])
    day_day= int(day.split("-")[2])
    day_date_toyear = date(year, day_month, day_day)
    if today > day_date_toyear:
        day_date_next = date((year+1), day_month, day_day)
    elif today == day_date_toyear:
        day_date_next = today
    else:
        day_date_next = day_date_toyear
    day_left = str(day_date_next.__sub__(today)).split(" ")[0]
    if day_left == "0:00:00": day_left = 0
    return day_left

#作用：从金山词霸获取每日一句的英文和中文内容，并进行分割。
# 实现方式：向金山词霸的 API 发送请求，获取响应的 JSON 数据，
# 提取其中的 “content”（英文句子）和 “note”（中文翻译），
# 然后将它们分别平均分割为两部分。
def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    middle_en = len(note_en) // 2
    middle_ch = len(note_ch) // 2
    note_en1 = note_en[:middle_en]
    note_en2 = note_en[middle_en:]
    note_ch1 = note_ch[:middle_ch]
    note_ch2 = note_ch[middle_ch:]
    return note_en1, note_en2, note_ch1, note_ch2

#作用：向指定的微信用户发送模板消息。
def send_message(to_user, access_token, region_name, weather_day_text, weather_day_icon, weather_night_text, weather_night_icon, temp_max, temp_min, note_ch1, note_ch2, note_en1, note_en2, note_de1, note_de2):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    #日期
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    love_days_left = get_day_left(config["love_date"], year, today)
    if love_days_left == 0:
        love_days_data = "今天是纪念日哦，祝宝贝纪念日快乐！"
    else:
        love_days_data = "距离下个纪念日还有 {} 天".format(love_days_left)
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    birthday_data1 = []
    birthday_data2 = []
    for key, value in birthdays.items():
        birthday_left = get_day_left(value["birthday"], year, today)
        if birthday_left == 0:
            birthday_data1.append("今天是<{}>生日哦，".format(value["name"]))
            birthday_data2.append("祝<{}>生日快乐".format(value["name"]))
        else:
            birthday_data1.append("距离<{}>生日还有 {} 天".format(value["name"], birthday_left))
            birthday_data2.append("")
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
            },
            "region": {
                "value": region_name,
            },
            "weather_day": {
                "value": weather_day_text,
            },
            "weather_night": {
                "value": weather_night_text,
            },
            "weather_day_icon": {
                "value": "",
            },
            "weather_night_icon": {
                "value": "",
            },
            "temp_max": {
                "value": temp_max,
            },
            "temp_min": {
                "value": temp_min,
            },
            "love_day": {
                "value": love_days,
            },
            "love_day_data": {
                "value": love_days_data,
            },
            "birthday1_part1": {
                "value": "{}".format(birthday_data1[0]),
            },
            "birthday1_part2": {
                "value": "{}".format(birthday_data2[0]),
            },
            "birthday2_part1": {
                "value": "{}".format(birthday_data1[1]),
            },
            "birthday2_part2": {
                "value": "{}".format(birthday_data2[1]),
            },
            "note_ch1": {
                "value": note_ch1,
            },
            "note_ch2": {
                "value": note_ch2,
            },
            "note_en1": {
                "value": note_en1,
            },
            "note_en2": {
                "value": note_en2,
            }
            }
        }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)

if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)
 
    access_token = get_access_token()
    users = config["user"]
    region = config["region"]
    weather_day_text, weather_day_icon, weather_night_text, weather_night_icon, temp_max, temp_min = get_weather(region)
    note_en1, note_en2, note_ch1, note_ch2 = get_ciba()
    if ((config["note_ch1"] != "") or (config["note_ch2"] != "")):
        note_ch1 = config["note_ch1"]
        note_ch2 = config["note_ch2"]
    if ((config["note_en1"] != "") or (config["note_en2"] != "")):
        note_en1 = config["note_en1"]
        note_en2 = config["note_en2"]
    note_de1 = config["note_de1"]
    note_de2 = config["note_de2"]
    for user in users:
        send_message(user, access_token, region, weather_day_text, weather_day_icon, weather_night_text, weather_night_icon, temp_max, temp_min, note_ch1, note_ch2, note_en1, note_en2, note_de1, note_de2)
    os.system("pause")
