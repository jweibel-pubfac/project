import pygame,config,os
from random import randrange
#游戏对象父类--------------------------------------------
class SquishSprite(pygame.sprite.Sprite):

    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load(image).convert()
        #设定图片
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        #获得屏幕
        shrink = -config.margin*2
        self.area = screen.get_rect().inflate(shrink,shrink)
        #设定屏幕区域
#游戏对象父类--------------------------------------------
class Weight(SquishSprite):

    def __init__(self, speed):
        SquishSprite.__init__(self,config.weight_image)
        
        self.speed = speed
        self.reset()
        #初始化速度
    #重置位置
    def reset(self):
        x = randrange(self.area.left, self.area.right)
        self.rect.midbottom = x, 0

    #更新位置
    def update(self):
        self.rect.top += self.speed
        self.landed = self.rect.top >= self.area.bottom
        #如果超出区域

class Banana(SquishSprite):

    def __init__(self):
        SquishSprite.__init__(self, config.banana_image)
        self.rect.bottom = self.area.bottom
        #设定在屏幕区域底部

        self.pad_top = config.banana_pad_top
        #膨胀扩张参数
        self.pad_side = config.banana_pad_side

    def update(self):
        self.rect.centerx = pygame.mouse.get_pos()[0]
        #设定位置为鼠标位置
        self.rect = self.rect.clamp(self.area)
        #必须夹在屏幕区域内

    def touches(self, other):
        bounds = self.rect.inflate(-self.pad_side,-self.pad_top)
                                        #向两边          #向上
        #将香蕉图片膨胀绑定，碰到这个扩大的区域则视为相撞

        bounds.bottom = self.rect.bottom
        #返回是否碰撞
        return bounds.colliderect(other.rect)
