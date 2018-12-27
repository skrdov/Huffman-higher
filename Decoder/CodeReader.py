from bitarray import bitarray

from Model.EncodedData import EncodedData
from Model.EncodingRules import EncodingRules
from Model.DecodingRules import DecodingRules


class CodeReader:
    def __init__(self, fileName):
        self.fileName = fileName
        self.__readFromFile()

    def getEncodedData(self):
        return self.encodedData

    def getRulesFromEncoder(self):
        return self.rulesFromEncoder

    def __readFromFile(self):
        f = open(self.fileName, 'rb')

        # Skaitom kiek bituku paskutiniame teksto baite bereiksmiai + tame paciame baite kiek liko neuzkoduotu bituku (originalaus zodzio galune)
        trashAndSuffixBitsLengthByte = f.read(1)
        trashBitsLength, suffixBitsLength = self.__getTrashAndSuffixBitsLength(trashAndSuffixBitsLengthByte)

        # Skaitom koks raides ilgis bitukais originaliame žodyje
        seekCount = 1
        f.seek(seekCount)
        letterLengthByte = f.read(1)
        self.letterLength = self.__int_from_bytes(letterLengthByte)
        
        seekCount += 1
        f.seek(seekCount)
        unitLengthByte = f.read(1)
        self.unitLength = self.__int_from_bytes(unitLengthByte)

        # Skaitom suffix bitukus (bitukai kurie nebuvo uzkoduoti, nes netilpo i ivesta raides ilgi)
        seekCount += 1
        f.seek(seekCount)
        bytesToRead = self.__getBytesAmountToRead(suffixBitsLength)
        suffixBytes = f.read(bytesToRead)
        suffixBits = self.__getSuffixBits(suffixBytes, suffixBitsLength)

        seekCount += bytesToRead
        f.seek(seekCount)
        bytesForUniqueLetterUnitsByte = f.read(1)
        bytesForUniqueLetterUnits = self.__int_from_bytes(bytesForUniqueLetterUnitsByte)
       
        
        seekCount += 1
        f.seek(seekCount)
        uniqueLetterUnitsBytes = f.read(bytesForUniqueLetterUnits)
        uniqueLetterUnits = self.__int_from_bytes(uniqueLetterUnitsBytes)
        #print(uniqueLetterUnits)
        
        firstLettersUnitBytesToRead = self.__getBytesAmountToRead(self.unitLength * self.letterLength)
        seekCount += bytesForUniqueLetterUnits
        firstLettersUnitBytes = f.read(firstLettersUnitBytesToRead)
        firstLettersUnit = bitarray()
        firstLettersUnit.frombytes(firstLettersUnitBytes)
        firstLettersUnit = firstLettersUnit[:self.unitLength * self.letterLength]
        #print(firstLettersUnit)
        
        # Skaitom  kodavimo/dekodavimo taisykles
        seekCount += firstLettersUnitBytesToRead
        f.seek(seekCount)
        
        treeAndEncodedWordBitsinBytes = f.read()
        treeAndEncodedWordBits = bitarray()
        treeAndEncodedWordBits.frombytes(treeAndEncodedWordBitsinBytes)
        
        encodedWordWithTrashBits, dict = self.__getDictionaryOfDictionaries(treeAndEncodedWordBits, uniqueLetterUnits)
        
        encodedWord = self.__filterCodedWordAdditionalBits(encodedWordWithTrashBits, trashBitsLength)
        #print(len(encodedWord))
        #print(encodedWord[-70:])
        self.rulesFromEncoder = DecodingRules(dict, self.letterLength, self.unitLength, firstLettersUnit)
        self.encodedData = EncodedData(encodedWord, suffixBits)
    def __getDictionaryOfDictionaries(self, bits, lettersCount):
        dict = {}
        bitsToTake = self.letterLength * self.unitLength
        i = 0
        while i < lettersCount:
            #print("%d is %d" % (i, lettersCount))
            lettersUnit = bits[:bitsToTake]
            bits, currentLettersDict = self.__extractEncodingDecodingRules(bits[bitsToTake:])
            dict[lettersUnit.to01()] = currentLettersDict
            i += 1
        print("end")
        #print(len(dict))
        return bits, dict
    #return rules dictionary and bits that are left
    def __extractEncodingDecodingRules(self, bits):
        dict = {}
        currentSeq = bitarray()
        leftBits, dict = self.__getEncodingDecodingDictionary(bits, dict, currentSeq)
        #print(leftBits[:25])
        return leftBits, dict
    def __getEncodingDecodingDictionary(self, bits, dict, currentSeq):
        if bits[0] == 0:
            dict[currentSeq.to01()] = bits[1:1+self.letterLength*self.unitLength]
            if len(currentSeq) == 0:
                dict['0'] = bits[1:1+self.letterLength*self.unitLength]
            return bits[1+self.letterLength*self.unitLength:], dict
        elif bits[0] == 1:
            del bits[0]
            currentSeq.append(False)
            leftBits, dict = self.__getEncodingDecodingDictionary(bits, dict, currentSeq)
            currentSeq.pop()
            currentSeq.append(True)
            leftBits, dict = self.__getEncodingDecodingDictionary(leftBits, dict, currentSeq)
            currentSeq.pop()
            return leftBits, dict

    def __getSuffixBits(self, suffixBytes, suffixBitsLength):
        if suffixBitsLength == 0:
            return bitarray()
        suffixBits = bitarray()
        suffixBits.frombytes(suffixBytes)
        suffixBits = suffixBits[:suffixBitsLength]
        return suffixBits

    def __getBytesAmountToRead(self, bits):
        if bits % 8 == 0:
            return int(bits / 8)
        else:
            return int(bits / 8) + 1

    def __getTrashAndSuffixBitsLength(self, trashAndSuffixBitsLengthByte):
        b = bitarray()
        b.frombytes(trashAndSuffixBitsLengthByte)
        trashBitsSizeBits = bitarray(8)
        trashBitsSizeBits.setall(False)
        trashBitsSizeBits[5:] = b[:3]
        suffixBitsSizeBits = bitarray(8)
        suffixBitsSizeBits.setall(False)
        suffixBitsSizeBits[3:] = b[3:]
        return self.__int_from_bytes(trashBitsSizeBits.tobytes()), self.__int_from_bytes(suffixBitsSizeBits.tobytes())

    def __chopToLetterInBitsList(self, allLettersInBitsSeq, letterLength, letterCount):
        totalBitsForLetters = letterLength * letterCount
        allLettersInBitsSeq = allLettersInBitsSeq[:totalBitsForLetters]
        i = 0
        letterInBitsList = []
        while i < len(allLettersInBitsSeq):
            currentLetterInBits = allLettersInBitsSeq[i:i + letterLength]
            letterInBitsList.append(currentLetterInBits)
            i += letterLength
        return letterInBitsList

    def __getEncodedLettersAmount(self, treeBits):
        count = 0
        for i in treeBits:
            if i == 0:
                count += 1
        return count

    def __filterCodedWordAdditionalBits(self, bits, trashBitsLength):
        return bits[:len(bits) - trashBitsLength]

    def __filterTrashBits(self, bits):
        length = len(bits)
        i = length - 1
        while bits[i] != 0:
            bits = bits[:len(bits) - 1]
            i -= 1
        return bits

    def __int_from_bytes(self, xbytes):
        return int.from_bytes(xbytes, 'big')