#!/usr/bin/python
# encoding: utf-8

def lines(file):
    """
    生成器,在文本最后加一空行
    """
    for line in file: yield line
    yield '\n'
#分离每一行
def blocks(file):
    """
    生成器,生成单独的文本块
    """
    block = []
    for line in lines(file):
        if line.strip():
        #strip()删除空格符，如果有内容就保留
            block.append(line)
        elif block:
        #如果遇到换行，则测试block是否为空，不为空则返回这一个文字块
            yield ''.join(block).strip()
            block = []
