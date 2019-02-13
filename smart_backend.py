# -*- coding: utf-8 -*-
from flask import Flask
from pic import resizeImg
import os
import json
from flask import request
import redis
import mysql.connector
from flask import make_response
import time
import random
from threading import Timer
import zipfile
app = Flask(__name__)
r = redis.Redis(host='127.0.0.1',port=6379)
dir_workprocess={}
last_work={}
FILEDIR="/home/file/"
WORKPROCESS="dirworkprocess:"
GROUP_KEY="group_all"
GROUP_PEOPLE_KEY_PREFIX="group_name_"
GROUP_PERMISSION_KEY_PREFIX="group_permission_"
DIR_KEY="dir_all"
DIR_KEY_PREFIX="dir_name_"
IMAGE_LOCK=False


@app.route('/get_info',methods=['GET', 'POST'])
def get_info():
    groups=r.smembers(GROUP_KEY)
    dirs=r.smembers(DIR_KEY)
    retMap={}
    retMap["groups"]=list(groups)
    retMap["dirs"]=list(dirs)
    response = make_response(json.dumps(retMap))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response
@app.route('/add_people',methods=['GET', 'POST'])
def add_people():
    group_name = request.form.get('group')
    people_name = request.form.get('people')
    if group_name=="" or group_name==None or people_name=="" or people_name==None:
        pass
    else:
        r.sadd(GROUP_PEOPLE_KEY_PREFIX+group_name,people_name)
    ret=r.smembers(GROUP_PEOPLE_KEY_PREFIX+group_name)
    response = make_response(json.dumps(list(ret)))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response
@app.route('/get_people',methods=['GET', 'POST'])
def get_people():
    group_name = request.form.get('group')
    peoples=[]
    if group_name=="" or group_name==None :
        pass
    else:
        peoples=r.smembers(GROUP_PEOPLE_KEY_PREFIX+group_name)
    response = make_response(json.dumps(list(peoples)))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response
@app.route('/out_answer',methods=['GET', 'POST'])
def out_answer():
    group_name = request.form.get('group')
    people_name = request.form.get('people')
    dir_name=request.form.get('dir')
    ans_all=[]
    if (group_name=="" or group_name==None) and (people_name!="" and people_name!=None)  :
        ans_all=execsql("select id,ans from answer where wid='"+people_name +"' and dir='"+dir_name+"'")
    elif (group_name!="" and group_name!=None)and (people_name=="" or people_name==None):
        ans_all=execsql("select id,ans from answer where grou='"+group_name +"' and dir='"+dir_name+"'")
    print (ans_all)
    zip_name='out'+str(int(time.time()))+'.zip'
    azip = zipfile.ZipFile('/home/file/zip_out_answer/'+zip_name, 'w')
    for ansA in ans_all:
        id,ans=ansA
        print(id)
        print(ans)
        if len(ans)>10:
            azip.writestr(str(id)+'.txt', ans[9:len(ans)-2], zipfile.ZIP_DEFLATED)
    azip.close()
    response = make_response(zip_name)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response
@app.route('/add_group',methods=['GET', 'POST'])
def add_group():
    group_name = request.form.get('name')
    if group_name=="" or group_name==None:
        pass
    else:
        r.sadd(GROUP_KEY,group_name)
    groups=r.smembers(GROUP_KEY)
    response = make_response(json.dumps(list(groups)))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response
@app.route('/add_permission',methods=['GET', 'POST'])
def add_permission():
    group_name = request.form.get('group')
    dir_name = request.form.get('dir')
    if group_name=="" or group_name==None or dir_name=="" or dir_name==None:
        pass
    else:
        r.sadd(GROUP_PERMISSION_KEY_PREFIX+group_name,dir_name)
    # groups=r.smembers(GROUP_KEY)
    response = make_response("ok")
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response
@app.route('/init_dir',methods=['GET', 'POST'])
def init_dir():
    print("init_dir")
    dir_in='/home/orifile/'
    dir_out='/home/file/'
    dirsIn=os.listdir(dir_in)
    dirsOut=os.listdir(dir_out)
    for dirIn in dirsIn:
        have=0
        for dirOut in dirsOut:
            if dirIn==dirOut:
                have=1
                break
        if have==0:
            dirs=os.listdir(dir_in+dirIn+"/")
            index=0
            os.mkdir(dir_out+dirIn)
            for dir in dirs:
                print (dir)
                index=index+1
                if dir.endswith('.jpg')==False:
                    continue
                ori_img = dir_in+dirIn+"/"+dir
                dst_img = dir_out+dirIn+"/"+ dir
                dst_w = 800.0
                dst_h = 800.0
                save_q = 80
                w,h=resizeImg(ori_img=ori_img, dst_img=dst_img, dst_w=dst_w, dst_h=dst_h, save_q=save_q)
                print(w/dst_w,h/dst_h)
                print (json.dumps({"widthZoom":w/dst_w,"heightZoom":h/dst_h}))
                r.set("work_"+   dirIn+'_'+str(index),json.dumps({"widthZoom":w/dst_w,"heightZoom":h/dst_h,"name":dir}))
            r.sadd(DIR_KEY,dirIn)
            # r.set('dirinit_'+dirIn,'1')
            all=0
            succ=0
            for dir in dirs:
                print("test!!!!")
                outDirs=os.listdir(dir_out+dirIn+"/")
                have=0
                for dirOut in outDirs:
                    if dir==dirOut:
                        have=1
                        break
                all+=1
                succ+=have
            res=r.smembers(DIR_KEY)
            print (res)
            print("all,succ")
            print(all)
            print(succ)
            r.set('dirworkprocess:'+dirIn,"1")
            r.set("dirallnum:"+dirIn,succ)
    response = make_response("ok")
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response
@app.route('/get_image',methods=['GET', 'POST'])
def get_image():
    print("get_image")
    dir_name = request.form.get('dir')
    group = request.form.get('group')
    wid = request.form.get('wid')
    print(dir_name)
    print(group)
    print(wid)
    if last_work.has_key(wid) and last_work[wid]!={}:
        work_temp=last_work[wid]
        allnum=r.incr("dirallnum:"+work_temp["dir"])
        r.set("work_"+work_temp["dir"]+'_'+str(allnum),r.get("work_"+work_temp["dir"]+"_"+str(work_temp["index"])))

    r.set("dirworkprocess:"+dir_name,"1")
    dir_workprocess[dir_name]=1
    if dir_workprocess.has_key(dir_name)==False:
        dir_workprocess[dir_name]=int(r.get(WORKPROCESS+dir_name))
    print("process:"+str(dir_workprocess[dir_name]))
    workJson=r.get("work_"+dir_name+"_"+str(dir_workprocess[dir_name]))
    print("json:"+workJson)
    if workJson==None:
        response = make_response("")
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    else:
        store_message={"time":time.time(),"dir":dir_name,"index":dir_workprocess[dir_name]}
        last_work[wid]=store_message
        r.set("working_"+wid,json.dumps(store_message))
        dir_workprocess[dir_name]+=1
        r.set(WORKPROCESS+dir_name,dir_workprocess[dir_name])
        print("work:"+workJson)
        work=json.loads(workJson)
        response = make_response(json.dumps(work))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

@app.route('/push_answer',methods=['GET', 'POST'])
def push_answer():
    print("push_answer")
    answer=request.form.get('answer')
    wid=request.form.get('wid')
    group=request.form.get('group')
    dir=request.form.get('dir')
    # answer="a"
    # wid="b"
    # group="c"
    # dir="f"
    last_work[wid]={}
    r.delete("wroking_"+wid)
    ans_mysql=json.dumps({"ans":answer})
    # con=mysql.connector.connect(host='localhost',port=3306,user='root',
    #                         password='root',database='test',charset='utf8')
    conn = mysql.connector.connect(host='114.116.23.135',port=3306,user='kael', password='123456', database='answer', charset='utf8')
    cursor = conn.cursor()
    sql="INSERT INTO answer (ans, wid, grou, dir, create_time) VALUES (\'"+ "test_answer"+"\', \'"+str(wid)+"\',\'"+group+"\',\'"+dir+"\', 1234)"
    print(sql)
    cursor.execute("INSERT INTO answer (ans, wid, grou, dir, create_time) VALUES (\'"+ ans_mysql+"\', \'"+str(wid)+"\',\'"+group+"\',\'"+dir+"\', 1234)")
    conn.commit()
    cursor.close()
    conn.close()
    response = make_response(json.dumps("ok"))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

def timedTask():
    Timer(10, task, ()).start()
def task():
    print("task")
    workings=r.keys("working_*")
    for working in workings:
        work_temp=json.loads(r.get(working))
        if int(work_temp["time"])+2*60*60<time.time():
            print(working)
            allnum=r.incr("dirallnum:"+work_temp["dir"])
            r.set("work_"+work_temp["dir"]+'_'+str(allnum),r.get("work_"+work_temp["dir"]+"_"+work_temp["index"]))
def execsql(sql):
    conn = mysql.connector.connect(host='114.116.23.135',port=3306,user='kael', password='123456', database='answer', charset='utf8')
    cursor = conn.cursor()
    print(sql)
    cursor.execute(sql)
    ret=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return ret
if __name__ == '__main__':
    import mysql.connector
    # host     : '114.116.23.135:3306',
    # user     : 'pig',
    # password : '123456'
    # cursor.execute('create table user (id varchar(20) primary key, name varchar(20))')
    # cursor.execute('insert into user (id, name) values (%s, %s)', ['1', 'Michael'])
    # cursor.execute('show databases')
    # results = cursor.fetchall()
    # for d in results:
    #     print (d)
    r.set('name','root')
    print(r.get('name').decode('utf8'))
    # init_dir()
    timedTask()
    # push_answer()
    app.run(host='0.0.0.0', port=5000, debug=True)

