import uuid
import json
import math
import random

def getUniqueID(_IDlist):
    _tryCount = 0
    _UID = ''
    _getUID = False
    while not _getUID:
        _UID = str(uuid.uuid1())[0:8]
        _tryCount += 1
        if _UID not in _IDlist:
            print('New ID >' + _UID + ': Try ' + str(_tryCount) + ' times')
            _tryCount = 0
            _getUID = True
    return _UID

def rectCollision(pilot, _objList):
    _id = []
    _margin = 5
    _returnState = False
    _ObjIDs = list(_objList.keys())
    _minX1 = pilot.X - pilot.W / 2 + _margin
    _maxX1 = pilot.X + pilot.W / 2 - _margin
    _minY1 = pilot.Y - pilot.H / 2 + _margin
    _maxY1 = pilot.Y + pilot.H / 2 - _margin

    for _key in _ObjIDs:
        if pilot.id != _objList[_key].id:
            _minX2 = _objList[_key].X - _objList[_key].W / 2 + _margin
            _maxX2 = _objList[_key].X + _objList[_key].W / 2 - _margin
            _minY2 = _objList[_key].Y - _objList[_key].H / 2 + _margin
            _maxY2 = _objList[_key].Y + _objList[_key].H / 2 - _margin
            if _maxX1 > _minX2 and _maxX2 > _minX1 and _maxY1 > _minY2 and _maxY2 > _minY1:
                _returnState = True
                _id.append(_objList[_key].id)

    return _returnState, _id

def getInitPosition(positionMode, mapSize, obj, gObjList):
    _collisionState = (True, 0)
    _tryCount = 0
    _XY = []
    _tmpW = obj.W
    _tmpH = obj.H
    obj.W *= 1.8
    obj.H *= 1.8
    while _collisionState[0]:
        if positionMode == 'auto':
            _XY = [0, 0]
            _XY[0] = random.randint((_tmpW/2), mapSize[0]-(_tmpW/2))
            _XY[1] = random.randint((_tmpH/2), mapSize[1]-(_tmpH/2))
        else:
            _initPoint = positionMode.split(',')
            _XY = [round(float(_initPoint[0])), round(float(_initPoint[1]))]

        obj.X = _XY[0]
        obj.Y = _XY[1]
        obj.tX = _XY[0]
        obj.tY = _XY[1]
        if positionMode == 'auto':
            _collisionState = rectCollision(obj, gObjList)
            _tryCount += 1
            if _tryCount > 1000:
                _XY = [-100, -100]
                print('Error: Already try 1000 times to find a position')
                return [-1, -1]
        else:
            _collisionState = (False, 0)

    obj.W = _tmpW
    obj.H = _tmpH
    return _XY

def distance(P1, P2):
    _dX = P1[0] - P2[0]
    _dY = P1[1] - P2[1]
    return math.sqrt((_dX ** 2) + (_dY ** 2))

def getResize(_sizeLimit, _originSize):
    _scale = 0
    _wL = _sizeLimit[0]
    _hL = _sizeLimit[1]
    _wO = _originSize[0]
    _hO = _originSize[1]
    _wN = 0
    _hN = 0
    if _wO >= _hO:
        _scale = _wL / _wO
    else:
        _scale = _hL / _hO
    _scale = round(_scale, 3)
    _wN = round(_wO * _scale)
    _hN = round(_hO * _scale)
    return [_wN, _hN]

class TimeCtrl:
    def __init__(self):
        self.sysTime = 0
        self.lastSysTime = 0
        self.lastTime_ForOneSecond = 0

    def oneSecondTimeOut(self):
        if self.sysTime - self.lastTime_ForOneSecond > 1:
            self.lastTime_ForOneSecond = self.sysTime
            return True
        else:
            return False

    def showFPS(self):
        _FPS = round(1/(self.sysTime-self.lastSysTime+0.0001), 2)
        # print('FPS: ' + str(_FPS))
        self.lastSysTime = self.sysTime
        return _FPS

class MsgCtrl:
    def __init__(self):
        self.box = [['系統公告', '遊戲開始']]
        self.maxNum = 6

    def add(self, _name, _msg):
        if len(self.box) >= self.maxNum:
            _tmp = self.box[1:]
            self.box = _tmp
        self.box.append([_name, _msg])

    def returnToWeb(self):
        _returnDataInJSON = {}
        _returnDataInJSON['list'] = self.box
        _returnData = 'SysMsg@' + json.dumps(_returnDataInJSON)
        return _returnData

    def filter(self, _msg):
        _msg = _msg.replace('\t', "")
        _msg = _msg.replace('\T', "")
        _msg = _msg.replace('\\', "")
        _msg = _msg.replace('@', '')
        _msg = _msg.replace(';', '')
        _msg = _msg.replace('"', '\'')
        _msg = _msg.replace('>', "")
        _msg = _msg.replace('<', "")
        return _msg
