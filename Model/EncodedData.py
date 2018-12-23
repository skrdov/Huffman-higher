class EncodedData:
    def __init__(self, encodedWord, suffixBits):
        self.encodedWord = encodedWord
        self.suffixBits = suffixBits

    def getEncodedWord(self):
        return self.encodedWord

    def getSuffixBits(self):
        return self.suffixBits
