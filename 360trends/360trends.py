import base64
from PIL import Image
from io import BytesIO
import re
import requests
import datetime, time
from my_fake_useragent import UserAgent
import random
import argparse
import os

def get_rep_json(url):
    cookie = "QiHooGUID=56E17FD737B5B69B6488EE088E991345.1653136999673; __guid=210905680.3622796060561407000.1653136997259.949; Q=u=360H3372129794&n=henlf&le=&m=ZGt4WGWOWGWOWGWOWGWOWGWOZGZ1&qid=3372129794&im=1_t01d7ad37f80ff04d7a&src=pcw_360index_weixin&t=1; __NS_Q=u=360H3372129794&n=henlf&le=&m=ZGt4WGWOWGWOWGWOWGWOWGWOZGZ1&qid=3372129794&im=1_t01d7ad37f80ff04d7a&src=pcw_360index_weixin&t=1; T=s=8fc2f1ded9f447acec7558343b9b7224&t=1653183520&lm=&lf=&sk=84dd9063defa4685acacbd9ee81a8f9b&mt=1653183520&rc=&v=2.0&a=0; __NS_T=s=8fc2f1ded9f447acec7558343b9b7224&t=1653183520&lm=&lf=&sk=84dd9063defa4685acacbd9ee81a8f9b&mt=1653183520&rc=&v=2.0&a=0; _S=179d47370b4cc4fe99f53714a3791243; __bn=OBSO{OxnBwx$/$VBKVQFx<>t>R3q/L,n+,U3p.dw(oOXS)4T{1<Dz,g>}QYSGQ@J$?M)fR^o0|,sTlSeo#^Aq8/ZTW2WE?9UuE%Hr2kD_rcyU*NX5v_; count=24; test_cookie_enable=null"
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
 
    def get_number_for_img(self, path):
        global PATHX
        number_location_list = re.findall("""background-position:(.*?)['";]""", self.data_item["css"])
        number_location_int_list = [[abs(eval(x)) for x in str_location.strip().split("px") if x] for str_location in
                                    number_location_list]
 
        number = Image.new("RGBA", (200, 38), (255, 255, 255))
        for i, number_location in enumerate(number_location_int_list):
            image_number = self.image_bg.crop((number_location[0], 0, sum(number_location), self.image_bg.height))
            image_number = image_number.resize((image_number.width * 3, image_number.height * 3), Image.ANTIALIAS)
            number.paste(image_number, (i * 20, 0))
        # number.show()
        number.save(path+".png")
        number.close()
        self.image_bg.close()
 
    def get_image_base4(self, index, t, path):
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
        self.get_number_for_img(path)

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
        global KWDIR_FOCUS_TREND_DIR
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
                path = os.path.join(KWDIR_FOCUS_TREND_DIR, datestr)
                self.number_img.get_image_base4(i, "index", path)
                fr += one_step
 
    def get_soMediaJson(self):
        """
        曝光量:list
        """
        global KWDIR_EXPOSURE_DIR
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
                path = os.path.join(KWDIR_EXPOSURE_DIR, datestr)
                self.number_img.get_image_base4(i, "media", path)
                fr += one_step

parser = argparse.ArgumentParser(description='360Trends')
parser.add_argument("--kw", type=str, default="360")
parser.add_argument("--fr", type=str, default="2022-01-01")
parser.add_argument("--area", type=str, default="全国")
args = parser.parse_args()

CURPATH = os.path.abspath(os.path.dirname(__file__))
KWDIR = os.path.join(CURPATH, args.kw)
KWDIR_FOCUS_TREND_DIR = os.path.join(KWDIR, "FocusTrends")
KWDIR_EXPOSURE_DIR = os.path.join(KWDIR, "Exposure")
if not os.path.exists(KWDIR):
    os.makedirs(KWDIR)
if not os.path.exists(KWDIR_FOCUS_TREND_DIR):
    os.makedirs(KWDIR_FOCUS_TREND_DIR)
if not os.path.exists(KWDIR_EXPOSURE_DIR):
    os.makedirs(KWDIR_EXPOSURE_DIR)

if args.kw.count(","):
    print("only one keyword is allowed")

A = Trends360([args.kw], args.area, args.fr)
print(args.kw, " => ", "FocusTrends")
A.get_soIndexJson()
print(args.kw, " => ", "ExposureValue")
A.get_soMediaJson()
print("[", args.kw, ", finished]")
