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
from copy import copy

class Cipher:
    def __init__(self,key='',alphabet=Constants.alphabets['en']):
        self.key = key
        self.alphabet = alphabet

    def decode(self,msg,key=None,alphabet=None):
        return msg

class Playfair(Cipher):
    def __init__(self,key='',alphabet=Constants.alphabets['en']):
        self.key = key
        self.alphabet = alphabet
        if key != '':
            self.build_keysquare(key, math.floor(math.sqrt(len(key))))
        
    def build_keysquare(self,k,l):
        self.keysquare = [k[(x-1)*l:x*l] for x in range(1,1+math.floor(len(k)/l))]

    def find_in_keysquare(self,c):
        for y in range(len(self.keysquare)):
            row = self.keysquare[y]
            for x in range(len(row)):
                if row[x] == c:
                    return [x,y]

    def decode(self,msg,key='abcedfghiklmnopqrstuvwxyz',alphabet=None,ln=None):
        # Initialise...
        if alphabet is None:
            alphabet = self.alphabet
        if key is None:
            key = self.key
        if ln is None:
            ln = math.floor(math.sqrt(len(key)))
        if key is not None:
            self.build_keysquare(key,ln)

        r = ''
        if len(msg)%2 == 1:
            msg += 'x'

        for x in range(math.floor(len(msg)/2)):
            bi = msg[x*2] + msg[1+(x*2)]
            pos = [self.find_in_keysquare(c) for c in bi]
            if pos[0][0] == pos[1][0]:
                r += self.keysquare[(pos[0][1] - 1)%len(self.keysquare)][pos[0][0]] + self.keysquare[(pos[1][1] - 1)%len(self.keysquare)][pos[0][0]]
            elif pos[0][1] == pos[1][1]:
                r += self.keysquare[pos[0][1]][(pos[0][0] - 1)%len(self.keysquare[0])] + self.keysquare[pos[0][1]][(pos[1][0] - 1)%len(self.keysquare[0])]
            else:
                r += self.keysquare[pos[0][1]][pos[1][0]] + self.keysquare[pos[1][1]][pos[0][0]]

        return r   
    

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
    def decode(self,msg,key=None,alphabet=Constants.alphabets['en']):
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
    def decode(self,msg,key=None,alphabet=Constants.alphabets['en']):
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
                #r += alphabet[(alphabet.index(key[keypos])- alphabet.index(ch))%len(alphabet)]
                keypos += 1
                if keypos == len(key):
                    keypos = 0
            except:
                r += ch
        return r

class VariantBeaufort(Cipher):
    def __init__(self,key='',alphabet=Constants.alphabets['en']):
        self.key = key
        self.alphabet = alphabet
        self.sub = Vigenere()
        
    def decode(self,msg,key=None,alphabet=None):
        if key is None:
            key = copy(self.key)
        if alphabet is None:
            alphabet = self.alphabet

        v_k = ''
        for k in key:
            v_k += alphabet[(-1)*(alphabet.index(k))]


        return self.sub.decode(msg,v_k,alphabet)

class Beaufort(Cipher):
    def __init__(self,key='',alphabet=Constants.alphabets['en']):
        self.key = key
        self.alphabet = alphabet
        self.sub = VariantBeaufort()
        
    def decode(self,msg,key=None,alphabet=None):
        if key is None:
            key = copy(self.key)
        if alphabet is None:
            alphabet = self.alphabet

        v_c =''
        for c in msg:
            v_c += alphabet[(-1)*(alphabet.index(c))]

        return self.sub.decode(v_c,key,alphabet)

class Porta(Cipher):
    def decode(self,msg,key=None,alphabet=None):
        if key is None:
            key = copy(self.key)
        if alphabet is None:
            alphabet = self.alphabet

        v_k = ''
        for k in key:
            v_k += alphabet[math.floor(alphabet.index(k)/2)]

        keypos = 0
        r = ""
        second_alph = alphabet[math.floor(len(alphabet)/2):]
        first_alph = alphabet[:math.floor(len(alphabet)/2)]
        for ch in msg:
            if ch in first_alph:
                r += second_alph[(first_alph.index(ch) + alphabet.index(v_k[keypos]))%len(second_alph)]
            elif ch in second_alph:
                r += first_alph[(second_alph.index(ch) - alphabet.index(v_k[keypos]))%len(first_alph)]
            else:
                r += ch

            keypos += 1
            if keypos == len(v_k):
                keypos = 0
        return r
    

class Redefence(Cipher):
    def decode(self,msg,key=None,alphabet=None):
        if key is None:
            key = copy(self.key)

        keyword = copy(key)
        key = len(key)
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

        proto_rows = {}
        sorted_kwd = sorted(keyword)

        for k in keyword:
            ind = sorted_kwd.index(k)
            r = rowLengths[ind]
            proto_rows[ind] = list(msg[:r])
            msg = msg[r:]

        rows = []
        for x in range(key):
            rows.append(proto_rows[x])
        

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

class Railfence(Cipher):
    def __init__(self,key=2,alphabet=None):
        self.key = key
        self.sub = Redefence()
        
    def decode(self,msg,key=None,alphabet=None):
        if key is None:
            key = copy(self.key)

        return self.sub.decode(msg, range(key))
