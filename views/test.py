from django.http import HttpResponse

def test(request,user,pwd):
    html=' test'
    YiBan(user,pwd)
    return HttpResponse(html)

from threading import Thread
import time

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import hashlib
import json
import requests
import base64
import uuid
###############################################

def rsa_encrypt(pwd):
    """
    rsa_key: 密钥
    登录密码加密
    """
    PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
    MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA6aTDM8BhCS8O0wlx2KzA
    Ajffez4G4A/QSnn1ZDuvLRbKBHm0vVBtBhD03QUnnHXvqigsOOwr4onUeNljegIC
    XC9h5exLFidQVB58MBjItMA81YVlZKBY9zth1neHeRTWlFTCx+WasvbS0HuYpF8+
    KPl7LJPjtI4XAAOLBntQGnPwCX2Ff/LgwqkZbOrHHkN444iLmViCXxNUDUMUR9bP
    A9/I5kwfyZ/mM5m8+IPhSXZ0f2uw1WLov1P4aeKkaaKCf5eL3n7/2vgq7kw2qSmR
    AGBZzW45PsjOEvygXFOy2n7AXL9nHogDiMdbe4aY2VT70sl0ccc4uvVOvVBMinOp
    d2rEpX0/8YE0dRXxukrM7i+r6lWy1lSKbP+0tQxQHNa/Cjg5W3uU+W9YmNUFc1w/
    7QT4SZrnRBEo++Xf9D3YNaOCFZXhy63IpY4eTQCJFQcXdnRbTXEdC3CtWNd7SV/h
    mfJYekb3GEV+10xLOvpe/+tCTeCDpFDJP6UuzLXBBADL2oV3D56hYlOlscjBokNU
    AYYlWgfwA91NjDsWW9mwapm/eLs4FNyH0JcMFTWH9dnl8B7PCUra/Lg/IVv6HkFE
    uCL7hVXGMbw2BZuCIC2VG1ZQ6QD64X8g5zL+HDsusQDbEJV2ZtojalTIjpxMksbR
    ZRsH+P3+NNOZOEwUdjJUAx8CAwEAAQ==
    -----END PUBLIC KEY-----
    '''
    cipher = PKCS1_v1_5.new(RSA.importKey(PUBLIC_KEY))
    cipher_text = base64.b64encode(cipher.encrypt(bytes(pwd, encoding="utf8")))
    return cipher_text.decode("utf-8")
######################################################################################

class YiBan:
    #固定参数
    session = requests.session()
    access_token = ''
    headers = {
        "Origin": "https://c.uyiban.com",
        "AppVersion": "5.0",
        'User-Agent':'Mozilla/5.0 (Linux; Android 11; Pixel 5 Build/RD2A.211001.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.120 Mobile Safari/537.36 yiban_android/5.0.8'
    }
    CSRF = '0000'
    cookies = {"csrf_token": CSRF}




    def login(self,user, pwd):
        login_url = 'https://m.yiban.cn/api/v4/passport/login'
        headers = {
            "Origin": "https://c.uyiban.com",
            "User-Agent": "Yiban",
            "AppVersion": "5.0"
        }
        # 密码rsa加密
        rsa_pwd = rsa_encrypt(pwd)
        uu = str(uuid.uuid4())
        hl = hashlib.md5()
        hl.update(uu.encode(encoding='utf-8'))
        sig = hl.hexdigest()[0: 16]
        login_data = {
            'device': 'samsung:SM-G9750',
            'v': '5.0.8',
            'password': rsa_pwd,
            'token': '',
            'mobile': user,
            'ct': 2,
            'identify': '010045026872666',
            'sversion': '22',
            'apn': 'wifi',
            'app': '1',
            'authCode': '',
            'sig': sig
        }

        req = self.session.post(login_url,data=login_data,headers=headers,cookies=self.cookies,allow_redirects=True,params={}).json()
        if req['response'] == 100:
            print('登录成功 欢迎',req['data']['user']['name'])
            return req['data']['access_token']
        else:
            raise Exception('账号或密码错误')

    def Send(self):
        for index in range(1,21):
            content = requests.get('http://v1.hitokoto.cn').json()
            data={
                'channel':[{"boardId":"Oa1cGeM6lE65Okd","orgId":2006794}],
                'hasVLink':0,
                'isPublic':1,
                'summary':"",
                'thumbType':1,
                'title':content['hitokoto'],
                'content':f'author:{content["from"]}',
                'kind':'1',
                'id':'1'
            }
            if index==1:
                yimiaomiao = requests.get('https://mm.yiban.cn/article/index/add',
                                          headers={'loginToken': access_token},
                                          allow_redirects=True,
                                          json=data)
                print(yimiaomiao.json()['message'],'易喵喵 第',index,'次 发帖:',time.strftime('%Y-%m-%d %H:%M:%S'))
            weishequ = requests.get('https://s.yiban.cn/api/post/advanced',
                                    headers={'loginToken': access_token},
                                    allow_redirects=True,
                                    json=data)

            #print(weishequ.json())#社区帖子
            print(weishequ.json()['message'],'微社区 第',index,'次 发帖:',time.strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(61)


    def qiandao(self):
        option = ''
        chk = requests.get('https://m.yiban.cn/api/v4/home?modules=checkin',
                           headers={'loginToken': access_token},
                           allow_redirects=True)
        req = requests.get('https://m.yiban.cn/api/v4/checkin/question',
                           headers={'loginToken': access_token},
                           allow_redirects=True)
        reqs = req.json()
        if reqs['response'] == 100:
            option = reqs['data']['survey']['question']['option'][0]['id']
        data={'optionId':option}
        ans = requests.post('https://m.yiban.cn/api/v4/checkin/answer',
                            headers={'loginToken': access_token},
                            allow_redirects=True,
                            json=data)
        if json.dumps(ans.json()['data']['status'])=="1":
            print("签到成功 +2")
        else:
            print("重复签到！")





    def up(self):
        req = requests.get('https://s.yiban.cn/api/forum/getListByBoard?offset=0&count=50&boardId=Oa1cGeM6lE65Okd&orgId=2006794',
                           headers={'loginToken': access_token,
                                    'client':'android',
                                    'yiban_user_token':access_token
                                    },
                           allow_redirects=True)
        count = 1
        req_csrf=requests.post('https://s.yiban.cn/api/security/getToken',headers={'loginToken': access_token,
                                                                                   'client':'android',
                                                                                   'yiban_user_token':access_token})
        PHPSESSID = req_csrf.cookies["PHPSESSID"]
        csrf=req_csrf.json()['data']['csrfToken']
        for index in range(len(req.json()['data']['list'])-1):
            if count>30:
                break
            isup=req.json()['data']['list'][index]['isUp']
            postid=req.json()['data']['list'][index]['id']
            userid=req.json()['data']['list'][index]['user']['id']
            if json.dumps(isup)=='false':
                chk=requests.get('https://s.yiban.cn/api/post/thumb',
                                 headers={'loginToken': access_token,
                                          'client':'android',
                                          'yiban_user_token':access_token},
                                 json={'action':'up',
                                       'postId':postid,
                                       'userId':userid},
                                 allow_redirects=True)
                print(chk.json()['message'],'第',count,'次 点赞 ',time.strftime('%Y-%m-%d %H:%M:%S'))
                count+=1
                time.sleep(3)

    def pinglun(self):
        yimm_url='https://mm.yiban.cn/news/index/index3?offset=0&size=31'
        wsq_url='https://s.yiban.cn/api/forum/getListByBoard?offset=0&count=31&boardId=Oa1cGeM6lE65Okd&orgId=2006794'
        sqlist = requests.get(wsq_url,
                              headers={'loginToken': access_token,
                                       'client':'android',
                                       'yiban_user_token':access_token
                                       },
                              allow_redirects=True)
        mmlist = requests.get(yimm_url,
                              headers={'loginToken': access_token,
                                       'client':'android',
                                       'yiban_user_token':access_token
                                       },
                              allow_redirects=True)
        req_csrf=requests.post('https://s.yiban.cn/api/security/getToken',headers={'loginToken': access_token,
                                                                                   'client':'android',
                                                                                   'yiban_user_token':access_token})
        PHPSESSID = req_csrf.cookies["PHPSESSID"]
        csrf=req_csrf.json()['data']['csrfToken']
        for index in range(1,31):
            content = requests.get('http://v1.hitokoto.cn').json()
            postid=sqlist.json()['data']['list'][index]['id']
            userid=sqlist.json()['data']['list'][index]['user']['id']
            if index<=5:
                mmid=mmlist.json()['data']['list'][index]['id']
                com_mm = requests.post('https://mm.yiban.cn/news/comment/add?recommend_type=3',cookies={'PHPSESSID':PHPSESSID},
                                       headers={'loginToken': access_token,
                                                'yiban_user_token':access_token},
                                       json={'id':mmid,
                                             'comment':content['hitokoto']
                                             },
                                       allow_redirects=True)
                print(com_mm.json()['message'],'易喵喵 第',index,'次 评论 ',time.strftime('%Y-%m-%d %H:%M:%S'))
            com_sq = requests.post('https://s.yiban.cn/api/post/comment',cookies={'PHPSESSID':PHPSESSID},
                                   headers={'loginToken': access_token,
                                            'yiban_user_token':access_token},
                                   json={'postId':postid,
                                         'comment':content['hitokoto'],
                                         'userId':userid,
                                         'csrfToken':csrf
                                         },
                                   allow_redirects=True)
            print(com_sq.json()['message'],'微社区 第',index,'次 评论 ',time.strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(61)



    def __init__(self, user, pwd):
        global access_token
        access_token=self.login(user,pwd)
        dz=Thread(target=self.up)
        dz.start()
        send=Thread(target=self.Send)
        send.start()
        qd=Thread(target=self.qiandao)
        qd.start()
        pl=Thread(target=self.pinglun)
        pl.start()


# if __name__ == '__main__':
#     a = input("请输入您的账号:")
#     b = input("请输入您的密码:")
#     YiBan(a,b)
