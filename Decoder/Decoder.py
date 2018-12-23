from bitarray import bitarray


class Decoder:
    def __init__(self, encodedData, rulesFromEncoder):
        self.encodedWord = encodedData.getEncodedWord()
        self.suffixBits = encodedData.getSuffixBits()
        self.decodingDictionary = rulesFromEncoder.getDecodingDictionary()

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
        str = bitarray()
        i = 0
        temp = bitarray()
        while i < len(self.encodedWord):
            temp.append(self.encodedWord[i])
            if self.__isEncodedLetter(temp):
                str.extend(self.decodingDictionary[temp.to01()])
                temp = bitarray()
            i += 1
        return str

    def __isEncodedLetter(self, temp):
        if temp.to01() in self.decodingDictionary:
            return True
        return False

    def __createDecodingDictionary(self, bits, letters, buildingBits):
        if bits[0] == 0:
            self.decodingDictionary[buildingBits.to01()] = letters[0]
            # print("key: %s, value: %s" % (letters[0].to01(), buildingBits.to01()))
            # print(self.decodingDictionary[''])
            # print(buildingBits.to01())
            # print(letters[0])
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
