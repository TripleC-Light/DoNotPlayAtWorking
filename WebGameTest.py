# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.httpclient
import os
import webbrowser
import serial
import requests
import time
import serial.tools.list_ports
import random
import threading
import math
import tornado.websocket
from Object import Object
import json

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    global gCharacterList

    def check_origin(self, origin):  # 允许WebSocket的跨域请求
        return True

    def allow_draft76(self):        # for iOS 5.0 Safari
        return True

    def open(self):
        print("new client opened")

    def on_close(self):
        print("Client leave")

    def on_message(self, CMDfromWEB):
        global gCharacterList
        global gMyID
        global gPilotListInJSON

        _tmp = CMDfromWEB.split('@')
        _cmd = _tmp[0]
        _returnInfo = ''
        if _cmd == 'createPilot':
            _data = _tmp[1]
            _originalPoint = _data
            _originalPoint = _originalPoint.split(',')
            robot = Object()
            robot.id = gMyID
            robot.name = str(robot.id)
            _XY = setInitPosition(_originalPoint, robot)
            robot.X = _XY[0]
            robot.Y = _XY[1]
            robot.targetX = _XY[0]
            robot.targetY = _XY[1]
            robot.connectTimeOut = time.time()
            # robot.pic = './static/pilot/robot/right.gif'
            gCharacterList.append(robot)
            addNewMsgToBox('系統公告', '新玩家 ' + robot.name + '進入遊戲')
            _returnInfo = returnMsg()

        elif _cmd == 'getNewData':
            _data = _tmp[1]
            _id = _data
            for _pilot in gCharacterList:
                if str(_pilot.id) == _id:
                    _pilot.connectTimeOut = time.time()
                    break
            gPilotListInJSON.update({'serverTime': time.time()})
            _returnInfo = 'NewData@' + json.dumps(gPilotListInJSON)

        elif _cmd == 'getID':
            _tmp = math.modf(time.time())
            _tmp = _tmp[0] * 10000000
            _tmp = math.modf(_tmp)
            _tmp = int(_tmp[1])
            gMyID = id(self) + _tmp
            print('New ID= ' + str(gMyID))
            _returnInfo = 'ID@' + str(gMyID)

        elif _cmd == 'move':
            _data = _tmp[1]
            _tmp = _data.split(';')
            _id = _tmp[0]
            _XY = _tmp[1]
            _XY = _XY.split(',')
            for _pilot in gCharacterList:
                if str(_pilot.id) == _id:
                    _pilot.targetX = int(_XY[0])
                    _pilot.targetY = int(_XY[1])
                    break

        elif _cmd == 'attack':
            _id = _tmp[1]
            for _pilot in gCharacterList:
                if str(_pilot.id) == _id:
                    _pilot.attack = time.time()
                    break

        elif _cmd == 'sendMsg':
            _data = _tmp[1]
            _tmp = _data.split(';')
            _id = _tmp[0]
            _msg = _tmp[1]
            _msg = legalMsg(_msg)
            for _pilot in gCharacterList:
                if str(_pilot.id) == _id:
                    _pilot.msgTimeCount = 5
                    _pilot.msg = _msg
                    addNewMsgToBox(_pilot.name, _msg)
                    break

        elif _cmd == 'getMsg':
            _returnInfo = returnMsg()

        elif _cmd == 'setMap':
            _reserveList = []
            for _mapObj in gCharacterList:
                if _mapObj.type != 'mapObj':
                    _reserveList.append(_mapObj)
            gCharacterList = _reserveList.copy()

            _data = _tmp[1]
            _mapRegion = _data
            _mapObjInJSON = {}
            _mapObjList = []
            _mapObjID = 0
            filename = './static/map/setting/' + _mapRegion + '.map'
            with open(filename, 'r', encoding='utf-8') as fRead:
                for line in fRead:
                    line = line.strip()
                    line = line.split(':')
                    _type = line[0]

                    if _type == 'region':
                        _mapObjInJSON.update({'region': line[1]})
                    elif _type == 'size':
                        _description = line[1].split(',')
                        _mapSize = [int(_description[0]), int(_description[1])]
                        _mapObjInJSON.update({'size': _mapSize})
                    elif _type == 'background':
                        _mapObjInJSON.update({'background': './static/map/background/' + line[1]})
                    elif _type == 'mapObj':
                        _obj = Object()
                        _description = line[1].split(',')
                        _pic = _description[0]
                        _X = int(_description[1])
                        _Y = int(_description[2])
                        _obj.type = 'mapObj'
                        _obj.id = _mapObjID
                        _obj.name = str(_obj.id)
                        _obj.X = _X
                        _obj.Y = _Y
                        _obj.targetX = _X
                        _obj.targetY = _Y
                        if _pic == 'bud':
                            _obj.HP = 1000
                            _obj.width = 70
                            _obj.height = 70
                            _obj.pic = './static/map/obj/' + _pic + '.png'
                        gCharacterList.append(_obj)
                        _mapObjList.append(_obj.__dict__)
                        _mapObjID += 1
            _mapObjInJSON.update({'ObjList': _mapObjList})
            _objToJSON = json.dumps(_mapObjInJSON)
            _returnInfo = 'setMap@' + _objToJSON

        self.write_message(_returnInfo)

def setInitPosition(originalPoint, robot):
    _collisionState = (True, 0)
    _tryCount = 0
    _XY = []
    while _collisionState[0]:
        _XY = [0, 0]
        _XY[0] = random.randint(1+(robot.width/2), 600-(robot.width/2)) - robot.width/2 + round(float(originalPoint[0]))
        _XY[1] = random.randint(1+(robot.height/2), 600-(robot.height/2)) - robot.height/2 + round(float(originalPoint[1]))
        robot.X = _XY[0]
        robot.Y = _XY[1]
        robot.targetX = _XY[0]
        robot.targetY = _XY[1]
        _collisionState = rectCollision(robot, gCharacterList)
        _tryCount += 1
        if _tryCount > 1000:
            _XY = [-100, -100]
            print('Already try 1000 times to find a good position but the map has no position to put Pilot')
            break
    print('Try select a new position in ' + str(_tryCount) + ' times')
    return _XY

def addNewMsgToBox(_name, _msg):
    global gMsgBox
    if len(gMsgBox) >= 6:
        _tmp = gMsgBox[1:]
        gMsgBox = _tmp
    gMsgBox.append([_name, _msg])

def returnMsg():
    global gMsgBox
    _returnInfoInJSON = {'list': gMsgBox}
    _returnInfo = 'SysMsg@' + json.dumps(_returnInfoInJSON)
    return _returnInfo

def legalMsg(_msg):
    print(_msg)
    _msg = _msg.replace('\t', "")
    _msg = _msg.replace('\T', "")
    _msg = _msg.replace('\\', "")
    _msg = _msg.replace('@', '')
    _msg = _msg.replace(';', '')
    _msg = _msg.replace('"', '\'')
    _msg = _msg.replace('>', "")
    _msg = _msg.replace('<', "")
    return _msg

def updateAll():
    global gTimeCounter
    global gFrameTime
    global gPilotListInJSON

    _msgUpdateTime = 1  # second
    _attackTime = 0.1   # second
    _offlineTime = 5    # second
    while True:
        gTimeCounter += 1
        if (gTimeCounter * gFrameTime) > _msgUpdateTime:
            gTimeCounter = 0
            for _pilot in gCharacterList:
                if _pilot.type == 'pilot':
                    if _pilot.msgTimeCount > 0:
                        _pilot.msgTimeCount -= 1
                        if _pilot.msgTimeCount == 0:
                            _pilot.msg = ''

        _pilotList = []
        for _pilot in gCharacterList:
            if _pilot.type == 'pilot':
                updatePosition(_pilot)
                if (_pilot.attack != 0) and ((time.time()-_pilot.attack) > _attackTime):
                    _pilot.attack = 0

                if _pilot.attack != 0:
                    _weapen = Object()
                    _weapen.id = _pilot.id
                    _weapen.width = _pilot.width/2
                    _weapen.height = _pilot.height
                    if _pilot.direction == 'right':
                        _weapen.X = _pilot.X + _pilot.width/2 + _weapen.width/2
                        _weapen.Y = _pilot.Y
                    else:
                        _weapen.X = _pilot.X - _pilot.width/2 - _weapen.width/2
                        _weapen.Y = _pilot.Y
                    _weapenCollision = rectCollision(_weapen, gCharacterList)
                    if _weapenCollision[0]:
                        _pilot.attack = 0
                        for _beHitPilot in gCharacterList:
                            if _beHitPilot.id == _weapenCollision[1]:
                                _beHitPilot.HP -= 1
                                break
                        print(_weapenCollision[1])

                if (time.time() - _pilot.connectTimeOut) > _offlineTime:
                    if _pilot.connectTimeOut == 0:
                        addNewMsgToBox('系統公告', _pilot.name + ' 離開遊戲')
                        gCharacterList.remove(_pilot)
                        print('delete: ' + str(_pilot.id))
                    _pilot.connectTimeOut = 0

                _pilotList.append(_pilot.__dict__)

        gPilotListInJSON.update({'list': _pilotList})
        time.sleep(gFrameTime)

def updatePosition(pilot):
    global gPilotStep
    global gCharacterList

    _P1 = [pilot.X, pilot.Y]
    _P2 = [pilot.targetX, pilot.targetY]
    _dX = _P1[0] - _P2[0]
    _dY = _P1[1] - _P2[1]
    if distance(_P1, _P2) < 1:
        return True
    else:
        _step = gPilotStep
        _d = round(distance(_P1, _P2))
        _howManyTimesToGo = round(_d / _step)
        if _howManyTimesToGo == 0:
            pilot.X = pilot.targetX
            pilot.Y = pilot.targetY
        else:
            if pilot.targetX > pilot.X:
                pilot.direction = 'right'
            elif pilot.targetX < pilot.X:
                pilot.direction = 'left'
            pilot.X = round(pilot.X - (_dX / _howManyTimesToGo))
            if rectCollision(pilot, gCharacterList)[0]:
                pilot.X = round(pilot.X + (_dX / _howManyTimesToGo))
                pilot.targetX = pilot.X
                pilot.targetY = pilot.Y
            pilot.Y = round(pilot.Y - (_dY / _howManyTimesToGo))
            if rectCollision(pilot, gCharacterList)[0]:
                pilot.Y = round(pilot.Y + (_dY / _howManyTimesToGo))
                pilot.targetX = pilot.X
                pilot.targetY = pilot.Y
        return False

def rectCollision(pilot, gCharacterList):
    _id = 0
    _margin = 0
    _returnState = False
    for ind, _obj in enumerate(gCharacterList):
        if pilot.id != _obj.id:
            _minX1 = pilot.X - pilot.width / 2 + _margin
            _maxX1 = pilot.X + pilot.width / 2 - _margin
            _minY1 = pilot.Y - pilot.height / 2 + _margin
            _maxY1 = pilot.Y + pilot.height / 2 - _margin
            _minX2 = _obj.X - _obj.width / 2 + _margin
            _maxX2 = _obj.X + _obj.width / 2 - _margin
            _minY2 = _obj.Y - _obj.height / 2 + _margin
            _maxY2 = _obj.Y + _obj.height / 2 - _margin
            if _maxX1 > _minX2 and _maxX2 > _minX1 and _maxY1 > _minY2 and _maxY2 > _minY1:
                _returnState = True
                _id = gCharacterList[ind].id
                return _returnState, _id

    return _returnState, _id

def distance(P1, P2):
    _dX = P1[0] - P2[0]
    _dY = P1[1] - P2[1]
    return math.sqrt((_dX ** 2) + (_dY ** 2))

if __name__ == "__main__":
    global gCharacterList
    global gPilotList
    global gPilotListInJSON
    global gTimeCounter
    global gFrameTime           # Frame per second
    global gPilotVilocity       # pixel / s
    global gPilotStep           # Pixel per frame
    global gMsgBox
    global gMyID

    try:
        gMyID = 0
        gCharacterList = []
        gTimeCounter = 0
        gFrameTime = 0.05
        gPilotVilocity = 350
        gPilotStep = gPilotVilocity * gFrameTime
        gMsgBox = []
        gPilotList = []
        gPilotListInJSON = {}

        # 建立一個子執行緒
        t = threading.Thread(target=updateAll)
        # 執行該子執行緒
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

