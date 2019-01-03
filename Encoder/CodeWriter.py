from bitarray import bitarray


class CodeWriter:
    def __init__(self, encodingRules, encodedData):
        self.encodingRules = encodingRules
        self.encodedData = encodedData

    def writeToFile(self, fileName):
        treeBitsDictionary = self.encodingRules.getTreeBits()
        treeBitsToWrite = self.__convertToOneBitarray(treeBitsDictionary)
        
        suffixBits = self.encodedData.getSuffixBits()
        suffixBitsBytes = self.__getBytesFromNonFullBits(suffixBits) 

        #raides ilgi ir unit ilgi galim apjungti i viena baita
        letterLength = self.encodingRules.getLetterLength()
        letterLengthByte = self.__int_to_bytes(letterLength)
        
        unitLength = self.encodingRules.getUnitLength()
        unitLengthByte = self.__int_to_bytes(unitLength)
        
        #Tam kad zinotume kiek dictionary (pvz a:{a:0, b:10, ...}) reiks nuskaityti decodinant (tam kad nepradeti skaityti uzkoduoto zodzio kaip naujo 
        #medzio). O gal galima kitaip padaryti?
        uniqueLetterUnits = len(treeBitsDictionary)
        uniqueLetterUnitsBytes = self.__int_to_bytes(uniqueLetterUnits)
        #print(uniqueLetterUnits)
        
        bytesForUniqueLetterUnits = len(uniqueLetterUnitsBytes)
        #print(bytesForUniqueLetterUnits)
        bytesForUniqueLetterUnitsByte = self.__int_to_bytes(bytesForUniqueLetterUnits)
        #print(uniqueLetterUnits)
        
        #print(uniqueLetterUnits)
        encodedWord = self.encodedData.getEncodedWord()
        
        treeRulesPlusEncodedWord = bitarray()
        treeRulesPlusEncodedWord.extend(treeBitsToWrite)
        treeRulesPlusEncodedWord.extend(encodedWord)
        #print(len(encodedWord))
        trashAndSuffixBitsLengthByte = self.__getTrashAndSuffixBitsLengthByte(len(treeRulesPlusEncodedWord), len(suffixBits))
        treeRulesPlusEncodedWordBytes = self.__addBitsToCompleteLastByte(treeRulesPlusEncodedWord)

        firstLettersUnit = self.encodingRules.getFirstLettersUnit()
        firstLettersUnitBytes = firstLettersUnit.tobytes()
        #print(firstLettersUnit)
        
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
        #print(len(treeRulesPlusEncodedWordBytes))
    def __convertToOneBitarray(self, treeBitsDictionary):
        wholeStretch = bitarray()
        bitCounter = 0
        letterCount = 0
        detailsDict = {}
        for item in treeBitsDictionary.items():
            currentStretch = bitarray(item[0])
            currentStretch.extend(item[1])
            detailsDict[letterCount] = bitCounter
            bitCounter += (len(item[1]) + len(item[0]))
            letterCount += 1
            wholeStretch.extend(currentStretch)
        
        return wholeStretch
        
    def __getTrashAndSuffixBitsLengthByte(self, encodedWordLength, suffixBitsLength):
        if encodedWordLength % 8 == 0:
            value1 = 0
        else:
            value1 = (8 - (encodedWordLength % 8)) << 5
        return self.__int_to_bytes(value1 + suffixBitsLength)

    # Gaunam baitus, is bitu sekos kurios liekana != 0 (uzpildom vienetukais gala)
    def __getBytesFromNonFullBits(self, bits):
        #newBits = bitarray()
        newBits = bits.copy()
        # Gaunam kiek bitu reikia kad uzpildytume baita
        bitsToAdd = self.__bitsToGetFullByte(len(bits))
        # Prijungiam bitukas, kad gautume pilna baita
        newBits.extend(self.__addBitsToCompleteByte(bitsToAdd))
        # Verciam i baitus
        return newBits.tobytes()

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


