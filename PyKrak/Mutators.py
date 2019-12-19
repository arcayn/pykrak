import Constants
import random
from Scorers import ngram_loader

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
        s += random.randint(1,26)
        try:
            s = s%kwargs['mod']
        except:
            s = s
        return s

#####################################

######### SPECIAL MUTATORS

class StoredMutator(Mutator):
    def generate(self,s,**kwargs):
        try:
            mut = kwargs['mut']
        except:
            mut = SwapMutator(self.alphabet)

        r = mut.generate(s, **kwargs)
        while r in self.tested:
            r = mut.generate(s, **kwargs)
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

#####################################

############ CIPHER MUTATORS

#####################################

