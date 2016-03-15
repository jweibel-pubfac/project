#!/usr/bin/python
# encoding: utf-8

import sys, re
from handler import *
from uil import *
from rule import *

class Parser:
    """
    解析器父类
    """
    def __init__(self, handler):
        self.handler = handler
        self.rules = []
        self.filters = []

    def addRule(self, rule):
        """
        添加规则
        """
        self.rules.append(rule)

    def addFilter(self, pattern, name):
        """
        添加过滤器
        """
        def filter(block, handler):
            return re.sub(pattern, handler.sub(name), block)
        self.filters.append(filter)
        #添加规则闭包 filter 需传入参数为一行文字，处理handler类，返回re.sub('正则表达式'，'替换为的文字','需要处理的一行文字')

    def parse(self, file):
        """
        解析
        """
        self.handler.start('document')
        for block in blocks(file):
        #将文件分块
            for filter in self.filters:
                block = filter(block, self.handler)
                #如果需找到了关键字emphasis，url，mail，则替换，否则保持原有文字
                #此时block已经为替换后的文字
            for rule in self.rules:
            #迭代规则
                if rule.condition(block):
                #如果符合规则就执行,每次初始化都会更新type
                    last = rule.action(block, self.handler)
                #执行action，打印出html格式的文字
                    if last: break
                #如果有结果就停止迭代，所以如果符合前一个规则，将不会匹配下一个规则
        self.handler.end('document')
        #打印结束

class BasicTextParser(Parser):
    """
    纯文本解析器
    """
    def __init__(self, handler):
        Parser.__init__(self, handler)
        self.addRule(ListRule())
        self.addRule(ListItemRule())
        self.addRule(TitleRule())
        self.addRule(HeadingRule())
        self.addRule(ParagraphRule())

        self.addFilter(r'\*(.+?)\*', 'emphasis')
        self.addFilter(r'(http://[\.a-zA-Z/]+)', 'url')
        self.addFilter(r'([\.a-zA-Z]+@[\.a-zA-Z]+[a-zA-Z]+)', 'mail')

"""
运行程序
"""
handler = HTMLRenderer()
parser = BasicTextParser(handler)
parser.parse(sys.stdin)
