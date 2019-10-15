# import time

def clearBeHITstate(_gObjList):
    for _id in list(_gObjList.keys()):
        _pilot = _gObjList[_id]
        if _pilot.type == 'pilot' or _pilot.type == 'enemy':
            _pilot.beHIT = False


# def clearAttackTime(_pilot):
#     _sysTime = time.time()
#     if (_pilot.attack != 0) and ((_sysTime - _pilot.attack) > self.attackTime):
#         _pilot.attack = 0