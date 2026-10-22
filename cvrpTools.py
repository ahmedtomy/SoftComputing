import random
DEPOT = 0

def Iproblem(demands, capacity, num_vehicles):
    if demands[DEPOT] != 0:
        raise ValueError("The depot (index 0) must have demand 0.")
    if max(demands) > capacity:
        raise ValueError("A customer's demand exceeds the vehicle capacity.")
    if sum(demands) > capacity * num_vehicles:
        raise ValueError("Total demand exceeds total fleet capacity.")
    return {"demands": list(demands), "capacity": capacity, "num_vehicles": num_vehicles}

def getCustomers(demands):
    return list(range(1, len(demands)))

def decode(chromosome, demands, capacity, num_vehicles):
    
    routes = [[] for _ in range(num_vehicles)]
    loads = [0] * num_vehicles
    v = 0
    for c in chromosome:
        d = demands[c]
        if loads[v] + d > capacity and v < num_vehicles - 1:
            v += 1
        routes[v].append(c)
        loads[v] += d
    return routes, loads

def getRouteAndLoads(chromosome, demands, capacity, num_vehicles):
    return decode(chromosome, demands, capacity, num_vehicles)[1]

def CheckDups(chromosome, demands):
    return sorted(chromosome) == getCustomers(demands)

def OverWeight(chromosome, demands, capacity, num_vehicles):
    loads = getRouteAndLoads(chromosome, demands, capacity, num_vehicles)
    return sum(max(0, load - capacity) for load in loads)

def CorrectOption(chromosome, demands, capacity, num_vehicles):
    if not CheckDups(chromosome, demands):
        return False
    return OverWeight(chromosome, demands, capacity, num_vehicles) == 0

def penalty(chromosome, demands, capacity, num_vehicles, weight=1000.0):
    if not CheckDups(chromosome, demands):
        return weight * sum(demands)  
    return weight * OverWeight(chromosome, demands, capacity, num_vehicles)

def Offload(routes, loads, r, demands, capacity):
    cb=sorted(routes[r], key=lambda c: -demands[c])
    for c in cb:
        for t in range(len(routes)):
            if t != r and loads[t] + demands[c] <= capacity:
                routes[r].remove(c)
                routes[t].append(c)
                loads[r] -= demands[c]
                loads[t] += demands[c]
                return True
    return False  

def swap(routes, loads, r, demands, capacity):
    for c in routes[r]:
        for t in range(len(routes)):
            if t == r:
                continue
            for c2 in routes[t]:
                diff = demands[c] - demands[c2]  
                if diff > 0 and loads[t] + diff <= capacity:
                    i = routes[r].index(c)
                    j = routes[t].index(c2)
                    routes[r][i] = c2
                    routes[t][j] = c
                    loads[r] -= diff
                    loads[t] += diff
                    return True
    return False  

def repair(chromosome, demands, capacity, num_vehicles, max_iter=200):

    if not CheckDups(chromosome, demands):
        raise ValueError("repair() needs a valid permutation of the customers.")

    routes, loads = decode(chromosome, demands, capacity, num_vehicles)

    for i in range(max_iter):
        overloaded = [v for v in range(num_vehicles) if loads[v] > capacity]
        if not overloaded:
            break  
        r = overloaded[0]
        fixed = Offload(routes, loads, r, demands, capacity) or swap(routes, loads, r, demands, capacity)
        if not fixed:
            break  
    nc = [c for route in routes for c in route]

    old_excess = OverWeight(chromosome, demands, capacity, num_vehicles)
    new_excess = OverWeight(nc, demands, capacity, num_vehicles)
    if new_excess < old_excess:
        return nc
    return list(chromosome)