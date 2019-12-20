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
from copy import copy

class Solver:
    def __init__(self,cipher,fitness,mutator,starter,iterations,**kwargs):
        self.cipher = cipher
        self.fitness = fitness
        self.mutator = mutator
        self.starter = starter
        self.iterations = iterations
        self.options = kwargs

    def print_verbose(self,stats,title="KEY UPDATE"):
        print ("==========",title,"==========")
        for k in stats:
            print (k+':',str(stats[k]))

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

class BruteForce(Solver):
    def solve(self,msg,**kwargs):
        op = self.parse_options(**self.options)
        curr_k = self.starter.generate(m=msg, **op['starter'])
        t_dec = self.cipher.decode(msg,curr_k)
        curr_fit = self.fitness.score(t_dec, **op['fitness'])

        run = 0
        t_k = curr_k
        while run < self.iterations and t_k is not None:
            t_k = self.mutator.generate(t_k, **op['mutator'])
            if t_k is None:
                break
            t_dec = self.cipher.decode(msg,t_k)
            t_fit = self.fitness.score(t_dec, **op['fitness'])
            if t_fit < curr_fit:
                if 'verbose' in kwargs:
                    self.print_verbose({'Current fitness':t_fit,"Current key": t_k,"Current iteration": run,"Sample output": (t_dec[:200] if len(t_dec) > 199 else t_dec)})
                curr_fit = t_fit
                curr_k = copy(t_k)
            run += 1
        plain = self.cipher.decode(msg,curr_k)
        if 'verbose' in kwargs:
            self.print_verbose({'Iterations':run,'Key':curr_k,'Fitness':curr_fit,'Plaintext':plain}, 'FINAL RESULTS')
        return {"key":curr_k,"fit":curr_fit,"plain":plain}

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
                    self.print_verbose({'Current fitness':t_fit,"Current key": t_k,"Current iteration": run,"Sample output": (t_dec[:200] if len(t_dec) > 199 else t_dec)})
                curr_fit = t_fit
                curr_k = copy(t_k)

        plain = self.cipher.decode(msg,curr_k)
        if 'verbose' in kwargs:
            self.print_verbose({'Iterations':self.iterations,'Key':curr_k,'Fitness':curr_fit,'Plaintext':plain}, 'FINAL RESULTS')

        return {"key":curr_k,"fit":curr_fit,"plain":plain}

class ParticleSwarm(Solver):
    def word_distance(self,s,d,alphabet=Constants.alphabets['en'],comp=13):
        t = 0
        if len(d) < len(s):
            t += comp*(len(s)len(d))
            s = s[:len(d)]
        if len(d) > len(s):
            t += comp*(len(d)-len(s))
        for x in range(len(s)):
            t += alphabet.index(s[x])-alphabet.index(d[x])
            
        return t
    def solve(self,msg,**kwargs):
        op = self.parse_options(**self.options)
        n = self.options['n']
        omega = self.options['omega']
        phi_p = self.options['phi_p']
        phi_g = self.options['phi_g']
        distance_function = self.options['distance_function']
        max_velocity = self.options['max_velocity']

        def fit(k):
            return self.fitness.score(self.cipher.decode(msg,k), **op['fitness'])
        
        particles = []
        best_f = -1
        best_p = ''
        for x in range(n):
            particles.append({'p': self.starter.generate(m=msg, **op['starter']), 'v': random.randint(0,max_velocity)})
            particles[-1]['x'] = copy(particles[-1]['p'])
            c_f = fit(particles[-1]['p'])
            if best_f == -1 or c_f < best_f:
                best_f = c_f
                best_p = copy(particles[-1]['p'])

        for run in range(self.iterations):
            for part in particles:
                r_p = random.random()
                r_g = random.random()

                part['v'] = math.ceil(omega*part['v'] + phi_p*r_p*(distance_function(part['x'],part['p'])) + phi_g*r_g*(distance_function(part['x'],best_p)))
                #print (part['v'])
                curr_update = copy(part['p'])
                for i in range(part['v']):
                    curr_update = self.mutator.generate(curr_update, **op['mutator'])
                part['x'] = copy(curr_update)

                x_fit = fit(part['x'])
                p_fit = fit(part['p'])
                if x_fit < p_fit:
                    part['p'] = copy(part['x'])
                    if x_fit < best_f:
                        best_p = copy(part['p'])
                        best_f = x_fit
                        t_dec = self.cipher.decode(msg,best_p)
                        if 'verbose' in kwargs:
                            self.print_verbose({'Current fitness':best_f,"Current key":best_p,"Lead Particle":particles.index(part),"Current iteration": run,"Sample output": (t_dec[:200] if len(t_dec) > 199 else t_dec)})
        

        plain = self.cipher.decode(msg,best_p)
        if 'verbose' in kwargs:
            self.print_verbose({'Iterations':run,'Key':best_p,'Fitness':best_f,'Plaintext':plain}, 'FINAL RESULTS')

        return {"key":best_p,"fit":best_f,"plain":plain}

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

            if 'verbose' in kwargs and t_fit <= curr_fit:
                self.print_verbose({'Current fitness':t_fit,"Current key": t_k,"Current iteration": run,"Sample output": (t_dec[:200] if len(t_dec) > 199 else t_dec)})
            curr_fit = t_fit
            curr_k = copy(t_k)

        plain = self.cipher.decode(msg,curr_k)
        if 'verbose' in kwargs:
            self.print_verbose({'Iterations':self.iterations,'Key':curr_k,'Fitness':curr_fit,'Plaintext':plain}, 'FINAL RESULTS')

        return {"key":curr_k,"fit":curr_fit,"plain":plain}
    
