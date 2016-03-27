import os, sys, pygame
from pygame.locals import *
import objects, config
#状态父类，所有状态都具有此属性---------------------------------
class State:
    def handle(self,event):
        #处理退出事件，各状态均可
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()
    
    def firstDisplay(self, screen):
        screen.fill(config.background_color)
        pygame.display.flip()

    def display(self, screen):
#状态父类，所有状态都具有此属性---------------------------------
        pass

class Level(State):

    def __init__(self,number=1):
        self.number = number
        #number为等级数
        #self.remaining为此等级总共铁块
        self.remaining = config.weights_per_level
        #定义速度
        speed = config.drop_speed
        
        speed += (self.number - 1) * config.speed_increase
        #增加速度
        #定义游戏对象，香蕉、铁块
        self.weight = objects.Weight(speed)
        self.banana = objects.Banana()
        both = self.weight,self.banana
        #定义游戏群组，添加所有对象
        self.sprites = pygame.sprite.RenderUpdates(both)

    def update(self, game):
        #更新位置
        #objiects中定义
        #def update(self):
        #    self.rect.top += self.speed
        #    self.landed = self.rect.top >= self.area.bottom
        self.sprites.update()

        #如果相撞，下一个游戏状态改变为GameOver()
        if self.banana.touches(self.weight):
            game.nextState = GameOver()
        #如果铁块掉下去，则调用reset()方法，重置铁块位置
        elif self.weight.landed:
            self.weight.reset()
            #剩余铁块减一
            self.remaining -= 1
            if self.remaining == 0:
                #如果过关
                game.nextState = LevelCleared(self.number)
        #不可用else，因为除了这两种状态外，还有状态铁块在空中
    #定义display方法，画出游戏类，背景
    def display(self, screen):
        screen.fill(config.background_color)
        updates = self.sprites.draw(screen)
        #更新pygame.display
        pygame.display.update(updates)
#定义暂停状态类-------------------------------------------------
class Paused(State ):
    finished = 0
    image = None
    text = ''
    #各状态有自己的处理函数，用于处理该状态下发生事件
    def handle(self, event):
        State.handle(self, event)
        #继承父类State的退出处理
        #如果发生鼠标点击、敲键盘时间
        if event.type in [MOUSEBUTTONDOWN,KEYDOWN]:
            self.finished = 1
            #游戏开始标志设置为1

    def update(self, game):
        if self.finished:
            #如果发生事件，设置下一个状态
            #具体状态在继承类设定
            game.nextState = self.nextState()
    def firstDisplay(self, screen):
        screen.fill(config.background_color)
        #显示背景
        #设置字体
        font = pygame.font.Font(None, config.font_size)
        lines = self.text.strip().splitlines()
        #得到需要打印的正文

        height = len(lines) * font.get_linesize()
        #获取屏幕中心坐标
        center,top = screen.get_rect().center
        top -= height // 2

        if self.image:
            image = pygame.image.load(self.image).convert()
            #如果继承类中有设定显示的图片
            r = image.get_rect()
            #获得图片矩阵
            top += r.height // 2
            #设置矩阵中下部位坐标
            r.midbottom = center, top -20
            #显示图片
            screen.blit(image, r)

        antialias = 1
        black = 0,0,0

        #开始显示文字------------------------------------------
        for line in lines:
            text = font.render(line.strip(),antialias,black)
            r = text.get_rect()
            r.midtop = center,top
            screen.blit(text, r)
            top += font.get_linesize()
        #开始显示文字------------------------------------------

        pygame.display.flip()
        #刷新显示
#定义暂停状态类-------------------------------------------------
#继承暂停类，设置信息类----------------------------------------
class Info(Paused):

    nextState = Level
    text = '''
    In this game you are a banana,
    trying to survive a course in
    self-defense against fruit,where the
    participants will 'defend' themselves
    against you with a 16 ton weight.'''
#继承暂停类，设置信息类----------------------------------------
#设置暂停继承类，开始类-----------------------------------
class StartUp(Paused):

    nextState = Info
    image = config.splash_image
    #开始界面
    text = '''
    Welcome to Squish.
    the game of Fruit Self-Defense'''
#设置暂停继承类，开始类-----------------------------------
#升级类------------------------------------------------
class LevelCleared(Paused):

    def __init__(self, number):
            self.number = number
            self.text = '''Level %i cleared
            Click to start next level''' % self.number
    #返回下一个状态，提升等级
    def nextState(self):
            return Level(self.number + 1)
#升级类------------------------------------------------
#定义失败类-------------------------
class GameOver(Paused):
    nextState = Level
    text = '''
    Game Over
    Click to Restart, Esc to Quit'''
#定义失败类-------------------------

class Game:

    def __init__(self,*args):
        path = os.path.abspath(args[0])
        dir = os.path.split(path)[0]
        os.chdir(dir)
        #改变目录
        self.state = None
        #初始状态，开始页面
        self.nextState = StartUp()

    def run(self):
        pygame.init()

        flag = 0
        #设置游戏屏幕-----------------------------------------
        if config.full_screen:
                flag = FULLSCREEN
        screen_size = config.screen_size
        screen = pygame.display.set_mode(screen_size,flag)

        pygame.display.set_caption('Fruit Self Defense')
        pygame.mouse.set_visible(False)
        #设置游戏屏幕-----------------------------------------

#游戏关键，状态机----------------------------------------------
        while True:
            if self.state != self.nextState:
            #判断状态变化
                self.state = self.nextState
                self.state.firstDisplay(screen)
            #获取事件
            for event in pygame.event.get():
                self.state.handle(event)
                #调用各状态的处理函数
            self.state.update(self)
            #调用各状态升级方法，更新位置等
            self.state.display(screen)
            #调用各状态的方法画出屏幕
#游戏关键，状态机----------------------------------------------
if __name__ == '__main__':
    game = Game(*sys.argv)
    game.run()
