class DecodingRules:
    def __init__(self, decodingDictionary, letterLength, unitLength, firstLettersUnit):
        self.decodingDictionary = decodingDictionary
        self.letterLength = letterLength
        self.unitLength = unitLength
        self.firstLettersUnit = firstLettersUnit
    def getDecodingDictionary(self):
        return self.decodingDictionary
    def getLetterLength(self):
        return self.letterLength
    def getUnitLength(self):
        return self.unitLength
    def getFirstLettersUnit(self):
        return self.firstLettersUnit

