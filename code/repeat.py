'''
重复队列ReapeatQueue检查局面是否重复
保证电脑不走重复的棋,防止长将等情况
'''

class RepeatQueue:
    def __init__(self, length=5):
        self.length = length
        self.rqueue = [-1 for _ in range(length)]
        self.head = 0

    # 将局面的zobrist的值放入队列中
    def push(self, val):
        self.head %= self.length      # 循环
        self.rqueue[self.head] = val
        self.head += 1
    
    # 将局面弹出队列(在悔棋的时候,弹出上一步/两步,但不恢复更早的记录的值)
    def pop(self):
        self.head -= 1
        self.head %= self.length
        pop_val = self.rqueue[self.head]
        self.rqueue[self.head] = -1
        return pop_val

    # 检查最近length(5)个局面内是否出现重复
    def has_repeat(self, val):
        if val in self.rqueue:
            return True
        return False
    

if __name__ == '__main__':
    q = RepeatQueue()
    for i in range(10):
        if q.has_repeat(i % 3):
            print(i, i % 3)
        q.push(i % 3)