import Constants
import random
import Scorers
from Scorers import ngram_loader, Dictionary
from Mutators import DictionaryMutator

######## BASE CLASSES

class Starter:
    def __init__(self,alphabet=Constants.alphabets['en'],**kwargs):
        self.alphabet = alphabet
################################

############ BASIC STARTERS

class RandomAlphabet(Starter):
    def generate(self,**kwargs):
        alphabet = self.alphabet
        if 'removes' in kwargs:
            for r in kwargs['removes']:
                alphabet = alphabet.replace(r,'')
        alph_list = list(alphabet)
        random.shuffle(alph_list)
        return ''.join(alph_list)

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

class RandomWord(Starter):
    def __init__(self,alphabet=Constants.alphabets['en'],language='en',d_type='fast'):
        self.alphabet = alphabet
        self.dm = DictionaryMutator(language=language,d_type=d_type)
        
    def generate(self,**kwargs):
        try:
            keygen = kwargs['keygen']
        except:
            keygen = self.dm.no_change
        return keygen(self.dm.dict.get_random_word()[0],**kwargs)

#####################################

############## SPECIAL STARTERS

class FixedInteger(Starter):
    def generate(self,**kwargs):
        try:
            return kwargs['i']
        except:
            return 0

class AffineStarter(Starter):
    def generate(self,**kwargs):
        return [1,0]

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
