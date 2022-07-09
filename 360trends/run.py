import base64
from PIL import Image
from io import BytesIO
import re
import requests
import datetime, time
from my_fake_useragent import UserAgent
import random
import argparse

PATHX = ""

def get_rep_json(url):
    cookie = "!!!!!!!!待填"
	
	ua = UserAgent(family='chrome')
    res = ua.random()
    headers={"User-Agent":res, "Cookie":cookie}
    response=requests.get(url=url,headers=headers)
    response_data = response.json()
    # print(response_data)
    print(url)
    n = random.randint(1, 5)
    time.sleep(n)
    return response_data

 
def yesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return yesterday
 
 
class Base4ToNumber:
    def __init__(self, q, area, fr, to):
        self.q = q
        self.area = area
        self.fr = fr
        self.to = to
 
    def get_number_for_img(self, datestr):
        global PATHX
        number_location_list = re.findall("""background-position:(.*?)['";]""", self.data_item["css"])
        number_location_int_list = [[abs(eval(x)) for x in str_location.strip().split("px") if x] for str_location in
                                    number_location_list]
 
        number = Image.new("RGBA", (200, 38), (255, 255, 255))
        for i, number_location in enumerate(number_location_int_list):
            image_number = self.image_bg.crop((number_location[0], 0, sum(number_location), self.image_bg.height))
            image_number = image_number.resize((image_number.width * 3, image_number.height * 3), Image.ANTIALIAS)
            number.paste(image_number, (i * 20, 0))
        path = PATHX + "\\" + datestr + ".png"
        # number.show()

        number.save(path)
        number.close()
        self.image_bg.close()
 
    def get_image_base4(self, index, t, datestr):
        url = f"https://trends.so.com/index/csssprite?q={self.q}&area={self.area}&from={self.fr}&to={self.to}&click={index}&t={t}"
        response_data = get_rep_json(url)
        if len(response_data["data"]) == 0:
            print(response_data)
            return ''
        self.data_item = response_data["data"][self.q]

        base4 = self.data_item["img"]
        image_data = base64.b64decode(base4.split(',')[1])
        image = Image.open(BytesIO(image_data))
        self.image_bg = image
        self.get_number_for_img(datestr)

class Trends360:
 
    def __init__(self, keywords: list, area="全国", fr="2022-05-01", to=yesterday()):
        self.q = "+".join(keywords)
        self.area = area
        self.to = to
        # self.fr_date(fr_step-1)
        self.fr = datetime.date(*map(int, fr.split('-')))
        self.number_img = Base4ToNumber(self.q, area, self.strftime(self.fr), self.strftime(to))

    @staticmethod
    def strftime(date):
        return date.strftime("%Y%m%d")
 
    def get_soIndexJson(self):
        """
        关注趋势:list
        """
        url = f"https://trends.so.com/index/soIndexJson?area={self.area}&q={self.q}&from={self.strftime(self.fr)}&to={self.strftime(self.to)}&s=0"
        response = get_rep_json(url)

        if response['status'] == 0:
            fr = self.fr
            one_step = datetime.timedelta(days=response['data']['step'])
            i = 0
            while fr < self.to:
                i += 1
                oneday = datetime.timedelta(days=1)
                to = fr + one_step - oneday
                datestr= self.strftime(fr) if response['data']['step']==1 else f"{self.strftime(fr)}-{self.strftime(to)}"
                self.number_img.get_image_base4(i, "index",datestr)
                fr += one_step
 
    def get_soMediaJson(self):
        """
        曝光量:list
        """
        url = f"https://trends.so.com/index/soMediaJson?q={self.q}&from={self.strftime(self.fr)}&to={self.strftime(self.to)}&s=0"
        response = get_rep_json(url)
 
        if response['status'] == 0:
            fr = self.fr
            one_step = datetime.timedelta(days=response['data']['step'])
            i = 0
            while fr < self.to:
                i += 1
                oneday = datetime.timedelta(days=1)
                to = fr + one_step - oneday
                datestr = self.strftime(fr) if response['data']['step']==1 else f"{self.strftime(fr)}-{self.strftime(to)}"
                self.number_img.get_image_base4(i, "media", datestr)
                fr += one_step


parser = argparse.ArgumentParser(description='360 Trends')
parser.add_argument("-kw", type=str, default="urays")
parser.add_argument("-fr", type=str, default="2022-05-01")
parser.add_argument("-area", type=str, default="全国")
args = parser.parse_args()

print(args)


# A = Trends360(["ST新亿"], "全国", "2018-05-01")
# print("ST新亿_关注趋势")
# PATHX = "ST新亿_关注趋势"
# A.get_soIndexJson()
# print("ST新亿_曝光量")
# PATHX = "ST新亿_曝光量"
# A.get_soMediaJson()

# A = Trends360(["深圳堂堂"], "全国", "2021-02-01")
# print("深圳堂堂_关注趋势")
# PATHX = "深圳堂堂_关注趋势"
# A.get_soIndexJson()
# print("深圳堂堂_曝光量")
# PATHX = "深圳堂堂_曝光量"
# A.get_soMediaJson()
