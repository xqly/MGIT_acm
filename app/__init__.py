import os
import requests
import json
from flask import Flask,render_template,request
from app.db import *
from flask_apscheduler import APScheduler
from datetime import timedelta

def update_data():
    print(123)
    db =outline_get_db()
    user = db.execute(
        'select * from user'
    ).fetchall()
    allname =""
    for i in user:
        allname+=i['cf_nickname']+";"
    url = "https://codeforces.com/api/user.info?handles="+allname
    # print(url)
    r = requests.get(url)
    r = r.json()
    # print(r)
    data=[]
    if(r['status'] == "OK"):
        r = r['result']
        for i in r :
            if 'rating' in i:
                db.execute(
                    'update user set cf_rating = ? where cf_nickname = ?',(i['rating'],i['handle'])
                )
    db.commit()
    data = []
    answ = db.execute(
        'select * from user order by cf_rating desc'
    ).fetchall()
    for i in answ:
        elem = {"name": i['cf_nickname'],
                "value": i['cf_rating'],
                "date": 2020}
        data.append(elem)
    file = open("app/static/data1.js", "w", encoding="utf-8")
    file.write("var TotalData=" + json.dumps(data))
    file.close()

def method_test(a,b):
    print(a+b)


class Config(object):  # 创建配置，用类
    # 任务列表
    JOBS = [
        # {  # 第一个任务
        #     'id': 'job1',
        #     'func': '__main__:job_1',
        #     'args': (1, 2),
        #     'trigger': 'cron', # cron表示定时任务
        #     'hour': 19,
        #     'minute': 27
        # },
        {  # 第二个任务，每隔5S执行一次
            'id': 'job2',
            'func': 'app.__init__:update_data', # 方法名
            'args': (), # 入参
            'trigger': 'interval', # interval表示循环任务
            'seconds': 30,
        }
    ]



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
    # a simple page that says hello
    @app.route('/animation')
    def animation():
        return render_template('animation.html')


    @app.route('/')
    def good():
        db = get_db()
        all = db.execute(
            'select * from user order by cf_rating desc'
        ).fetchall()
        data = []
        for i in all :
            temp = []
            temp.append(i['cf_nickname'])
            temp.append(i['cf_rating'])
            data.append(temp)
        return render_template('rating.html' ,data=data)

    @app.route('/addcf',methods=['GET','POST'])
    def addcf():
        db=get_db()
        if request.method=='POST':
            db.execute(
                'insert into user(cf_nickname)values (?);',([request.form['name']])
            )
            db.commit()
            print(request.form['name'])
        return render_template('addcf.html')
    from . import db
    db.init_app(app)
    app.config.from_object(Config())
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    return app