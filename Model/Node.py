class Node:
    def __init__(self, letter):
        self.letter = letter
        self.leftChild = None
        self.rightChild = None

    def addLeftChild(self, child):
        self.leftChild = child

    def addRightChild(self, child):
        self.rightChild = child

    def getLeftChild(self):
        return self.leftChild

    def getLetter(self):
        return self.letter

    def setLetter(self, letter):
        self.letter = letter
