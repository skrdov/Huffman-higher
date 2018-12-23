class EncodingRules:
    def __init__(self, treeBits, letterLength, unitLength, uniqueLettersLength):
        self.treeBits = treeBits
        self.letterLength = letterLength
        self.unitLength = unitLength
        self.uniqueLettersLength = uniqueLettersLength
    def getTreeBits(self):
        return self.treeBits
    def getLetterLength(self):
        return self.letterLength
    def getUnitLength(self):
        return self.unitLength
    def getUniqueLettersLength(self):
        return self.uniqueLettersLength

