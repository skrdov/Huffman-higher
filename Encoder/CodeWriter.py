from bitarray import bitarray


class CodeWriter:
    def __init__(self, encodingRules, encodedData):
        self.encodingRules = encodingRules
        self.encodedData = encodedData

    def writeToFile(self, fileName):
        # Rasom: 3 bitai pasako kiek uzkoduotam zodyje yra nereikalingu bituku, tam kad uzkoduotas zodis tilptu i pilna baita. + 5 bitai pasako kiek bitu liko neuzkoduotu
        # Gaunam kiek bitu nuskaityti neuzkoduotai galunei
        # Rasom neuzkoduota galune
        # Rasom medi
        # Rasom viska iki galo - uzkoduota zodi
        treeBitsDictionary = self.encodingRules.getTreeBits()
        treeBitsToWrite = self.__convertToSuitableFormat(treeBitsDictionary)
        #print(len(treeBitsToWrite))
        
        suffixBits = self.encodedData.getSuffixBits()
        suffixBitsBytes = self.__getBytesFromNonFullBits(suffixBits)
        
        letterLength = self.encodingRules.getLetterLength()
        letterLengthByte = self.__int_to_bytes(letterLength)
        
        unitLength = self.encodingRules.getUnitLength()
        unitLengthByte = self.__int_to_bytes(unitLength)
        
        uniqueLetterUnits = len(treeBitsDictionary)
        uniqueLetterUnitsBytes = self.__int_to_bytes(uniqueLetterUnits)
        
        bytesForUniqueLetterUnits = len(uniqueLetterUnitsBytes)
        bytesForUniqueLetterUnitsByte = self.__int_to_bytes(bytesForUniqueLetterUnits)
        print(uniqueLetterUnits)
        
        #print(treeBitsDictionary)
        encodedWord = self.encodedData.getEncodedWord()
        print(len(encodedWord))
        print(len(treeBitsDictionary))
        
        
        treeRulesPlusEncodedWord = bitarray()
        treeRulesPlusEncodedWord.extend(treeBitsToWrite)
        treeRulesPlusEncodedWord.extend(encodedWord)
        #print(encodedWord[:25])
        treeRulesPlusEncodedWordBytes = self.__addBitsToCompleteLastByte(treeRulesPlusEncodedWord)
        trashAndSuffixBitsLengthByte = self.__getTrashAndSuffixBitsLengthByte(len(treeRulesPlusEncodedWord), len(suffixBits))
        
        firstLettersUnit = self.encodingRules.getFirstLettersUnit()
        firstLettersUnitBytes = firstLettersUnit.tobytes()
        print(firstLettersUnit)
        
        f = open(fileName, 'wb')
        f.write(trashAndSuffixBitsLengthByte)
        f.write(letterLengthByte)
        f.write(unitLengthByte)
        f.write(suffixBitsBytes)
        f.write(bytesForUniqueLetterUnitsByte)
        f.write(uniqueLetterUnitsBytes)
        
        f.write(firstLettersUnitBytes)
        f.write(treeRulesPlusEncodedWordBytes)
        f.close()

    def __convertToSuitableFormat(self, treeBitsDictionary):
        letterLength = self.encodingRules.getLetterLength()
        unitLength = self.encodingRules.getUnitLength()
        wholeStretch = bitarray()
        aaa = 0
        for item in treeBitsDictionary.items():
            if len(item[1]) == 2 + letterLength * unitLength:
                #print('HEREEEEEEEEEEEEEEEEE')
                #print(item[1])
                del (item[1])[0]
                #print(item[1])
            '''
            if aaa >= 0 and aaa <10:
                print('this---------------------------------------------------------------')
                print(item[0])
                print(item[1])
                print(len(item[1]))
            '''
            currentStretch = bitarray(item[0])
            currentStretch.extend(item[1])
            wholeStretch.extend(currentStretch)
            aaa += 1
        return wholeStretch
        
    def __getTrashAndSuffixBitsLengthByte(self, encodedWordLength, suffixBitsLength):
        if encodedWordLength % 8 == 0:
            value1 = 0
        else:
            value1 = (8 - (encodedWordLength % 8)) << 5
        return self.__int_to_bytes(value1 + suffixBitsLength)

    # Gaunam baitus, is bitu sekos kurios liekana != 0 (uzpildom vienetukais gala)
    def __getBytesFromNonFullBits(self, bits):
        # Gaunam kiek bitu reikia kad uzpildytume baita
        bitsToAdd = self.__bitsToGetFullByte(len(bits))
        # Prijungiam bitukas, kad gautume pilna baita
        bits.extend(self.__addBitsToCompleteByte(bitsToAdd))
        # Verciam i baitus
        return bits.tobytes()

    def __addBitsToCompleteByte(self, bitsToAdd):
        bits = []
        for i in range(0, bitsToAdd):
            bits.append(True)
        return bits

    def __addBitsToCompleteLastByte(self, bitArray):
        bitsToAdd = self.__bitsToGetFullByte(len(bitArray))
        bitArray.extend(self.__appendBits(bitsToAdd))
        bytes = bitArray.tobytes()
        return bytes

    def __appendBits(self, bitsToAdd):
        extraBits = bitarray()
        for i in range(0, bitsToAdd):
            extraBits.append(True)
        return extraBits

    def __bitsToGetFullByte(self, bits):
        if bits % 8 == 0:
            return 0
        else:
            return (int(bits / 8) + 1) * 8 - bits

    def __int_to_bytes(self, x):
        if x == 0:
            b = bitarray(8)
            b.setall(False)
            return b.tobytes()
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')


