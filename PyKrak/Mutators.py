import Constants
import random
from Scorers import ngram_loader, Dictionary,dictionary_files
from copy import copy
import pkg_resources

######## BASE CLASSES

class Mutator:
    def __init__(self,alphabet=Constants.alphabets['en']):
        self.queries = 0
        self.tested = []
        self.alphabet = alphabet

    def reset(self):
        self.queries = 0
        self.tested = []

################################

######### BASIC MUTATORS

class SwapMutator(Mutator):
    def generate(self,s,**kwargs):
        a = random.randint(0,len(s)-1)
        b = random.randint(0,len(s)-1)
        s = list(s)
        s[a],s[b] = s[b],s[a]
        return ''.join(s)

class SubMutator(Mutator):
    def generate(self,s,**kwargs):
        i = random.randint(0,len(s)-1)
        l_k = list(s)
        l_k.insert(i,self.alphabet[random.randint(0,len(self.alphabet)-1)])
        l_k.pop(i+1)
        return ''.join(l_k)      

class GrowthMutator(Mutator):
    def generate(self,s,**kwargs):
        s += self.alphabet[random.randint(0,len(self.alphabet)-1)]
        return s

class IncrementMutator(Mutator):
    def generate(self,s,**kwargs):
        try:
            m = kwargs['top']
        except:
            m = 1
        s += random.randint(1,m)
        try:
            s = s%kwargs['mod']
        except:
            s = s

        if 'systematic' in kwargs and s == 0:
            return None
        return s

#####################################

######### SPECIAL MUTATORS

class StoredMutator(Mutator):
    def generate(self,s,**kwargs):
        try:
            mut = kwargs['mut']
        except:
            mut = SwapMutator(self.alphabet)

        try:
            stop = kwargs['stop']
        except:
            stop = -1

        r = mut.generate(s, **kwargs)
        tries = 0
        while r in self.tested and (stop == -1 or tries <= stop):
            r = mut.generate(s, **kwargs)
            tries += 1
        return r

class RepeaterMutator(Mutator):
    def generate(self,s,**kwargs):
        try:
            mode = kwargs['mode']
        except:
            mode = [0.2,0.33]

        try:
            n = kwargs['n']
        except:
            n = 1

        try:
            mut = kwargs['mut']
        except:
            mut = SwapMutator(self.alphabet)

        c = self.queries/n

        r = mut.generate(s, **kwargs)
        for i in mode:
            if c < i:
                r = mut.generate(r, **kwargs)

        self.queries += 1
        return r

class DictionaryMutator(Mutator):
    def __init__(self,alphabet=Constants.alphabets['en'],language='en',d_type='fast',**kwargs):
        self.dict = Dictionary(language,d_type)
        self.alphabet = alphabet
        self.queries = 0

    def no_change(self, s, **kwargs):
        return s

    def alphabetizer(self,s,**kwargs):
        t_alph = self.alphabet
        if 'removes' in kwargs:
            for r in kwargs['removes']:
                t_alph = t_alph.replace(r,'')
        k = ''
        for ch in s:
            if ch in k or ch not in t_alph:
                continue
            k += ch
            t_alph.replace(ch,'')
        for ch in t_alph:
            if ch in k:
                continue
            k += ch

        return k
    
    def generate(self,s,**kwargs):
        try:
            lang = kwargs['lang']
        except:
            lang = 'en'
            
        try:
            dictionary = kwargs['dict']
        except:
            dictionary = self.dict

        try:
            key_generator = kwargs['keygen']
        except:
            key_generator = self.no_change

        if 'systematic' in kwargs:
            word = dictionary.get_next_word()
            if word[1] == 0 and self.queries != 0:
                return None

            word = word[0]

        else:
            if self.queries == 0:
                self.queries = random.randint(0,dictionary.word_count - 1)
            w = dictionary.get_nearby_word(self.queries)
            self.queries = w[1]
            word = w[0]

        return key_generator(word,**kwargs)

    def reset(self):
        self.dict.reset()
        self.queries = 0

        

#####################################

############ CIPHER MUTATORS

class AffineMutator(Mutator):
    def coprime(self, a, m): 
        a = a % m
        for x in range(1, m): 
            if ((a * x) % m == 1): 
                return False
        return True
    
    def generate(self,k,**kwargs):
        k = copy(k)
        try:
            inc = kwargs['inc']
        except:
            inc = 1

        inc = random.randint(1,inc)
        
        if k[1] >= len(self.alphabet):
            k[1] = 0
            if k[0] >= len(self.alphabet):
                k[0] = 1
                if 'systematic' in kwargs:
                    return None
            else:
                k[0] += inc
                while self.coprime(k[0], len(self.alphabet)):
                    k[0] += inc
                    if k[0] >= len(self.alphabet):
                        k[0] = 1
                        if 'systematic' in kwargs:
                            return None
        else:
            k[1] += inc

        return k
        

#####################################

