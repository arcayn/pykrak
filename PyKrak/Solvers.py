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
from copy import copy,deepcopy
import Constants

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

class SelectionFunctions:
    def random_selection(G, elitism, **kwargs):
        temp_generation = [k[0] for k in G[:elitism]]
        random.shuffle(G)
        temp_generation += [k[0] for k in G[:(-elitism)]]
        return temp_generation

    def full_elitism(G, elitism, **kwargs):
        temp_generation = [k[0] for k in G[:elitism]]
        temp_generation += [k[0] for k in G[:(-elitism)]]
        return temp_generation

    def tournament(G, elitism, **kwargs):
        temp_generation = [k[0] for k in G[:elitism]]
        
        try:
            k = kwargs['k']
        except:
            k = math.floor(len(G) * 0.2)

        try:
            P = kwargs['P']
        except:
            P = 1

        for j in range(len(G) - elitism):
            s = None
            selected = []
            for x in range(k):
                while s is None or s in selected:
                    s = random.randint(0,len(G)-1)
                selected.append(s)
            selected = sorted(selected)

            tournament_pool = [G[i] for i in selected]
            PM = random.random()

            P_totals = 0
            current_winner = 0
            
            P_totals += P*((1-P)**current_winner)
            while PM >= P_totals:
                #print (P_totals)
                P_totals += P*((1-P)**current_winner)
                current_winner += 1

            temp_generation.append(tournament_pool[current_winner][0])
        #print (temp_generation)
        return temp_generation

    def FPS(G, elitism, **kwargs):
        temp_generation = [k[0] for k in G[:elitism]]

        try:
            weight = kwargs['weight']
        except:
            weight = 1

        try:
            norm_factor = kwargs['norm']
        except:
            norm_factor = 1

        worst_candidate = G[-1][1] + norm_factor
        weighting_factor = worst_candidate*(1-weight)
        weighted_G = [[k[0],worst_candidate + weighting_factor - k[1]] for k in G]
        sum_of_gen = sum([k[1] for k in weighted_G])
        normalised_G = [[k[0],k[1]/sum_of_gen] for k in weighted_G]

        for j in range(len(G) - elitism):
            PM = random.random()
            P_totals = 0
            current_selection = 0
            P_totals += normalised_G[current_selection][1]

            while PM >= P_totals:
                P_totals += normalised_G[current_selection][1]
                current_selection += 1

            temp_generation.append(normalised_G[current_selection][0])

        return temp_generation

    def SUS(G, elitism, **kwargs):
        temp_generation = [k[0] for k in G[:elitism]]

        try:
            weight = kwargs['weight']
        except:
            weight = 1

        try:
            norm_factor = kwargs['norm']
        except:
            norm_factor = 1

        worst_candidate = G[-1][1] + norm_factor
        weighting_factor = worst_candidate*(1-weight)
        weighted_G = [[k[0],worst_candidate + weighting_factor - k[1]] for k in G]
        sum_of_gen = sum([k[1] for k in weighted_G])
        spacing = sum_of_gen/len(G)
        
        pointers = []
        precision = 10000000
        PM = random.randint(0, math.floor(spacing*precision))/precision
        pointers.append(PM)
        for j in range(len(G) - elitism):
            pointers.append(pointers[-1] + spacing)

        for p in pointers:
            P_totals = 0
            current_selection = 0
            P_totals += weighted_G[current_selection][1]

            while p >= P_totals:
                P_totals += weighted_G[current_selection][1]
                current_selection += 1

            temp_generation.append(weighted_G[current_selection][0])

        return temp_generation

class CrossoverFunctions:
    def uniform_crossover(L,k=1,alphabet=Constants.alphabets['en'],**kwargs):
        off1 = ''
        off2 = ''

        selected = []
        s = -1
        for x in range(k):
            while s == -1 or s in selected:
                s = random.randint(1,len(L[0])-1)
            selected.append(s)
        selected = sorted(selected)

        mode = 1
        original = 0
        for p in selected:
            if mode == 1:
                off1 += L[0][original:p]
                off2 += L[1][original:p]
            else:
                off1 += L[1][original:p]
                off2 += L[0][original:p]
            mode = (-1)*mode
        
        return [off1,off2]
    
    def position_based_crossover(L,k=1,alphabet=Constants.alphabets['en'],**kwargs):
        #print ("START:",L)
        crossover1 = []
        crossover2 = []
        used_chars1 = ''
        used_chars2 = ''
        off1 = ''
        off2 = ''

        for x in range(k):
            c1 = random.randint(0, len(L[0])-1)
            while c1 in crossover1:
                c1 = random.randint(0, len(L[0])-1)
            crossover1.append(c1)
            c2 = random.randint(0, len(L[0])-1)
            while c2 in crossover2:
                c2 = random.randint(0, len(L[0])-1)
            crossover2.append(c2)

        crossover1 = [9]
        crossover2 = [25]

        for c in crossover1:
            used_chars1 += L[1][c]
        for c in crossover2:
            used_chars2 += L[0][c]
            
        counter1 = 0
        counter2 = 0
        while counter2 < len(L[0]):
            if counter2 in crossover1:
                off1 += L[1][counter2]
                counter2 += 1
            else:
                if L[0][counter1] not in used_chars1:
                    off1 += L[0][counter1]
                    counter2 += 1
                counter1 += 1
                

        counter1 = 0
        counter2 = 0
        while counter2 < len(L[1]):
            if counter2 in crossover2:
                off2 += L[0][counter2]
                counter2 += 1
            else:
                if L[1][counter1] not in used_chars2:
                    off2 += L[1][counter1]
                    counter2 += 1
                counter1 += 1

        #print (crossover1,crossover2)

        #print ('END  :',[off1,off2])

        return [off1,off2]

class GeneticAlgorithm(Solver):
    def solve(self,msg,**kwargs):
        op = self.parse_options(**self.options)
        op['crossover'] = {}
        op['selector'] = {}

        for k in kwargs:
            if 'crossover_' in k:
                op['crossover'][k.replace('crossover_', '')] = kwargs[k]
            if 'selector_' in k:
                op['selector'][k.replace('selector_', '')] = kwargs[k]
        
        n = self.options['n']
        if n%2 == 1:
            n += 1
        mutation_chance = self.options['mutation_chance']
        elitism = math.floor(self.options['elitism']*n)
        crossover_function = self.options['crossover_function']
        selection_function = self.options['selection_function']

        def fit(k):
            return self.fitness.score(self.cipher.decode(msg,k), **op['fitness'])

        current_generation = []
        for i in range(n):
            current_generation.append(self.starter.generate(m=msg, **op['starter']))

        best_fit = self.fitness.score(msg, **op['fitness'])
        best_candidate = ''
            
        for gen in range(self.iterations):
            generation_scores = sorted([[p,fit(p)] for p in current_generation], key=lambda x: x[1])

            if generation_scores[0][1] < best_fit:
                best_candidate = copy(generation_scores[0][0])
                best_fit = generation_scores[0][1]
                if 'verbose' in kwargs:
                    t_dec =  self.cipher.decode(msg,best_candidate)
                    self.print_verbose({'Current fitness':best_fit,"Current key": best_candidate,"Current generation": gen,"Sample output": (t_dec[:200] if len(t_dec) > 199 else t_dec)})

            #temp_generation = [k[0] for k in generation_scores[:elitism]]
            #random.shuffle(generation_scores)
            #temp_generation += [k[0] for k in generation_scores[:(-elitism)]]

            temp_generation = selection_function(generation_scores, elitism, **op['selector'])

            pairs = [[temp_generation[2*x],temp_generation[1+(2*x)]] for x in range(math.floor(len(temp_generation)/2))]
            next_generation = []

            for p in pairs:
                xd = crossover_function(p, **op['crossover'])
                next_generation += xd

            for x in range(len(next_generation)):
                gd = random.random()
                if gd < mutation_chance:
                    next_generation[x] = self.mutator.generate(next_generation[x], **op['mutator'])
                #print (next_generation[x])

            current_generation = deepcopy(next_generation)

        generation_scores = sorted([[p,fit(p)] for p in current_generation], key=lambda x: x[1])

        if generation_scores[0][1] < best_fit:
            best_candidate = copy(generation_scores[0][0])
            best_fit = generation_scores[0][1]

        plain = self.cipher.decode(msg,best_candidate)
        if 'verbose' in kwargs:
            self.print_verbose({'Generations':self.iterations,'Key':best_candidate,'Fitness':best_fit,'Plaintext':plain}, 'FINAL RESULTS')

        return {"key":best_candidate,"fit":best_fit,"plain":plain}

class DistanceFunctions:
    def word_distance(self,s,d,alphabet=Constants.alphabets['en'],comp=13):
        t = 0
        if len(d) < len(s):
            t += comp*(len(s)-len(d))
            s = s[:len(d)]
        if len(d) > len(s):
            t += comp*(len(d)-len(s))
        for x in range(len(s)):
            t += alphabet.index(s[x])-alphabet.index(d[x])
            
        return t

class ParticleSwarm(Solver):
    def solve(self,msg,**kwargs):
        op = self.parse_options(**self.options)
        op['df'] = {}

        for k in kwargs:
            if 'distance_' in k:
                op['df'][k.replace('distance_', '')] = kwargs[k]

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

                part['v'] = math.ceil(omega*part['v'] + phi_p*r_p*(distance_function(part['x'],part['p'],**op['df'])) + phi_g*r_g*(distance_function(part['x'],best_p,**op['df'])))
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
    
