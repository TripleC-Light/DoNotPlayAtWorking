import uuid
import json
import math

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

def distance(P1, P2):
    _dX = P1[0] - P2[0]
    _dY = P1[1] - P2[1]
    return math.sqrt((_dX ** 2) + (_dY ** 2))

class TimeCtrl:
    def __init__(self):
        self.sysTime = 0
        self.lastsysTime = 0
        self.lastTime_ForOneSecond = 0
        self.attackTime = 0

    def oneSecondTimeOut(self):
        if self.sysTime - self.lastTime_ForOneSecond > 1:
            self.lastTime_ForOneSecond = self.sysTime
            return True
        else:
            return False

    def clearAttackTime(self, _pilot):
        if (_pilot.attack != 0) and ((self.sysTime - _pilot.attack) > self.attackTime):
            _pilot.attack = 0

    def showFPS(self):
        print('FPS: ' + str(round(1/(self.sysTime-self.lastsysTime+0.0001), 3)))
        self.lastsysTime = self.sysTime

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
