from Object import Object
import myFunction as myFunc
import random

class ObjCtrl:
    def __init__(self):
        self.objList = {}
        self.sysTime = 0
        self.attackTime = 0
        self.offlineTime = 0
        self.weapen = ''
        self.mapSize = []

    def updatePosition(self, _pilot):
        _P1 = [_pilot.X, _pilot.Y]
        _P2 = [_pilot.tX, _pilot.tY]
        _dX = _P1[0] - _P2[0]
        _dY = _P1[1] - _P2[1]
        if abs(_dX) < 1 and abs(_dY) < 1:
            return True
        else:
            _step = _pilot.SP
            _d = round(myFunc.distance(_P1, _P2))
            _howManyTimesToGo = round(_d / _step)
            if _howManyTimesToGo == 0:
                _pilot.X = _pilot.tX
                _pilot.Y = _pilot.tY
            else:
                if _pilot.tX > _pilot.X:
                    _pilot.dir = 'right'
                elif _pilot.tX < _pilot.X:
                    _pilot.dir = 'left'

                _pilot.X = round(_pilot.X - (_dX / _howManyTimesToGo))
                if myFunc.rectCollision(_pilot, self.objList)[0]:
                    _pilot.X = round(_pilot.X + (_dX / _howManyTimesToGo))
                    _pilot.tX = _pilot.X

                _pilot.Y = round(_pilot.Y - (_dY / _howManyTimesToGo))
                if myFunc.rectCollision(_pilot, self.objList)[0]:
                    _pilot.Y = round(_pilot.Y + (_dY / _howManyTimesToGo))
                    _pilot.tY = _pilot.Y
            return False

    def clearBeHIT(self):
        for _id in list(self.objList.keys()):
            _pilot = self.objList[_id]
            if _pilot.type == 'pilot' or _pilot.type == 'enemy' or _pilot.type == 'item':
                _pilot.beHIT = False

    def clearAttack(self, _pilot):
        if (_pilot.attack != 0) and ((self.sysTime - _pilot.attack) > self.attackTime):
            _pilot.attack = 0

    def createWeapen(self, _pilot):
        _weapen = Object()
        _weapen.id = _pilot.id
        if _pilot.weapen == 'punch':
            _weapen.W = _pilot.W / 2
            _weapen.H = _pilot.H
            if _pilot.dir == 'right':
                _weapen.X = _pilot.X + _pilot.W / 2 + _weapen.W / 2
                _weapen.Y = _pilot.Y
            else:
                _weapen.X = _pilot.X - _pilot.W / 2 - _weapen.W / 2
                _weapen.Y = _pilot.Y
        self.weapen = _weapen
        return _weapen

    def attackJudge(self, _pilot):
        _weapenCollision = myFunc.rectCollision(self.weapen, self.objList)
        if _weapenCollision[0]:
            _pilot.attack = 0
            for _beHitID in _weapenCollision[1]:
                if self.objList[_beHitID].type == 'item':
                    self.itemCtrl(_pilot, self.objList[_beHitID])
                else:
                    self.objList[_beHitID].beHIT = True
                    _damage = _pilot.AT - self.objList[_beHitID].DEF
                    if _damage > 0:
                        if self.objList[_beHitID].HP > 0:
                            self.objList[_beHitID].HP -= _damage

    def itemCtrl(self, _whoGet, _item):
        _itemType = _item.pic
        if _itemType == 'fullHP':
            _whoGet.HP = 10
            _item.timeOut = 1
            print('Get Item')

        if _itemType == 'button':
            _damage = _whoGet.AT - _item.DEF
            if _damage > 0:
                if _item.HP > 0:
                    _item.HP -= _damage
            print('Get Item')

    def timeOut(self, _pilot):
        if (self.sysTime - _pilot.timeOut) > self.offlineTime:
            if _pilot.timeOut == 0:
                return True
            else:
                _pilot.timeOut = 0
                return False

    def HPtoZero(self, _pilot):
        if _pilot.HP == -999:
            _pilot.HP = -1000
            return True
        elif _pilot.HP == -1000:
            _pilot.HP = -1000
        elif _pilot.HP <= 0:
            _pilot.HP = -999
        return False

    def msgTimeOutCheck(self, _pilot):
        if _pilot.msgTimeCount > 0:
            _pilot.msgTimeCount -= 1
            if _pilot.msgTimeCount == 0:
                _pilot.msg = ''

    def enemySetTargetXY(self, _enemy):
        _allDistance = self._getAlldistance(_enemy)
        if len(_allDistance) == 0:
            _enemy.tX = random.randint(0, self.mapSize[0])
            _enemy.tY = random.randint(0, self.mapSize[1])
        else:
            _mostCloseID = min(_allDistance, key=_allDistance.get)
            _targetPilot = self.objList[_mostCloseID]
            _enemy.tX = _targetPilot.X
            _enemy.tY = _targetPilot.Y

    def _getAlldistance(self, _pilot1):
        _allDistance = {}
        for _id in list(self.objList.keys()):
            _pilot2 = self.objList[_id]
            if _pilot2.type == 'pilot' and _pilot2.HP > 0:
                _allDistance[_id] = int(myFunc.distance([_pilot1.X, _pilot1.Y], [_pilot2.X, _pilot2.Y]))
        return _allDistance

    def enemyAutoCtrl(self, _pilot):
        if _pilot.type == 'enemy':
            if _pilot.pic == 'zombie':
                self.enemySetTargetXY(_pilot)
                _weapen = self.createWeapen(_pilot)
                _weapenCollision = myFunc.rectCollision(_weapen, self.objList)
                if _weapenCollision[0]:
                    for _beHitID in _weapenCollision[1]:
                        if self.objList[_beHitID].type == 'pilot' and self.objList[_beHitID].HP > 0:
                            _pilot.attack = self.sysTime

    def enemyTimeReflash(self, _pilot):
        if _pilot.type == 'enemy' and _pilot.timeOut != 0:
            _pilot.timeOut = round(self.sysTime, 3)

    def itemTimeReflash(self, _item):
        if _item.type == 'item' and _item.timeOut != 0:
            _item.timeOut = round(self.sysTime, 3)
