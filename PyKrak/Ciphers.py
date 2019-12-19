#########################################
# Ciphers.py                            #
# 19/12/2019                            #
#                                       #
# Provides builtin fitness cipher       #
# decoders and helper functions for     #
# creating them                         #
#########################################

import Constants

class Cipher:
    def __init__(self,key='',alphabet=Constants.alphabets['en']):
        self.key = key
        self.alphabet = alphabet

    def decode(self,msg,key=None,alphabet=None):
        return msg

class CaesarShift(Cipher):
    def __init__(self,key=0,alphabet=Constants.alphabets['en']):
        self.key = key
        self.sub = SimpleSub()
        self.alphabet = alphabet

    def to_alph(self,k):
        return self.alphabet[k:] + self.alphabet[:k]
    
    def decode(self,msg,key=None,alphabet=None):
        # Initialise...
        if key is None:
            key = self.key
        if alphabet is None:
            alphabet = self.alphabet

        # Solve cipher
        return self.sub.decode(msg,self.to_alph((-1)*key),alphabet)
    
class SimpleSub(Cipher):
    def decode(self,msg,key=None,alphabet=None):
        # Initialise...
        if key is None:
            key = self.key
        if alphabet is None:
            alphabet = self.alphabet

        # Solve cipher
        r = ""
        for ch in msg:
            try:
                r += key[alphabet.index(ch)]
            except:
                r += ch
        return r
    
class Vigenere(Cipher):
    def decode(self,msg,key=None,alphabet=None):
        # Initialise...
        if key is None:
            key = self.key
        if alphabet is None:
            alphabet = self.alphabet

        # Solve cipher
        keypos = 0
        r = ""
        for ch in msg:
            try:
                r += alphabet[(alphabet.index(ch) - alphabet.index(key[keypos]) + len(alphabet))%len(alphabet)]
                keypos += 1
                if keypos == len(key):
                    keypos = 0
            except:
                r += ch
        return r
