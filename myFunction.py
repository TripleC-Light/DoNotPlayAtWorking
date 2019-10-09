import uuid
import time
import json
import math

def getUniqueID():
    # _getUID = False
    # while not _getUID:
    #     _UID = uuid.uuid1()
    #     if _UID not in _IDlist:
    #         _getUID = True
    # return _UID
    return str(uuid.uuid1())[0:8]

def rectCollision(pilot, _objListD):
    _start = time.time()
    _id = 0
    _margin = 5
    _returnState = False
    _ObjIDs = list(_objListD.keys())
    for _key in _ObjIDs:
        if pilot.id != _objListD[_key].id:
            _minX1 = pilot.X - pilot.width / 2 + _margin
            _maxX1 = pilot.X + pilot.width / 2 - _margin
            _minY1 = pilot.Y - pilot.height / 2 + _margin
            _maxY1 = pilot.Y + pilot.height / 2 - _margin
            _minX2 = _objListD[_key].X - _objListD[_key].width / 2 + _margin
            _maxX2 = _objListD[_key].X + _objListD[_key].width / 2 - _margin
            _minY2 = _objListD[_key].Y - _objListD[_key].height / 2 + _margin
            _maxY2 = _objListD[_key].Y + _objListD[_key].height / 2 - _margin
            if _maxX1 > _minX2 and _maxX2 > _minX1 and _maxY1 > _minY2 and _maxY2 > _minY1:
                _returnState = True
                _id = _objListD[_key].id
                return _returnState, _id
    # print(time.time()-_start)
    return _returnState, _id

def distance(P1, P2):
    _dX = P1[0] - P2[0]
    _dY = P1[1] - P2[1]
    return math.sqrt((_dX ** 2) + (_dY ** 2))

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
