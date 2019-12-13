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

    def updatePosition(self, pilot):
        P1 = [pilot.X, pilot.Y]
        P2 = [pilot.tX, pilot.tY]
        dX = P1[0] - P2[0]
        dY = P1[1] - P2[1]
        if abs(dX) < 1 and abs(dY) < 1:
            return True
        else:
            step = pilot.SP
            d = round(myFunc.distance(P1, P2))
            howManyTimesToGo = round(d / step)
            if howManyTimesToGo == 0:
                pilot.X = pilot.tX
                pilot.Y = pilot.tY
            else:
                if pilot.tX > pilot.X:
                    pilot.dir = 'right'
                elif pilot.tX < pilot.X:
                    pilot.dir = 'left'

                pilot.X = round(pilot.X - (dX / howManyTimesToGo))
                if myFunc.rectCollision(pilot, self.objList)[0]:
                    pilot.X = round(pilot.X + (dX / howManyTimesToGo))
                    pilot.tX = pilot.X

                pilot.Y = round(pilot.Y - (dY / howManyTimesToGo))
                if myFunc.rectCollision(pilot, self.objList)[0]:
                    pilot.Y = round(pilot.Y + (dY / howManyTimesToGo))
                    pilot.tY = pilot.Y
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
                    damage = pilot.AT - self.objList[beHitID].DEF
                    if damage > 0:
                        if self.objList[beHitID].HP > 0:
                            self.objList[beHitID].HP -= damage

    def itemCtrl(self, _whoGet, item_):
        itemType = item_.pic
        if itemType == 'fullHP':
            _whoGet.HP = 10
            item_.timeOut = 1
            print('Get Item')

        if itemType == 'button':
            item_.beHIT = True
            damage = _whoGet.AT - item_.DEF
            if damage > 0:
                if item_.HP > 0:
                    item_.HP -= damage
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

    def enemySetTargetXY(self, enemy):
        allDistance = self._getAlldistance(enemy)
        if len(allDistance) == 0:
            enemy.tX = random.randint(0, self.mapSize[0])
            enemy.tY = random.randint(0, self.mapSize[1])
        else:
            mostCloseID = min(allDistance, key=allDistance.get)
            targetPilot = self.objList[mostCloseID]
            enemy.tX = targetPilot.X
            enemy.tY = targetPilot.Y

    def _getAlldistance(self, pilot1):
        allDistance = {}
        for id_ in list(self.objList.keys()):
            pilot2 = self.objList[id_]
            if pilot2.type == 'pilot' and pilot2.HP > 0:
                allDistance[id_] = int(myFunc.distance([pilot1.X, pilot1.Y], [pilot2.X, pilot2.Y]))
        return allDistance

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

    def createItemInRandom(self, itemName, probability, quantity):
        probability = probability * 100
        itemProbability = random.randint(0, 100)
        if itemProbability <= probability:
            for _ in range(random.randint(1, quantity)):
                item_ = self.createItem(itemName)
                if item_:
                    self.objList[item_.id] = item_

    def createItem(self, itemName):
        getInitPositionFail = [-1, -1]
        item_ = Object()
        item_.id = myFunc.getUniqueID(list(self.objList.keys()))
        item_.type = 'item'
        item_.name = ''
        item_.pic = itemName
        item_.SP = 0
        item_.timeOut = round(time.time(), 3)

        sizeLimit = 60
        im = Image.open('./static/pilot/' + item_.type + '/' + item_.pic + '.gif')
        newSize = myFunc.getResize([sizeLimit, sizeLimit], im.size)
        item_.W = newSize[0]
        item_.H = newSize[1]
        XY = myFunc.getInitPosition('auto', self.mapSize, item_, self.objList)

        if itemName == 'button':
            XY = myFunc.getInitPosition(str(self.mapSize[0]/2) + ',' + str(self.mapSize[1]/2), self.mapSize, item_, self.objList)

        if XY != getInitPositionFail:
            item_.X = XY[0]
            item_.Y = XY[1]
            item_.tX = XY[0]
            item_.tY = XY[1]
            return item_
        else:
            return False

    def createCharacter(self, name_):
        getInitPositionFail = [-1, -1]
        character = Object()
        character.id = myFunc.getUniqueID(list(self.objList.keys()))
        character.timeOut = round(time.time(), 3)
        XY = myFunc.getInitPosition('auto', self.mapSize, character, self.objList)

        if name_ == 'zombie':
            character.name = '上班族殭屍'
            if XY != getInitPositionFail:
                character.type = 'enemy'
                character.pic = 'zombie'
                character.SP = random.randint(20, 100) * self.frameTime
                im = Image.open('./static/pilot/' + character.pic + '/right.gif')
                randomLimit = random.randint(80, 150)
            else:
                return False

        elif name_ == 'robot':
            character.name = '自走型殺人機械'
            if XY != getInitPositionFail:
                character.type = 'enemy'
                character.pic = 'robot'
                character.HP = 50
                character.HPmax = 50
                character.AT = 3
                character.SP = 400 * self.frameTime
                im = Image.open('./static/pilot/' + character.pic + '/right.gif')
                randomLimit = random.randint(120, 120)
            else:
                return False

        elif name_ == 'pilot':
            character.name = str(character.id)
            if XY != getInitPositionFail:
                character.type = 'pilot'
                character.pic = 'slimeUnknow'
                character.SP = 350 * self.frameTime
                im = Image.open('./static/pilot/' + character.pic + '/right.gif')
                randomLimit = random.randint(70, 70)
            else:
                return False

        character.X = XY[0]
        character.Y = XY[1]
        character.tX = XY[0]
        character.tY = XY[1]
        newSize = myFunc.getResize([randomLimit, randomLimit], im.size)
        character.W = newSize[0]
        character.H = newSize[1]

        return character

    def createMapItem(self, description):
        obj = Object()
        pic = description[0]
        X = int(description[1])
        Y = int(description[2])
        obj.type = 'mapObj'
        obj.id = myFunc.getUniqueID(list(self.objList.keys()))
        obj.name = str(obj.id)
        obj.X = X
        obj.Y = Y
        obj.tX = X
        obj.tY = Y
        if pic == 'bud':
            obj.HP = 1000
            obj.W = 70
            obj.H = 70
            obj.pic = './static/map/obj/' + pic + '.png'
        return obj
