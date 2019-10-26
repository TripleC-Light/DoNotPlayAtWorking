# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import webbrowser
from PIL import Image
import os
import time
import random
import threading
import tornado.websocket
from Object import Object
import json
import myFunction as myFunc
from ObjCtrl import ObjCtrl
from Script import Script

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):     # 允許跨來源資源共用
        return True

    def allow_draft76(self):            # for iOS 5.0 Safari
        return True

    def open(self):
        print("new client opened")

    def on_close(self):
        print("Client leave")

    def on_message(self, CMDfromWEB):
        global gFrameTime
        global gObjList
        global gPilotListInJSON
        global gMapSize
        global gMsgCtrl
        global gObjCtrl

        _getInitPositionFail = [-1, -1]
        _tmp = CMDfromWEB.split('@')
        _cmd = _tmp[0]
        _returnInfo = ''
        if _cmd == 'createPilot':
            _pilot = gObjCtrl.createCharacter('pilot')
            if _pilot != False:
                gObjList[_pilot.id] = _pilot
                gMsgCtrl.add('系統公告', '玩家 ' + _pilot.name + '進入遊戲')
                _pilotInJSON = _pilot.__dict__
                _returnInfo = 'newPilot@' + json.dumps(_pilotInJSON)

        elif _cmd == 'reBorn':
            _id = _tmp[1]
            gObjList[_id].HP = 10

        elif _cmd == 'getNewData':
            _data = _tmp[1]
            _id = _data
            if _id in gObjList:
                gObjList[_id].timeOut = round(time.time(), 3)
            gPilotListInJSON['serverTime'] = time.time()
            _returnInfo = 'NewData@' + json.dumps(gPilotListInJSON)

        elif _cmd == 'move':
            _data = _tmp[1]
            _tmp = _data.split(';')
            _id = _tmp[0]
            _XY = _tmp[1]
            _XY = _XY.split(',')
            gObjList[_id].tX = int(_XY[0])
            gObjList[_id].tY = int(_XY[1])

        elif _cmd == 'attack':
            _id = _tmp[1]
            gObjList[_id].attack = time.time()

        elif _cmd == 'createEnemy':
            for _i in range(5):
                _enemy = gObjCtrl.createCharacter('zombie')
                gObjList[_enemy.id] = _enemy

        elif _cmd == 'createItem':
            gObjCtrl.mapSize = gMapSize
            for _i in range(3):
                _item = gObjCtrl.createItem('fullHP')
                gObjList[_item.id] = _item

        elif _cmd == 'sendMsg':
            _data = _tmp[1]
            _tmp = _data.split(';')
            _id = _tmp[0]
            _msg = _tmp[1]
            _msg = gMsgCtrl.filter(_msg)
            gObjList[_id].msgTimeCount = 5
            gObjList[_id].msg = _msg
            gMsgCtrl.add(gObjList[_id].name, _msg)

        elif _cmd == 'getMsg':
            _returnInfo = gMsgCtrl.returnToWeb()

        elif _cmd == 'setMap':
            _reserveList = {}
            for _mapObj in gObjList:
                if gObjList[_mapObj].type != 'mapObj':
                    _reserveList[_mapObj] = gObjList[_mapObj]
            gObjList = _reserveList.copy()

            _data = _tmp[1]
            _mapRegion = _data
            _mapObjInJSON = {}
            _mapObjList = []
            filename = './static/map/setting/' + _mapRegion + '.map'
            with open(filename, 'r', encoding='utf-8') as fRead:
                for line in fRead:
                    line = line.strip()
                    line = line.split(':')
                    _type = line[0]

                    if _type == 'region':
                        _mapObjInJSON['region'] = line[1]
                    elif _type == 'size':
                        _description = line[1].split(',')
                        gMapSize = [int(_description[0]), int(_description[1])]
                        _mapObjInJSON['size'] = gMapSize
                    elif _type == 'background':
                        _mapObjInJSON['background'] = './static/map/background/' + line[1]
                    elif _type == 'mapObj':
                        _obj = Object()
                        _description = line[1].split(',')
                        _pic = _description[0]
                        _X = int(_description[1])
                        _Y = int(_description[2])
                        _obj.type = 'mapObj'
                        _obj.id = myFunc.getUniqueID(list(gObjList.keys()))
                        _obj.name = str(_obj.id)
                        _obj.X = _X
                        _obj.Y = _Y
                        _obj.tX = _X
                        _obj.tY = _Y
                        if _pic == 'bud':
                            _obj.HP = 1000
                            _obj.W = 70
                            _obj.H = 70
                            _obj.pic = './static/map/obj/' + _pic + '.png'
                        gObjList[_obj.id] = _obj
                        _mapObjList.append(_obj.__dict__)

            _mapObjInJSON['ObjList'] = _mapObjList
            _objToJSON = json.dumps(_mapObjInJSON)
            _returnInfo = 'setMap@' + _objToJSON

        self.write_message(_returnInfo)

def loopAll():
    global gMapSize
    global gFrameTime
    global gPilotListInJSON
    global gMsgCtrl
    global gObjList
    global gObjCtrl
    global gScript

    _timeCtrl = myFunc.TimeCtrl()
    gObjCtrl.attackTime = 0.1   # second
    gObjCtrl.offlineTime = 5    # second
    gObjCtrl.frameTime = gFrameTime

    while 1:
        _timeCtrl.sysTime = time.time()
        _FPS = _timeCtrl.showFPS()
        gObjCtrl.mapSize = gMapSize
        gObjCtrl.sysTime = _timeCtrl.sysTime
        gObjCtrl.objList = gObjList
        gObjCtrl.clearBeHIT()
        gScript.msgCtrl = gMsgCtrl
        _pilotList = []
        for _id in list(gObjList.keys()):
            _deleteState = False
            _pilot = gObjList[_id]
            if _pilot.type != 'mapObj':
                gObjCtrl.updatePosition(_pilot)
                gObjCtrl.clearAttack(_pilot)

                if _pilot.attack != 0:
                    _weapen = gObjCtrl.createWeapen(_pilot)
                    gObjCtrl.attackJudge(_pilot)

                if gObjCtrl.timeOut(_pilot):
                    if _pilot.type != 'item':
                        gMsgCtrl.add('系統公告', str(_pilot.name) + ' 離開遊戲')
                    _deleteState = True
                    print('delete: ' + str(_id))

                if gObjCtrl.HPtoZero(_pilot):
                    if _pilot.type == 'enemy':
                        print('Game Over: ' + str(_pilot.id))
                        _deleteState = True
                    elif _pilot.type == 'item' and _pilot.pic == 'button':
                        print('Button be push')
                        _deleteState = True
                    else:
                        gMsgCtrl.add('系統公告', str(_pilot.name) + ' HP歸零')

                if _deleteState:
                    del gObjList[_id]

        if _timeCtrl.oneSecondTimeOut():
            for _id in list(gObjList.keys()):
                _pilot = gObjList[_id]
                gObjCtrl.msgTimeOutCheck(_pilot)
                gObjCtrl.enemyAutoCtrl(_pilot)
                gObjCtrl.enemyTimeReflash(_pilot)
                gObjCtrl.itemTimeReflash(_pilot)

            gScript.region = '0-0'
            gScript.mapSize = gMapSize
            gScript.objCtrl = gObjCtrl
            gScript.run(gObjList)
            if gScript.Start:
                if random.randint(0, 10) == 0:
                    for _i in range(random.randint(1, 3)):
                        _item = gObjCtrl.createItem('fullHP')
                        gObjList[_item.id] = _item

        for _id in list(gObjList.keys()):
            _pilot = gObjList[_id]
            if _pilot.type != 'mapObj':
                _pilotList.append(_pilot.__dict__)

        gPilotListInJSON['list'] = _pilotList
        gPilotListInJSON['FPS'] = _FPS
        time.sleep(gFrameTime)

if __name__ == "__main__":
    global gObjList
    global gPilotListInJSON
    global gFrameTime           # Frame per second
    global gMsgCtrl
    global gMapSize
    global gObjCtrl
    global gScript

    try:
        gObjList = {}
        gFrameTime = 0.05
        gPilotListInJSON = {}
        gMsgCtrl = myFunc.MsgCtrl()
        gMapSize = []
        gObjCtrl = ObjCtrl()
        gScript = Script()

        # 建立執行緒並執行
        t = threading.Thread(target=loopAll)
        t.start()

        handlers = [[r'/index', IndexHandler],
                    [r'/ws', WebSocketHandler],
                    [r'/favicon.ico', tornado.web.StaticFileHandler, {'path': './static/favicon.ico'}]]

        webApp = tornado.web.Application(
            handlers,
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True
        )
        webApp.listen(8888)
        url = 'http://localhost:8888/index'
        # webbrowser.open(url=url, new=0)
        print('Server open in: ' + url)
        tornado.ioloop.IOLoop.instance().start()

    except KeyboardInterrupt:
        print('再見！')
