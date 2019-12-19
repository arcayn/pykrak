import Constants
import random
from Scorers import ngram_loader

######## BASE CLASSES

class Starter:
    def __init__(self,alphabet=Constants.alphabets['en']):
        self.alphabet = alphabet
################################

############ BASIC STARTERS

class RandomAlphabet(Starter):
    def generate(self,**kwargs):
        return random.shuffle(self.alphabet)

class RandomKey(Starter):
    def generate(self,**kwargs):
        try:
            ln = kwargs['ln']
        except:
            ln = len(self.alphabet)
        return ''.join([self.alphabet[random.randint(0, len(self.alphabet)-1)] for x in range(ln)])

class RandomInteger(Starter):
    def generate(self,**kwargs):
        try:
            ln = kwargs['max']
        except:
            ln = len(self.alphabet) - 1

        return random.randint(0,ln)

#####################################

############## SPECIAL STARTERS

class FixedInteger(Starter):
    def generate(self,**kwargs):
        try:
            return kwargs['i']
        except:
            return 0

class FrequencyAnalysisStarter(Starter):
    def __init__(self,m='',lang='en',alphabet=Constants.alphabets['en']):
        self.alphabet = alphabet
        self.lang = lang
        self.msg = m

    def generate(self,**kwargs):
        try:
            m = kwargs['m']
        except:
            m = self.msg
        counts = {}
        order = ngram_loader(1,self.lang,['order'])['order']
        for ch in m:
            if ch not in self.alphabet:
                continue
            try:
                counts[ch] += 1
            except:
                counts[ch] = 1

        for c in self.alphabet:
            if c not in counts:
                counts[c] = 0

        m_tup = [[k,counts[k]] for k in counts]
        m_tup = sorted(m_tup, key=lambda x: x[1])
        m_tup.reverse()

        key = ""
        for x in range(len(self.alphabet)):
            pos = 0
            for i in range(len(order)):
                if order[i] == self.alphabet[x]:
                    pos = i
                    break
            key += m_tup[pos][0]

        return key

##########################################
