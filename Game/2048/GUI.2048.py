#!/usr/bin/python
#-*- coding:utf-8 -*-
import wx
import os
import random
import copy

class Frame(wx.Frame):
    def __init__(self,title):
        #继承父类-----------------
        super(Frame,self).__init__(None,-1,title,
                style=wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX^wx.RESIZE_BORDER)
        #继承父类-----------------
        #设置画界面所需颜色------------------------------------
        self.colors = {0:(204,192,179),2:(238, 228, 218),4:(237, 224, 200),
                8:(242, 177, 121),16:(245, 149, 99),32:(246, 124, 95),
                64:(246, 94, 59),128:(237, 207, 114),256:(237, 207, 114),
                512:(237, 207, 114),1024:(237, 207, 114),2048:(237, 207, 114),
                4096:(237, 207, 114),8192:(237, 207, 114),16384:(237, 207, 114),
                32768:(237, 207, 114),65536:(237, 207, 114),131072:(237, 207, 114),
                262144:(237, 207, 114),524288:(237, 207, 114),1048576:(237, 207, 114),
                2097152:(237, 207, 114),4194304:(237, 207, 114),
                8388608:(237, 207, 114),16777216:(237, 207, 114),
                33554432:(237, 207, 114),67108864:(237, 207, 114),
                134217728:(237, 207, 114),268435456:(237, 207, 114),
                536870912:(237, 207, 114),1073741824:(237, 207, 114),
                2147483648:(237, 207, 114),4294967296:(237, 207, 114),
                8589934592:(237, 207, 114),17179869184:(237, 207, 114),
                34359738368:(237, 207, 114),68719476736:(237, 207, 114),
                137438953472:(237, 207, 114),274877906944:(237, 207, 114),
                549755813888:(237, 207, 114),1099511627776:(237, 207, 114),
                2199023255552:(237, 207, 114),4398046511104:(237, 207, 114),
                8796093022208:(237, 207, 114),17592186044416:(237, 207, 114),
                35184372088832:(237, 207, 114),70368744177664:(237, 207, 114),
                140737488355328:(237, 207, 114),281474976710656:(237, 207, 114),
                562949953421312:(237, 207, 114),1125899906842624:(237, 207, 114),
                2251799813685248:(237, 207, 114),4503599627370496:(237, 207, 114),
                9007199254740992:(237, 207, 114),18014398509481984:(237, 207, 114),
                36028797018963968:(237, 207, 114),72057594037927936:(237, 207, 114)}
        #设置画界面所需颜色------------------------------------                
        self.setIcon()
        self.initGame()
        #初始化游戏
        #键盘输入  ---------------
        panel = wx.Panel(self)
        panel.Bind(wx.EVT_KEY_DOWN,self.onKeyDown)
        panel.SetFocus()
        #键盘输入  ---------------
        self.initBuffer()
        #发生事件绑定函数----------------------------------------------------
        self.Bind(wx.EVT_SIZE,self.onSize) 
        #窗口大小变化，执行onsize
        self.Bind(wx.EVT_PAINT, self.onPaint)
        #当关闭事件发生，则执行onclose
        self.Bind(wx.EVT_CLOSE,self.onClose)
        #发生事件绑定函数----------------------------------------------------
        self.SetClientSize((505,720))
        self.Center()
        self.Show()

    def initBuffer(self):
        w,h = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(w,h)
        #buffer对象，画出界面
    #窗口大小变动-----------------------
    def onSize(self,event):
        self.initBuffer()
        self.drawAll()    
    #窗口大小变动-----------------------
    def onPaint(self,event):
        dc = wx.BufferedPaintDC(self,self.buffer)
    # 关闭窗口 ----------------
    def onClose(self,event):
        self.saveScore()
        self.Destroy()
    # 关闭窗口 ----------------
    def setIcon(self):
        icon = wx.Icon("icon.ico",wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
    #加载最高分 -------------
    def loadScore(self):
        if os.path.exists("bestscore.ini"):
            ff = open("bestscore.ini")
            self.bstScore = ff.read()
            ff.close()
    #加载最高分 -------------
    def saveScore(self):
        ff = open("bestscore.ini","w")
        ff.write(str(self.bstScore))
        ff.close()
#初始化游戏--------------------------------------------------------------------------------
    def initGame(self):
        #设置画界面的字体
        self.bgFont = wx.Font(50,wx.SWISS,wx.NORMAL,wx.BOLD,face=u"Roboto")
        self.scFont = wx.Font(36,wx.SWISS,wx.NORMAL,wx.BOLD,face=u"Roboto")
        self.smFont = wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL,face=u"Roboto")
        self.curScore = 0
        self.bstScore = 0
        self.loadScore()
        #加载最高分
        self.data = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        count = 0
        #随机生成2、4-----------------
        while count<2:
            row = random.randint(0,len(self.data)-1)
            col = random.randint(0,len(self.data[0])-1)
            if self.data[row][col]!=0: continue           
            self.data[row][col] = 2 if random.randint(0,1) else 4
            count += 1
        #随机生成2、4-----------------

#初始化游戏--------------------------------------------------------------------------------


    #随机生成2或4

    #每次判断移动成功，执行随机生成---------------------------------------------    
    def putTile(self):
        available = []
        for row in range(len(self.data)):
            for col in range(len(self.data[0])):
                if self.data[row][col]==0: available.append((row,col))
        if available:
            row,col = available[random.randint(0,len(available)-1)]
            self.data[row][col] = 2 if random.randint(0,1) else 4
            return True
        return False
    #每次判断移动成功，执行随机生成--------------------------------------------- 

    #传入一组数字，依据方向可能是一列或一行，根据false、true决定合并方向--------------------------------------------------
    def update(self,vlist,direct):
        score = 0
        if direct: #up or left
            i = 1
            while i<len(vlist):
                if vlist[i-1]==vlist[i]:
                    del vlist[i]
                    vlist[i-1] *= 2
                    score += vlist[i-1]
                    i += 1
                i += 1
        else:
            i = len(vlist)-1
            while i>0:
                if vlist[i-1]==vlist[i]:
                    del vlist[i]
                    vlist[i-1] *= 2
                    score += vlist[i-1]
                    i -= 1
                i -= 1      
        return score
    #传入一组数字，依据方向可能是一列或一行，根据false、true决定合并方向--------------------------------------------------
        
#取方块行列，上下左右合并，传入update函数，返回是否顺利移动，依据方块变动，并返回该次所得分-----------------------------------------
    def slideUpDown(self,up):
        score = 0
        numCols = len(self.data[0])
        numRows = len(self.data)
        oldData = copy.deepcopy(self.data)
        
        for col in range(numCols):
            cvl = [self.data[row][col] for row in range(numRows) if self.data[row][col]!=0]

            if len(cvl)>=2:
                score += self.update(cvl,up)
            for i in range(numRows-len(cvl)):
                if up: cvl.append(0)
                else: cvl.insert(0,0)
            for row in range(numRows): self.data[row][col] = cvl[row]
        return oldData!=self.data,score

    def slideLeftRight(self,left):
        score = 0
        numRows = len(self.data)
        numCols = len(self.data[0])
        oldData = copy.deepcopy(self.data)
        
        for row in range(numRows):
            rvl = [self.data[row][col] for col in range(numCols) if self.data[row][col]!=0]

            if len(rvl)>=2:           
                score += self.update(rvl,left)
            for i in range(numCols-len(rvl)):
                if left: rvl.append(0)
                else: rvl.insert(0,0)
            for col in range(numCols): self.data[row][col] = rvl[col]
        return oldData!=self.data,score
        #使用分数变动判断有无走动
#取方块行列，上下左右合并，传入update函数，返回所得分--------------------------------------------------------------------------


    def isGameOver(self):
        copyData = copy.deepcopy(self.data)
        
        flag = False
        if not self.slideUpDown(True)[0] and not self.slideUpDown(False)[0] and \
                not self.slideLeftRight(True)[0] and not self.slideLeftRight(False)[0]:
        #如果都返回移动失败，则游戏结束
            flag = True
        #如果还能移动，恢复原状
        if not flag: self.data = copyData
        return flag
        #不能移动，返回False

    def doMove(self,move,score):
        if move:
        #if self.slideUpDown(True)等，就是如果顺利移动，分数变化
            self.putTile()
            self.drawChange(score)
            if self.isGameOver():
                if wx.MessageBox(u"游戏结束，是否重新开始？",u"哈哈",
                        wx.YES_NO|wx.ICON_INFORMATION)==wx.YES:
                    bstScore = self.bstScore
                    #初始化游戏
                    self.initGame()
                    self.bstScore = bstScore
                    self.drawAll()
#监听键盘输入，执行变动------------------------------------------------------------------------
    def onKeyDown(self,event):
        keyCode = event.GetKeyCode()
                
        if keyCode==wx.WXK_UP:
            self.doMove(*self.slideUpDown(True))
        elif keyCode==wx.WXK_DOWN:
            self.doMove(*self.slideUpDown(False))
        elif keyCode==wx.WXK_LEFT:
            self.doMove(*self.slideLeftRight(True))
        elif keyCode==wx.WXK_RIGHT:
            self.doMove(*self.slideLeftRight(False)) 
#监听键盘输入，执行变动------------------------------------------------------------------------
       
#画出界面--------------------------------------------------------------------------------------------------------             
    def drawBg(self,dc):
        dc.SetBackground(wx.Brush((250,248,239)))
        dc.Clear()
        dc.SetBrush(wx.Brush((187,173,160)))
        dc.SetPen(wx.Pen((187,173,160)))
        dc.DrawRoundedRectangle(15,150,475,475,5)

    def drawLogo(self,dc):
        dc.SetFont(self.bgFont)
        dc.SetTextForeground((119,110,101))
        dc.DrawText(u"2048",15,26)

    def drawLabel(self,dc):
        dc.SetFont(self.smFont)
        dc.SetTextForeground((119,110,101))
        dc.DrawText(u"合并相同数字，得到2048吧!",15,114)
        dc.DrawText(u"怎么玩: \n用-> <- 上下左右箭头按键来移动方块. \
                \n当两个相同数字的方块碰到一起时，会合成一个!",15,639)

    def drawScore(self,dc):            
        dc.SetFont(self.smFont)
        scoreLabelSize = dc.GetTextExtent(u"SCORE")
        bestLabelSize = dc.GetTextExtent(u"BEST")
        curScoreBoardMinW = 15*2+scoreLabelSize[0]
        bstScoreBoardMinW = 15*2+bestLabelSize[0]
        curScoreSize = dc.GetTextExtent(str(self.curScore))
        bstScoreSize = dc.GetTextExtent(str(self.bstScore))
        curScoreBoardNedW = 10+curScoreSize[0]
        bstScoreBoardNedW = 10+bstScoreSize[0]
        curScoreBoardW = max(curScoreBoardMinW,curScoreBoardNedW)
        bstScoreBoardW = max(bstScoreBoardMinW,bstScoreBoardNedW)
        dc.SetBrush(wx.Brush((187,173,160)))
        dc.SetPen(wx.Pen((187,173,160)))
        dc.DrawRoundedRectangle(505-15-bstScoreBoardW,40,bstScoreBoardW,50,3)
        dc.DrawRoundedRectangle(505-15-bstScoreBoardW-5-curScoreBoardW,40,curScoreBoardW,50,3)
        dc.SetTextForeground((238,228,218))
        dc.DrawText(u"BEST",505-15-bstScoreBoardW+(bstScoreBoardW-bestLabelSize[0])/2,48)
        dc.DrawText(u"SCORE",505-15-bstScoreBoardW-5-curScoreBoardW+(curScoreBoardW-scoreLabelSize[0])/2,48)
        dc.SetTextForeground((255,255,255))
        dc.DrawText(str(self.bstScore),505-15-bstScoreBoardW+(bstScoreBoardW-bstScoreSize[0])/2,68)
        dc.DrawText(str(self.curScore),505-15-bstScoreBoardW-5-curScoreBoardW+(curScoreBoardW-curScoreSize[0])/2,68)
    
    def drawTiles(self,dc):
        dc.SetFont(self.scFont)
        for row in range(4):
            for col in range(4):
                value = self.data[row][col]
                color = self.colors[value]
                if value==2 or value==4:
                    dc.SetTextForeground((119,110,101))
                else:
                    dc.SetTextForeground((255,255,255))
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(color))
                dc.DrawRoundedRectangle(30+col*115,165+row*115,100,100,2)
                size = dc.GetTextExtent(str(value))
                while size[0]>100-15*2:
                    self.scFont = wx.Font(self.scFont.GetPointSize()*4/5,wx.SWISS,wx.NORMAL,wx.BOLD,face=u"Roboto")
                    dc.SetFont(self.scFont)
                    size = dc.GetTextExtent(str(value))
                if value!=0: dc.DrawText(str(value),30+col*115+(100-size[0])/2,165+row*115+(100-size[1])/2)

    def drawAll(self):
        dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
        self.drawBg(dc)
        self.drawLogo(dc)
        self.drawLabel(dc)
        self.drawScore(dc)
        self.drawTiles(dc)
#画出界面-----------------------------------------------------------------------------------------------------------   
#分数改变，重画分数，方块界面-------------------------------------
    def drawChange(self,score):
        dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
        if score:
            #执行加分
            self.curScore += score
            if self.curScore > self.bstScore:
                self.bstScore = self.curScore
            self.drawScore(dc)
        self.drawTiles(dc)
#分数改变，重画分数，方块界面-------------------------------------
        
if __name__ == "__main__":
    app = wx.App()
    Frame(u"2048 v1.0.1 by heibanke")
    app.MainLoop()
