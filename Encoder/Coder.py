from heapq import heappush, heappop

from bitarray import bitarray

from Model.EncodedData import EncodedData
from Model.EncodingRules import EncodingRules
from Model.Node import Node


class Coder:
    def __init__(self, word, letterLength, unitLength):
        self.word = bitarray()
        self.word.frombytes(word)
        self.letterLength = letterLength
        self.unitLength = unitLength
        self.lettersDictionary = {}
        # Bitai kurie nebeiejo i raide. Pvz:. jei k = 4 ir turim žodį: 010110, tai 0101 bus viena raidė, o galune 10 nebesudarys raides
        self.suffixBits = bitarray()
        self.suffixBits, self.word = self.__getSuffixBits()
        if len(self.word) < 1:
            raise Exception('Ivesties failas negali buti mazesnis nei koduojamo zodzio ilgis')
            
        #gaunam pvz:. {a:{a:00, b:01, ..}, b:{c:0}, c:{a:0, b:10, c:11000, ...}, ...}
        self.dictionaryOfDictionaries = self.__getEncodedLettersForDictionaryOfDictionaries()

    def __getEncodedLettersForDictionaryOfDictionaries(self):
        #Gaunam pvz:. {a:{a:2kartai, b:5kartai, ..}, b:{c:100kartu}, c:{a:1kartas, b:3kartai, c:5kartai, ...}, ...}
        dictionaryOfDictionaries = self.__getDictionaryOfDictionariesLettersFrequencies()
        #Konvertuojam i listus, tam kad veliau galetume sudarineti kodus raidems
        dictionaryOfLists = self.__convertToDictionaryOfLists(dictionaryOfDictionaries)
        for key in dictionaryOfLists:
            uniqueSymbolsWithFreqs = dictionaryOfLists[key]
            #iš čia gaunam konkrecias uzkodavimo taisykles, pvz:. dictionaryOfDictionaries['c'] = {a:0, b:10, c:11000, ...}
            #Tiesiogiai nesusije su metodu apacioj, bet:
            #Kai noresim uzkoduoti sekancia raide (einamuoju metu yra tarkim 'c' raide) darom dictionaryOfDictionaries['c'] ir gausim {a:0, b:10, c:11000, ...}
            #Tada jei raide bus b, rasysim 10 ir tada pasiimsim dictionaryOfDictionaries['b'] ir koduosim kita raide pagal sita zodyna
            dictionaryOfLists[key] = self.__getLettersDictionary(uniqueSymbolsWithFreqs)
        return dictionaryOfLists
        
    def __convertToDictionaryOfLists(self, dictionaryOfDictionaries):
        for element in dictionaryOfDictionaries.items():
            listItems = self.__getListItem(element[1])
            dictionaryOfDictionaries[element[0]] = listItems
        return dictionaryOfDictionaries
        
    def __getDictionaryOfDictionariesLettersFrequencies(self):
        dictionaryOfDictionaries = {}
        bitsToTake = self.letterLength * self.unitLength
        i = 0
        #pvz kai unit=2 imam 'ab', ziurim kokia sekanti pora (tarkim) 'ac', pagal tai pildom daznius
        while i < len(self.word) - bitsToTake:
            lettersUnit = self.word[i:i+bitsToTake]
            if lettersUnit.to01() not in dictionaryOfDictionaries:
                dictionaryOfDictionaries[lettersUnit.to01()] = {}
            lettersDictionary = dictionaryOfDictionaries[lettersUnit.to01()]
            nextLettersUnit = self.word[i+bitsToTake:i+2*bitsToTake]
            if nextLettersUnit.to01() in lettersDictionary:
                lettersDictionary[nextLettersUnit.to01()] += 1
            else:
                lettersDictionary[nextLettersUnit.to01()] = 1
            i += bitsToTake
        return dictionaryOfDictionaries
    
    def __getListItem(self, dict):
        list = []
        for key, value in dict.items():
            list.append([key, value])
        return list
        
    def __getSuffixBits(self):
        suffixBitsLength = len(self.word) % (self.letterLength * self.unitLength)
        if suffixBitsLength == 0:
            return bitarray(), self.word
        suffixBits = self.word[len(self.word) - suffixBitsLength:len(self.word)]
        return suffixBits, self.word[:len(self.word) - suffixBitsLength]

    def getEncodingRules(self):
        rootsDictionary = {}
        treeBitsDict = {}
        for item in self.dictionaryOfDictionaries.items():
            dict = item[0]
            innerDict = self.dictionaryOfDictionaries[dict]
            listOfItems = []
            for elem in innerDict.items():
                listOfItems.append(elem)
            rootsDictionary[item[0]] = self.__createTree(listOfItems)
            treeBits = self.__getEncodingRulesForCertainLettersUnit(rootsDictionary[item[0]])
            #Jei zodyne tera viena raide pvz a: {b:0}, tai medis lieka neuzpildytas (lieka bitukas '1' tuscias). Tai cia darom taip, kad tinkamai galetu dekoduoti,
            #nebeieskant '1' po to kai dekuoduotas '0'
            treeBits = self.__convertToSuitableFormat(treeBits)
            #print(len(treeBits))
            treeBitsDict[item[0]] = treeBits
        firstLettersUnit = self.word[:self.letterLength*self.unitLength]
        encodingRules = EncodingRules(treeBitsDict, self.letterLength, self.unitLength, len(self.dictionaryOfDictionaries), firstLettersUnit)
        return encodingRules
        
    def __convertToSuitableFormat(self, treeBits):
        lettersUnitLength = self.letterLength * self.unitLength
        if len(treeBits) == 2 + lettersUnitLength:
            del treeBits[0]
        return treeBits
        
    # Gaunam taisykles. Pvz:. 1110a110b... -> a dekoduojama i 000
    def __getEncodingRulesForCertainLettersUnit(self, node):
        str = bitarray()
        if node.getLetter() == '':
            str.append(True)
        else:
            str.append(False)
            #print(node.getLetter())
            str.extend(node.getLetter())
        if node.leftChild is not None:
            str.extend(self.__getEncodingRulesForCertainLettersUnit(node.leftChild))
        if node.rightChild is not None:
            str.extend(self.__getEncodingRulesForCertainLettersUnit(node.rightChild))
        return str

    def __createTree(self, uniqueLetters):
        rootNode = Node('')
        for letter in uniqueLetters:
            rootNode = self.__updateTree(rootNode, letter[1], letter[0])
        return rootNode

    def __updateTree(self, node, encodedLetter, letter):
        #encodedLetter = letter#self.lettersDictionary[letter]
        currentNode = node
        for i in range(0, len(encodedLetter)):
            bit = encodedLetter[i]
            if bit == 0:
                if currentNode.leftChild is None:
                    currentNode.leftChild = Node('')
                currentNode = currentNode.leftChild
            elif bit == 1:
                if currentNode.rightChild is None:
                    currentNode.rightChild = Node('')
                currentNode = currentNode.rightChild
        currentNode.setLetter(letter)
        return node

    def getEncodedData(self):
        encodedWord = bitarray()
        #encodedWord.append(False)
        bitsToRead = self.letterLength * self.unitLength
        currentUnit = self.word[0:bitsToRead]
        currentDictionary = self.dictionaryOfDictionaries[currentUnit.to01()]
        i = bitsToRead
        while i < len(self.word):
            currentUnit = self.word[i:i+bitsToRead]
            encodedUnit = currentDictionary[currentUnit.to01()]
            encodedWord.extend(encodedUnit)
            if i + bitsToRead < len(self.word):
                currentDictionary = self.dictionaryOfDictionaries[currentUnit.to01()]
            i += bitsToRead
        return EncodedData(encodedWord, self.suffixBits)

    def __getEncodedLetter(self, letter):
        return self.lettersDictionary[letter]

    # Gaunam žodyna koki simboli i koki uzkoduoti. Tai diction[a] - gaunam kaip uzkoduotas a
    def __getLettersDictionary(self, uniqueSymbolsWithFreqs):
        symbolsList = self.__splitListOfSymbolsToListOfSymbolsList(uniqueSymbolsWithFreqs)
        if len(symbolsList) == 1:
            diction = self.__createDictionaryForSymbols(symbolsList, "0", {})
        else:
            diction = self.__createDictionaryForSymbols(symbolsList, "", {})
        return diction

    # Jei turim lista [a,b,c,d], tai verciam i [[a],[b],[c],[d]]
    def __splitListOfSymbolsToListOfSymbolsList(self, uniqueSymbols):
        list = []
        for element in uniqueSymbols:
            newList = [element]
            list.append(newList)
        return list

    # gaunam dictionary raidems
    def __createDictionaryForSymbols(self, symbolsList, currentSeq, diction):
        if len(symbolsList) == 1:
            diction[((symbolsList[0])[0])[0]] = bitarray(currentSeq)
            return diction
        minHeap = self.__createHeap(symbolsList)
        while len(minHeap) != 2:
            # 2 mažiausius bucketus apjungiam i viena bucketa. Jei turim [[a],[b],[c],[d]] verciam i [[a], [b], [c,d]]
            minHeap = self.__merge2LeastBucketsIntoOne(minHeap)
            # symbolsList = self.__merge2LeastBucketsIntoOne(symbolsList)
        # Po loopo gaunam lista kuriame yra du itemai, pvz [[a, c, h, ...], [b, d, e, ...]]
        leftList = self.__splitListOfSymbolsToListOfSymbolsList(heappop(minHeap)[1])
        currentSeq = currentSeq + "0"
        diction = self.__createDictionaryForSymbols(leftList, currentSeq, diction)
        currentSeq = currentSeq[:len(currentSeq) - 1]
        rightList = self.__splitListOfSymbolsToListOfSymbolsList(heappop(minHeap)[1])
        currentSeq = currentSeq + "1"
        diction = self.__createDictionaryForSymbols(rightList, currentSeq, diction)
        return diction

    def __createHeap(self, symbolsList):
        heap = []
        for item in symbolsList:
            value = self.__calculateTotalValueOfBucket(item)
            heappush(heap, (value, item))
        return heap

    def __merge2LeastBucketsIntoOne(self, minHeap):
        least = heappop(minHeap)
        secLeast = heappop(minHeap)
        newItem = []
        newItem.extend(secLeast[1])
        newItem.extend(least[1])
        newItemValue = secLeast[0] + least[0]
        heappush(minHeap, (newItemValue, newItem))
        return minHeap

    def __calculateTotalValueOfBucket(self, bucket):
        totalValue = 0
        for item in bucket:
            totalValue = totalValue + item[1]
        return totalValue

