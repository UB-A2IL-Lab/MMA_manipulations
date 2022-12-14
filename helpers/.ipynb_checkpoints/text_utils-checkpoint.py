import random
import re
import json
import string

import nltk
from nltk.corpus import wordnet
import spacy
from nltk.stem import WordNetLemmatizer



from helpers.file_utils import FileUtils


class TextUtils:
    def __init__(self, cachePath, cacheUpdateThreshold=50):
        self.cachePath = cachePath
        self.antonymCachePath = f'{self.cachePath}/antonym.json'
        self.antonymCache = FileUtils.readJson(self.antonymCachePath)
        self.antonymCacheMissCount = 0
        self.cacheUpdateThreshold = cacheUpdateThreshold
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            nltk.download('wordnet')
            nltk.download('omw-1.4')
            self.nlp = spacy.load("en_core_web_sm")
        
    @staticmethod
    def getStartIdx(wordsList, idx):
        n = 0
        for i in range(idx):
            n += len(wordsList[i])

        return n + idx + 1

    @staticmethod
    def cleanString(s):
        res = []
        chars = re.escape(string.punctuation)
        for w in s.split(' '):
            rep = re.sub(r'['+chars+'].', '', w+' ')
            res.append(rep.strip())
        
        res[0] = res[0].title()
        return ' '.join(res)


    def updateAntonymCache(self):
        with open(self.antonymCachePath, 'w+') as fileDesc:
            json.dump(self.antonymCache, fileDesc)

    def getPOS(self, text):
        doc = self.nlp(text)
        return doc

    
    def getAntonyms(self, word):
        word = self.cleanString(word)
        if word in self.antonymCache:
            return self.antonymCache[word]
        
        antonyms = set()

        for syn in wordnet.synsets(word):
            for l in syn.lemmas():
                if l.antonyms():
                    antonyms.add(l.antonyms()[0].name())

        if not antonyms:
            return [] 

        self.antonymCacheMissCount += 1
        self.antonymCache[word] = list(antonyms)
        if self.antonymCacheMissCount > self.cacheUpdateThreshold:
            self.antonymCacheMissCount = 0
            self.updateAntonymCache()

        return self.antonymCache[word]

    def getAntonym(self, word, randomized=True):
        antonyms = self.getAntonyms(word)
        k = 0

        if randomized and len(antonyms) > 0:
            n = len(antonyms)
            k = random.randint(0, n-1)
        
        return antonyms[k] if antonyms else None
