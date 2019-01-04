from bitarray import bitarray


class Decoder:
    def __init__(self, encodedData, rulesFromEncoder):
        self.encodedWord = encodedData.getEncodedWord()
        self.suffixBits = encodedData.getSuffixBits()
        self.decodingDictionary = rulesFromEncoder.getDecodingDictionary()
        self.decodingRules = rulesFromEncoder
        #self.currentDecodedLettersUnit = rulesFromEncoder.getFirstLettersUnit()

    def decode(self):
        decodedWord = self.__decodeWord()
        decodedWord = self.__addSuffix(decodedWord)
        return decodedWord

    # Pridedam neuzkoduota galune, nes del k gali likti neuzkoduotu bituku zodyje
    def __addSuffix(self, decodedWord):
        if len(self.suffixBits) != 0:
            return decodedWord + self.suffixBits
        else:
            return decodedWord
    def __decodeWord(self):
        encodedWord = self.encodedWord
        dictionaryOfDictionaries = self.decodingDictionary
        decodedWord = bitarray()
        currentLettersUnit = self.decodingRules.getFirstLettersUnit()
        letterXunitLength = self.decodingRules.getLetterLength() * self.decodingRules.getUnitLength()

        decodedWord.extend(currentLettersUnit)
        temp = bitarray()
        i = 0
        currentDictionary = dictionaryOfDictionaries[currentLettersUnit.to01()]
        while i < len(encodedWord):
            temp.append(encodedWord[i])
            if self.__isEncodedLetter(currentDictionary, temp):
                currentDecodedLetter = currentDictionary[temp.to01()]
                decodedWord.extend(currentDecodedLetter)
                currentLettersUnit = decodedWord[-letterXunitLength:]
                currentDictionary = dictionaryOfDictionaries[currentLettersUnit.to01()]
                temp = bitarray()
            i += 1
        return decodedWord

    def __isEncodedLetter(self, currentDictionary, temp):
        if temp.to01() in currentDictionary:
            return True
        return False

    def __createDecodingDictionary(self, bits, letters, buildingBits):
        if bits[0] == 0:
            self.decodingDictionary[buildingBits.to01()] = letters[0]
            # print("key: %s, value: %s" % (letters[0].to01(), buildingBits.to01()))
            return bits[1:], letters[1:]
        elif bits[0] == 1:
            if len(bits) > 1:
                buildingBits.append(False)
                bitss, letters = self.__createDecodingDictionary(bits[1:], letters, buildingBits)
                bits = [bits[0]]
                bits.extend(bitss)
                buildingBits.pop()
            if len(bits) > 1:
                buildingBits.append(True)
                bitss, letters = self.__createDecodingDictionary(bits[1:], letters, buildingBits)
                bits = [bits[0]]
                bits.extend(bitss)
                buildingBits.pop()
            return bits[1:], letters
        return None
