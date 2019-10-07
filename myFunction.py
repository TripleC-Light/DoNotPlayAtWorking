import uuid
import time

def getUniqueID():
    # _getUID = False
    # while not _getUID:
    #     _UID = uuid.uuid1()
    #     if _UID not in _IDlist:
    #         _getUID = True
    # return _UID
    return str(uuid.uuid1())[0:8]

def rectCollision(pilot, objList):
    _start = time.time()
    _id = 0
    _margin = 5
    _returnState = False
    for ind, _obj in enumerate(objList):
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
                _id = objList[ind].id
                return _returnState, _id
    print(time.time()-_start)
    return _returnState, _id
