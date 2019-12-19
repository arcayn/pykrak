#########################################
# Ciphers.py                            #
# 19/12/2019                            #
#                                       #
# Provides builtin fitness cipher       #
# decoders and helper functions for     #
# creating them                         #
#########################################

import Constants
import math

class Cipher:
    def __init__(self,key='',alphabet=Constants.alphabets['en']):
        self.key = key
        self.alphabet = alphabet

    def decode(self,msg,key=None,alphabet=None):
        return msg

class AffineShift(Cipher):
    def mod_inverse(self,a,m):
        a = a%m
        for x in range(1,m):
            if (a*x)%m == 1:
                return x

    def decode(self,msg,key=None,alphabet=None):
        # Initialise...
        if key is None:
            key = self.key
        if alphabet is None:
            alphabet = self.alphabet

        #print (key)

        # Solve cipher
        p = ''
        mod = len(alphabet)
        m_inv = self.mod_inverse(key[0], mod)
        for ch in msg:
            x = alphabet.index(ch)
            p += alphabet[(m_inv*(x - key[1]))%mod]

        return p
        

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

class Railfence(Cipher):
    def decode(self,msg,key=None):
        if key is None:
            key = self.key
            
        rowLengths = []
        val = (2*key)-2
        fulls = math.floor(len(msg)/val)
        rem = len(msg)%val
        for x in range(key):
            if x == 0 or x == (key-1):
                rowLengths.append(fulls)
            else:
                rowLengths.append(2*fulls)
                
        for i in range(rem):
            add = i
            if i >= key:
                add = (key-2)-(i%key)
            rowLengths[add] = rowLengths[add] + 1

        # GENERATE ROWS

        rows = []
        for r in rowLengths:
            rows.append(list(msg[:r]))
            msg = msg[r:]

        # READ OFF ROWS

        position = 0
        direction = -1
        message = ""
        while True:
            try:
                message += rows[position].pop(0)
            except:
                break
            
            if position%(val/2) == 0:
                direction = (-1)*direction

            position = position + direction

        return message
