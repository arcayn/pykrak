#########################################
# Scorers.py                            #
# 19/12/2019                            #
#                                       #
# Provides builtin fitness testers and  #
# helper classes/functions for creating #
# them                                  #
#########################################

import math
from copy import copy as shallowcopy
import pkg_resources
import random

# 5+grams are not supported as they show no significant increase in decryption accuracy
# or decryption time, and smoothing becomes more difficult and can lead to a decrease in
# score accuracy

ngramfiles = {
    1: 'mgrams.txt',
    2: 'bigrams.txt',
    3: 'trigrams.txt',
    4: 'quadgrams.txt'
}

dictionary_files = {
    'fast': 'fast_dict.txt'
}

class Dictionary:
    def __init__(self,lang='en',t='fast'):
        self.words = []
        file = pkg_resources.resource_filename(__name__,'data/' + lang + '/' + dictionary_files[t])
        
        for line in open(file):
            self.words.append(line)

        self.counter = 0
        self.word_count = len(self.words)

    def get_word(self,i):
        return self.words[i]

    def get_random_word(self):
        i = random.randint(0,self.word_count-1)
        return [self.words[i], i]

    def get_nearby_word(self,i,radius=1000):
        i += (random.randint(-radius,radius))%(self.word_count-1)
        return [self.words[i], i]

    def get_next_word(self):
        r = self.words[self.counter]
        self.counter = (self.counter + 1)%(self.word_count - 1)
        return [r,self.counter]

    def find_word(self,w):
        return self.words.index(w)

    def reset(self):
        self.counter = 0

def ngram_loader(n,lang='en',query=['counts', 'order', 'frequencies', 'sum'],sep=' '):
    ngrams = {}
    ret = {}
    file = pkg_resources.resource_filename(__name__,'data/' + lang + '/' + ngramfiles[n])

    for line in open(file):
        key,count = line.split(sep)
        key = key.lower()
        ngrams[key] = int(count)

    L = len(key)
    N = sum([ngrams[k] for k in ngrams])
    #print (file)

    if 'counts' in query:
        ret['counts'] = shallowcopy(ngrams)
    if 'order' in query:
        ret['order'] = [k[0] for k in sorted([[k,ngrams[k]] for k in ngrams], key=lambda x: x[1])]
        ret['order'].reverse()
    if 'frequencies' in query:
        for ngram in ngrams:
            ngrams[ngram] = ngrams[ngram]/N
        ret['frequencies'] = shallowcopy(ngrams)
    if 'sum' in query:
        ret['sum'] = N

    return ret

class MarkovScorer:
    def __init__(self,mode,lang='en',base_weight=1):
        self.scorers = []
        self.weights = []

        # Where possible, stop dodgy values from getting into the system and being unhandled later
        try:
            if type(mode) == int:
                # Set up int modes
                self.weights.append(base_weight)
                self.scorers.append(NgramComponent(mode,lang))
                self.component_length = 1
                return

            # Ser up non-int modes
            self.component_length = len(mode)
            for m in mode:
                self.weights.append(base_weight if type(m) == int else m[1])
                self.scorers.append(NgramComponent((m if type(m) == int else m[0]),lang))
        except:
                raise ValueError("Invalid mode {}".format(str(mode)))

    def score(self,msg,mode='p'):
        # Generate weighted average of each ngram mode
        total = sum([self.scorers[x].score(msg)*self.weights[x] for x in range(self.component_length)])
        return (-1 if mode == 'p' else 1)*(total/self.component_length)
        

class NgramComponent:
    def __init__(self,n,lang='en',strategy='log-likelihood'):
        # Broadly a python2->3 port of PracticalCryptography's code as I also use their dataset
        # So far, only a log-likelihood approach is implemented, but maybe more will come soon

        self.strategy = strategy
        
        # Load ngrams from file
        query = ngram_loader(n,lang,['counts', 'sum'])
        
        self.ngrams = query['counts']
        self.L = n
        self.N = query['sum']

        # Calculate log probabilites
        # I use ln here for better SA results
        for key in self.ngrams:
            self.ngrams[key] = math.log(self.ngrams[key]/self.N)

        # Implement basic smoothing
        # TODO: Add more advanced smoothing techniques
        self.baseline = math.log(0.01/self.N)


    def score(self,text,strategy='log-likelihood'):
        # Make sure all internal handling is done lowercase
        text = text.lower()
        score = 0
        count = len(text)-self.L+1
        
        # Score the code here
        for i in range(count):
            if text[i:i+self.L] in self.ngrams:
                score += self.ngrams[text[i:i+self.L]]
            else:
                score += self.baseline
        return score
