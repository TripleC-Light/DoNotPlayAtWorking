import time
import random

class Script:
    def __init__(self):
        self.Start = False
        self.state = 0
        self.region = ''
        self.objCtrl = ''
        self.objList = {}
        self.mapSize = []
        self.itemID = 0
        self.oldSysTime = 0
        self.msgCtrl = ''
        self.mapCtrl = ''

    def run(self, objList):
        region = self.region
        scene = self.state
        self.objList = objList

        if region == '0-0':
            if scene == 0:
                pilotNum = 0
                for id_ in list(objList.keys()):
                    if objList[id_].type == 'pilot':
                        pilotNum += 1
                if pilotNum >= 3:
                    self.state = 1

            elif scene == 1:
                self.msgCtrl.add('centerInfo', '出現了一個令人好奇的神祕按鈕')
                self.objCtrl.mapSize = self.mapSize
                _item = self.objCtrl.createItem('button')
                _item.id = 'Scene00Button'
                _item.name = '神秘的按鈕'
                self.itemID = _item.id
                self.objList[_item.id] = _item
                self.state = 2

            elif scene == 2:
                if self.itemID not in self.objList:
                    self.mapCtrl.shake(5)
                    self.state = 3
                    self.oldSysTime = time.time()
                    print('Push Button')

            elif scene == 3:
                if (time.time()-self.oldSysTime) > 2:
                    self.msgCtrl.add('centerInfo', '有人手癢按下了按鈕, 導致世界發生了異變')
                    self.oldSysTime = time.time()
                    self.state = 4
                    print('Push Button')

            elif scene == 4:
                if (time.time()-self.oldSysTime) > 2:
                    self.Start = True
                    item_ = self.objCtrl.createItem('Zkey')
                    item_.W = item_.W * 1.5
                    item_.H = item_.H * 1.5
                    item_.X = self.mapSize[0]/2
                    item_.Y = item_.H - 20
                    item_.tX = item_.X
                    item_.tY = item_.Y
                    item_.name = '按[Z]進行攻擊!!'
                    self.itemID = item_.id
                    self.objList[item_.id] = item_
                    for _ in range(10):
                        enemy = self.objCtrl.createCharacter('zombie')
                        self.objList[enemy.id] = enemy
                    self.state = 5

            elif scene == 5:
                enemyNum = 0
                self.objCtrl.createItemInRandom('fullHP', 0.1, 2)
                for id_ in list(objList.keys()):
                    if objList[id_].type == 'enemy':
                        enemyNum += 1
                if enemyNum == 0:
                    self.oldSysTime = time.time()
                    self.state = 6

            elif scene == 6:
                self.objCtrl.createItemInRandom('fullHP', 1, 3)
                if (time.time() - self.oldSysTime) > 1:
                    self.state = 7

            elif scene == 7:
                for _i in range(20):
                    enemy = self.objCtrl.createCharacter('zombie')
                    self.objList[enemy.id] = enemy
                self.state = 8

            elif scene == 8:
                enemyNum = 0
                self.objCtrl.createItemInRandom('fullHP', 0.1, 2)
                for id_ in list(objList.keys()):
                    if objList[id_].type == 'enemy':
                        enemyNum += 1
                if enemyNum == 0:
                    self.oldSysTime = time.time()
                    self.state = 9

            elif scene == 9:
                self.objCtrl.createItemInRandom('fullHP', 1, 3)
                if (time.time() - self.oldSysTime) > 1:
                    self.state = 10

            elif scene == 10:
                for _i in range(3):
                    enemy = self.objCtrl.createCharacter('robot')
                    self.objList[enemy.id] = enemy
                self.state = 11

            elif scene == 11:
                enemyNum = 0
                self.objCtrl.createItemInRandom('fullHP', 0.1, 2)
                for id_ in list(objList.keys()):
                    if objList[id_].type == 'enemy':
                        enemyNum += 1
                if enemyNum == 0:
                    self.oldSysTime = time.time()
                    self.state = 12

            elif scene == 12:
                print('Stage Clear')
                self.objCtrl.createItemInRandom('fullHP', 1, 3)
                self.msgCtrl.add('centerInfo', '敵人已全部消滅, 世界暫時恢復了和平')
                self.objList[self.itemID].timeOut = 0
                self.Start = False
                self.state = 0

            # print('Scene: ' + str(scene))
