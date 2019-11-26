import uuid
import json
import math
import random
from os import listdir
from os.path import isfile, isdir, join

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

    if (obj.W % 2) != 0:
        obj.W += 1
    if (obj.H % 2) != 0:
        obj.H += 1
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

def getAllPilot():
    path = "static/pilot"  # 指定要列出所有檔案的目錄
    files = listdir(path)  # 取得所有檔案與子目錄名稱
    allPilot = []
    for f in files:
        fullpath = join(path, f)  # 產生檔案的絕對路徑
        if isdir(fullpath) and f != 'item' and f != 'zombie' and f != 'robot':
            allPilot.append(f)
    return allPilot

def haveIllegalChar(inputStr):
    illegalCharList = ['\\', '@', ';', '"', '>', '<']
    for illegalChar in illegalCharList:
        if illegalChar in inputStr:
            return True

    return False

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
        self.centerInfo = ['centerInfo', '']
        self.box = [['系統公告', '遊戲開始']]
        self.maxNum = 6

    def add(self, _name, _msg):
        if len(self.box) >= self.maxNum:
            _tmp = self.box[1:]
            self.box = _tmp
        if _name == 'centerInfo':
            self.centerInfo = ['centerInfo', _msg]
        else:
            self.box.append([_name, _msg])

    def returnToWeb(self):
        _returnDataInJSON = {}
        _returnDataInJSON['centerInfo'] = self.centerInfo
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

class MapCtrl:
    def __init__(self):
        self.CMD = ''
        self.mapRegion = ''
        self.mapObjInJSON = {}
        self.mapObjList = []

    def set(self):
        filename = './static/map/setting/' + self.mapRegion + '.map'
        with open(filename, 'r', encoding='utf-8') as fRead:
            for line in fRead:
                line = line.strip()
                line = line.split(':')
                type_ = line[0]
                if type_ == 'region':
                    self.mapObjInJSON['region'] = line[1]
                elif type_ == 'size':
                    description = line[1].split(',')
                    gMapSize = [int(description[0]), int(description[1])]
                    self.mapObjInJSON['size'] = [int(description[0]), int(description[1])]
                elif type_ == 'background':
                    self.mapObjInJSON['background'] = './static/map/background/' + line[1]
                elif type_ == 'mapObj':
                    description = line[1].split(',')
                    _obj = gObjCtrl.createMapItem(description)
                    self.mapObjList[_obj.id] = _obj
                    self.mapObjList.append(_obj.__dict__)

    def shake(self, level):
        _UID = str(uuid.uuid1())[0:8]
        self.CMD = 'mapCtrl@shake,' + _UID + ',' + str(level)

    def returnToWeb(self):
        _CMD = self.CMD
        return _CMD

class DatabaseCtrl:
    def __init__(self):
        self.databasePath = './static/userData.txt'
        self.userData = []

    def _reflashUserData(self):
        with open(self.databasePath, 'r', encoding='utf-8') as fRead:
            for line in fRead:
                line = line.replace('\n', '')
                line = line.split(',')
                _data = {'key': line[0], 'id': line[1], 'password': line[2], 'name': line[3], 'pilot': line[4]}
                self.userData.append(_data)

    def loginCheck(self, userID, password):
        self._reflashUserData()
        for ind, user in enumerate(self.userData):
            if user['id'] == userID and user['password'] in password:
                return user
        return False

    def getUser(self, key):
        self._reflashUserData()
        for ind, user in enumerate(self.userData):
            if user['key'] == key:
                return user
        return False

    def checkIDexist(self, userID):
        self._reflashUserData()
        for user in self.userData:
            if user['id'] == userID:
                return True
        return False

    def _checkKeyexist(self, userID):
        self._reflashUserData()
        for user in self.userData:
            if user['id'] == userID:
                return True
        return False

    def addData(self, signupData):
        _userData = ''
        _file = open(self.databasePath, 'a')

        _UID = ''
        while self._checkKeyexist(_UID) or _UID == '':
            _UID = str(uuid.uuid1())[0:8]
        _userData += _UID + ','
        _userData += signupData['userID'] + ','
        _userData += signupData['password'] + ','
        _userData += signupData['name'] + ','
        _userData += signupData['pilot']

        _file.write(_userData + '\n')
        _file.close()
