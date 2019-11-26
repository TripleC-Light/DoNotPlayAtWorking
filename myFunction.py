import uuid
import json
import math
import random
from os import listdir
from os.path import isfile, isdir, join

def getUniqueID(_IDlist):
    tryCount = 0
    UID = ''
    getUID = False
    while not getUID:
        UID = str(uuid.uuid1())[0:8]
        tryCount += 1
        if UID not in _IDlist:
            print('New ID >' + UID + ': Try ' + str(tryCount) + ' times')
            tryCount = 0
            getUID = True
    return UID

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
    dX = P1[0] - P2[0]
    dY = P1[1] - P2[1]
    return math.sqrt((dX ** 2) + (dY ** 2))

def getResize(_sizeLimit, _originSize):
    scale = 0
    wL = _sizeLimit[0]
    hL = _sizeLimit[1]
    wO = _originSize[0]
    hO = _originSize[1]
    wN = 0
    hN = 0
    if wO >= hO:
        scale = wL / wO
    else:
        scale = hL / hO
    scale = round(scale, 3)
    wN = round(wO * scale)
    hN = round(hO * scale)
    return [wN, hN]

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
        FPS = round(1/(self.sysTime-self.lastSysTime+0.0001), 2)
        # print('FPS: ' + str(_FPS))
        self.lastSysTime = self.sysTime
        return FPS

class MsgCtrl:
    def __init__(self):
        self.centerInfo = ['centerInfo', '']
        self.box = [['系統公告', '遊戲開始']]
        self.maxNum = 6

    def add(self, name, msg):
        if len(self.box) >= self.maxNum:
            tmp = self.box[1:]
            self.box = tmp
        if name == 'centerInfo':
            self.centerInfo = ['centerInfo', msg]
        else:
            self.box.append([name, msg])

    def returnToWeb(self):
        returnDataInJSON = {}
        returnDataInJSON['centerInfo'] = self.centerInfo
        returnDataInJSON['list'] = self.box
        returnData = 'SysMsg@' + json.dumps(returnDataInJSON)
        return returnData

    def filter(self, msg):
        msg = msg.replace('\t', "")
        msg = msg.replace('\T', "")
        msg = msg.replace('\\', "")
        msg = msg.replace('@', '')
        msg = msg.replace(';', '')
        msg = msg.replace('"', '\'')
        msg = msg.replace('>', "")
        msg = msg.replace('<', "")
        return msg

class MapCtrl:
    def __init__(self):
        self.CMD = ''
        self.objCtrl = ''
        self.objList = ''
        self.mapRegion = ''
        self.mapObjInJSON = {}
        self.mapObjList = []

    def set(self, mapRegion):
        self.mapRegion = mapRegion
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
                    # gMapSize = [int(description[0]), int(description[1])]
                    self.mapObjInJSON['size'] = [int(description[0]), int(description[1])]
                elif type_ == 'background':
                    self.mapObjInJSON['background'] = './static/map/background/' + line[1]
                elif type_ == 'mapObj':
                    description = line[1].split(',')
                    obj = self.objCtrl.createMapItem(description)
                    self.objList[obj.id] = obj
                    self.mapObjList.append(obj.__dict__)
        self.mapObjInJSON['ObjList'] = self.mapObjList
        return self.mapObjInJSON

    def shake(self, level):
        UID = str(uuid.uuid1())[0:8]
        self.CMD = 'mapCtrl@shake,' + UID + ',' + str(level)

    def returnToWeb(self):
        CMD = self.CMD
        return CMD

class DatabaseCtrl:
    def __init__(self):
        self.databasePath = './static/userData.txt'
        self.userData = []

    def _reflashUserData(self):
        with open(self.databasePath, 'r', encoding='utf-8') as fRead:
            for line in fRead:
                line = line.replace('\n', '')
                line = line.split(',')
                data = {'key': line[0], 'id': line[1], 'password': line[2], 'name': line[3], 'pilot': line[4]}
                self.userData.append(data)

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
        userData = ''
        file = open(self.databasePath, 'a')

        UID = ''
        while self._checkKeyexist(UID) or UID == '':
            UID = str(uuid.uuid1())[0:8]
        userData += UID + ','
        userData += signupData['userID'] + ','
        userData += signupData['password'] + ','
        userData += signupData['name'] + ','
        userData += signupData['pilot']

        file.write(userData + '\n')
        file.close()
