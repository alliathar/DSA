class Node():
    def __init__(self,d,n=None,p=None):
        self.data = d
        self.next_node = n
        self.prev_node = p
    def getNext(self):
        return self.next_node
    def setNext(self,n):
        self.next_node = n
    def getPrev(self):
        return self.prev_node
    def setPrev(self,p):
        self.prev_node = p
    def getData(self):
        return self.data
    def setData(self,d):
        self.data = d
    
class LinkedList():

    def __init__(self,r=None):
        self.root = r
        self.size  = 0
    def getSize(self):
        return self.size
    def add(self,d):
        newNode = Node(d,self.root)
        if self.root:
            self.root.setPrev(newNode)
        self.root = newNode
        self.size +=1
    def remove(self,d):
        thisNode = self.root
        while thisNode:
            if thisNode.getData()==d:
                next = thisNode.getNext()
                prev = thisNode.getPrev()
                if next:
                    next.setPrev(prev)
                if prev:
                    prev.setNext(next)
                else:
                    self.root = thisNode
                self.size -= 1
                return True
            else:
                thisNode=thisNode.getNext()
        return False
            
