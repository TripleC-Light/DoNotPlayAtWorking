from Object import Object
import myFunction as myFunc
import random
import time
from PIL import Image

class ObjCtrl:
    def __init__(self):
        self.objList = {}
        self.sysTime = 0
        self.frameTime = 0
        self.attackTime = 0
        self.offlineTime = 0
        self.weapen = ''
        self.msgCtrl = ''
        self.msgTimeOut = 5
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
        for id_ in list(self.objList.keys()):
            pilot = self.objList[id_]
            if pilot.type == 'pilot' or pilot.type == 'enemy' or pilot.type == 'item':
                pilot.beHIT = False

    def clearAttack(self, pilot):
        if (pilot.attack != 0) and ((self.sysTime - pilot.attack) > self.attackTime):
            pilot.attack = 0

    def createWeapen(self, pilot):
        weapen = Object()
        weapen.id = pilot.id
        if pilot.weapen == 'punch':
            weapen.W = pilot.W / 2
            weapen.H = pilot.H
            if pilot.dir == 'right':
                weapen.X = pilot.X + pilot.W / 2 + weapen.W / 2
                weapen.Y = pilot.Y
            else:
                weapen.X = pilot.X - pilot.W / 2 - weapen.W / 2
                weapen.Y = pilot.Y
        self.weapen = weapen
        return weapen

    def attackJudge(self, pilot):
        weapenCollision = myFunc.rectCollision(self.weapen, self.objList)
        if weapenCollision[0]:
            pilot.attack = 0
            for beHitID in weapenCollision[1]:
                if self.objList[beHitID].type == 'item':
                    self.itemCtrl(pilot, self.objList[beHitID])
                else:
                    self.objList[beHitID].beHIT = True
                    _damage = pilot.AT - self.objList[beHitID].DEF
                    if _damage > 0:
                        if self.objList[beHitID].HP > 0:
                            self.objList[beHitID].HP -= _damage

    def itemCtrl(self, _whoGet, item_):
        _itemType = item_.pic
        if _itemType == 'fullHP':
            _whoGet.HP = 10
            item_.timeOut = 1
            print('Get Item')

        if _itemType == 'button':
            item_.beHIT = True
            _damage = _whoGet.AT - item_.DEF
            if _damage > 0:
                if item_.HP > 0:
                    item_.HP -= _damage
            print('Get Item')

    def timeOut(self, pilot):
        if (self.sysTime - pilot.timeOut) > self.offlineTime:
            if pilot.timeOut == 0:
                return True
            else:
                pilot.timeOut = 0
                return False

    def HPtoZero(self, pilot):
        if pilot.HP == -999:
            pilot.HP = -1000
            return True
        elif pilot.HP == -1000:
            pilot.HP = -1000
        elif pilot.HP <= 0:
            pilot.HP = -999
        return False

    def msgTimeOutCheck(self, pilot):
        if self.sysTime - pilot.msgTimeCount > self.msgTimeOut and pilot.msgTimeCount != 0:
            pilot.msgTimeCount = 0
            pilot.msg = ''

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
        for id_ in list(self.objList.keys()):
            _pilot2 = self.objList[id_]
            if _pilot2.type == 'pilot' and _pilot2.HP > 0:
                _allDistance[id_] = int(myFunc.distance([_pilot1.X, _pilot1.Y], [_pilot2.X, _pilot2.Y]))
        return _allDistance

    def enemyAutoCtrl(self, pilot):
        if pilot.type == 'enemy':
            if pilot.pic == 'zombie' or pilot.pic == 'robot':
                self.enemySetTargetXY(pilot)
                weapen = self.createWeapen(pilot)
                weapenCollision = myFunc.rectCollision(weapen, self.objList)
                if weapenCollision[0]:
                    for beHitID in weapenCollision[1]:
                        if self.objList[beHitID].type == 'pilot' and self.objList[beHitID].HP > 0:
                            pilot.attack = self.sysTime

    def enemyTimeReflash(self, pilot):
        if pilot.type == 'enemy' and pilot.timeOut != 0:
            pilot.timeOut = round(self.sysTime, 3)

    def itemTimeReflash(self, item_):
        if item_.type == 'item' and item_.timeOut > 1:
            item_.timeOut = round(self.sysTime, 3)

    def createItemInRandom(self, _itemName, _probability, _quantity):
        _probability = _probability * 100
        _itemProbability = random.randint(0, 100)
        if _itemProbability <= _probability:
            for _i in range(random.randint(1, _quantity)):
                item_ = self.createItem(_itemName)
                if item_:
                    self.objList[item_.id] = item_

    def createItem(self, _itemName):
        _getInitPositionFail = [-1, -1]
        item_ = Object()
        item_.id = myFunc.getUniqueID(list(self.objList.keys()))
        item_.type = 'item'
        item_.name = ''
        item_.pic = _itemName
        item_.SP = 0
        item_.timeOut = round(time.time(), 3)

        _sizeLimit = 60
        _im = Image.open('./static/pilot/' + item_.type + '/' + item_.pic + '.gif')
        _newSize = myFunc.getResize([_sizeLimit, _sizeLimit], _im.size)
        item_.W = _newSize[0]
        item_.H = _newSize[1]
        _XY = myFunc.getInitPosition('auto', self.mapSize, item_, self.objList)

        if _itemName == 'button':
            _XY = myFunc.getInitPosition(str(self.mapSize[0]/2) + ',' + str(self.mapSize[1]/2), self.mapSize, item_, self.objList)

        if _XY != _getInitPositionFail:
            item_.X = _XY[0]
            item_.Y = _XY[1]
            item_.tX = _XY[0]
            item_.tY = _XY[1]
            return item_
        else:
            return False

    def createCharacter(self, _name):
        _getInitPositionFail = [-1, -1]
        _character = Object()
        _character.id = myFunc.getUniqueID(list(self.objList.keys()))
        _character.timeOut = round(time.time(), 3)
        _XY = myFunc.getInitPosition('auto', self.mapSize, _character, self.objList)

        if _name == 'zombie':
            _character.name = '上班族殭屍'
            if _XY != _getInitPositionFail:
                _character.type = 'enemy'
                _character.pic = 'zombie'
                _character.SP = random.randint(20, 100) * self.frameTime
                _im = Image.open('./static/pilot/' + _character.pic + '/right.gif')
                _randomLimit = random.randint(80, 150)
            else:
                return False

        elif _name == 'robot':
            _character.name = '自走型殺人機械'
            if _XY != _getInitPositionFail:
                _character.type = 'enemy'
                _character.pic = 'robot'
                _character.HP = 50
                _character.HPmax = 50
                _character.AT = 3
                _character.SP = 400 * self.frameTime
                _im = Image.open('./static/pilot/' + _character.pic + '/right.gif')
                _randomLimit = random.randint(120, 120)
            else:
                return False

        elif _name == 'pilot':
            _character.name = str(_character.id)
            if _XY != _getInitPositionFail:
                _character.type = 'pilot'
                _character.pic = 'slimeUnknow'
                _character.SP = 350 * self.frameTime
                _im = Image.open('./static/pilot/' + _character.pic + '/right.gif')
                _randomLimit = random.randint(70, 70)
            else:
                return False

        _character.X = _XY[0]
        _character.Y = _XY[1]
        _character.tX = _XY[0]
        _character.tY = _XY[1]
        _newSize = myFunc.getResize([_randomLimit, _randomLimit], _im.size)
        _character.W = _newSize[0]
        _character.H = _newSize[1]

        return _character

    def createMapItem(self, _description):
        _obj = Object()
        _pic = _description[0]
        _X = int(_description[1])
        _Y = int(_description[2])
        _obj.type = 'mapObj'
        _obj.id = myFunc.getUniqueID(list(self.objList.keys()))
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
        return _obj
