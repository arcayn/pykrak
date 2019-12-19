#########################################
# Solvers.py                            #
# 19/12/2019                            #
#                                       #
# Provides builtin cipher solvers and   #
# helper classes/functions for creating #
# them                                  #
#########################################

import random
import math

class Solver:
    def __init__(self,cipher,fitness,mutator,starter,iterations,**kwargs):
        self.cipher = cipher
        self.fitness = fitness
        self.mutator = mutator
        self.starter = starter
        self.iterations = iterations
        self.options = kwargs

    def parse_options(self,**kwargs):
        mutator = {}
        fitness = {}
        starter = {}

        for k in kwargs:
            if 'mutator_' in k:
                mutator[k.replace('mutator_', '')] = kwargs[k]
            if 'fitness_' in k:
                fitness[k.replace('fitness_', '')] = kwargs[k]
            if 'starter_' in k:
                starter[k.replace('starter_', '')] = kwargs[k]

        return {'mutator': mutator, 'fitness': fitness, 'starter': starter}

    def solve(self,message,**kwargs):
        return message

class HillClimb(Solver):
    def solve(self,msg,**kwargs):
        op = self.parse_options(**self.options)
        curr_k = self.starter.generate(m=msg, **op['starter'])
        curr_fit = self.fitness.score(self.cipher.decode(msg,curr_k), **op['fitness'])

        for run in range(self.iterations):
            t_k = self.mutator.generate(curr_k, **op['mutator'])
            t_dec = self.cipher.decode(msg,t_k)
            t_fit = self.fitness.score(t_dec, **op['fitness'])
            if t_fit < curr_fit:
                if 'verbose' in kwargs:
                    print ("===== BETTER KEY FOUND =====")
                    print ("Current fitness:", t_fit)
                    print ("Current key:", t_k)
                    print ("Current iteration:",run)
                    print ("Sample output:",(t_dec[:200] if len(t_dec) > 199 else t_dec))
                curr_fit = t_fit
                curr_k = t_k

        plain = self.cipher.decode(msg,curr_k)
        if 'verbose' in kwargs:
            print ("===== FINAL RESULTS =====")
            print ("Iterations:",self.iterations)
            print ("Key:",curr_k)
            print ("Fitness:",curr_fit)
            print ("Plaintext:",plain)

        return {"key":curr_k,"fit":curr_fit,"plain":plain}

class SimulatedAnnealing(Solver):
    def solve(self,msg,**kwargs):
        op = self.parse_options(**self.options)
        curr_k = self.starter.generate(m=msg, **op['starter'])
        curr_fit = self.fitness.score(self.cipher.decode(msg,curr_k), **op['fitness'])

        temp = self.options['temp']
        step = self.options['step']
        for run in range(self.iterations):
            temp -= step
            t_k = self.mutator.generate(curr_k, **op['mutator'])
            t_dec = self.cipher.decode(msg,t_k)
            t_fit = self.fitness.score(t_dec, **op['fitness'])
            
            if t_fit >= curr_fit:
                if temp <= 0:
                    continue
                gv = random.random()
                if gv > math.e**((curr_fit-t_fit)/temp):
                    continue

            if 'verbose' in kwargs:
                print ("===== UPDATED KEY FOUND =====")
                print ("Current fitness:", t_fit)
                print ("Current key:", t_k)
                print ("Current iteration:",run)
                print ("Sample output:",(t_dec[:200] if len(t_dec) > 199 else t_dec))
            curr_fit = t_fit
            curr_k = t_k

        plain = self.cipher.decode(msg,curr_k)
        if 'verbose' in kwargs:
            print ("===== FINAL RESULTS =====")
            print ("Iterations:",self.iterations)
            print ("Key:",curr_k)
            print ("Fitness:",curr_fit)
            print ("Plaintext:",plain)

        return {"key":curr_k,"fit":curr_fit,"plain":plain}
    
