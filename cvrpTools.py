import random

DEPOT = 0


def Iproblem(demands, capacity, num_vehicles):
    """Validate CVRP parameters and return a dictionary of problem dimensions."""
    if demands[DEPOT] != 0:
        raise ValueError("The depot (index 0) must have demand 0.")

    max_demand = 0
    total_demand = 0
    for demand in demands:
        if demand > max_demand:
            max_demand = demand
        total_demand += demand

    if max_demand > capacity:
        raise ValueError("A customer's demand exceeds the vehicle capacity.")

    fleet_capacity = capacity * num_vehicles
    if total_demand > fleet_capacity:
        raise ValueError("Total demand exceeds total fleet capacity.")

    demand_list = []
    for demand in demands:
        demand_list.append(demand)

    return {"demands": demand_list, "capacity": capacity, "num_vehicles": num_vehicles}


def getCustomers(demands):
    """Return a list of customer IDs excluding the depot at index 0."""
    customers = []
    for customer_id in range(1, len(demands)):
        customers.append(customer_id)
    return customers


def decode(chromosome, demands, capacity, num_vehicles):
    """Split a customer sequence into vehicle routes respecting vehicle capacity where possible."""
    routes = []
    loads = []
    for _ in range(num_vehicles):
        routes.append([])
        loads.append(0)

    vehicle_index = 0
    for customer in chromosome:
        customer_demand = demands[customer]

        # Move to next vehicle if current vehicle would exceed capacity, unless on the last vehicle
        if loads[vehicle_index] + customer_demand > capacity:
            if vehicle_index < num_vehicles - 1:
                vehicle_index += 1

        routes[vehicle_index].append(customer)
        loads[vehicle_index] += customer_demand

    return routes, loads


def getRouteAndLoads(chromosome, demands, capacity, num_vehicles):
    """Decode chromosome and return only the vehicle loads."""
    routes, loads = decode(chromosome, demands, capacity, num_vehicles)
    return loads


def CheckDups(chromosome, demands):
    """Check whether chromosome contains exactly each customer once with no duplicates or omissions."""
    sorted_chromosome = sorted(chromosome)
    expected_customers = getCustomers(demands)
    return sorted_chromosome == expected_customers


def OverWeight(chromosome, demands, capacity, num_vehicles):
    """Calculate the total capacity violation summed across all vehicles."""
    loads = getRouteAndLoads(chromosome, demands, capacity, num_vehicles)
    total_overweight = 0
    for load in loads:
        if load > capacity:
            excess = load - capacity
            total_overweight += excess
    return total_overweight


def CorrectOption(chromosome, demands, capacity, num_vehicles):
    """Return True if chromosome is a valid permutation and no vehicle is overloaded."""
    if not CheckDups(chromosome, demands):
        return False
    total_overweight = OverWeight(chromosome, demands, capacity, num_vehicles)
    return total_overweight == 0


def penalty(chromosome, demands, capacity, num_vehicles, weight=1000.0):
    """Calculate the penalty cost for duplicate customers or capacity violations."""
    if not CheckDups(chromosome, demands):
        total_demand = 0
        for demand in demands:
            total_demand += demand
        return weight * total_demand

    total_overweight = OverWeight(chromosome, demands, capacity, num_vehicles)
    return weight * total_overweight


def _try_offload_customer(customer, source_route, routes, loads, demands, capacity):
    """Attempt to move one customer from source route to another route with spare capacity."""
    customer_demand = demands[customer]
    for target_route in range(len(routes)):
        if target_route == source_route:
            continue
        if loads[target_route] + customer_demand <= capacity:
            routes[source_route].remove(customer)
            routes[target_route].append(customer)
            loads[source_route] -= customer_demand
            loads[target_route] += customer_demand
            return True
    return False


def Offload(routes, loads, r, demands, capacity):
    """Move a high-demand customer from overloaded route r to another vehicle if space allows."""
    def customer_neg_demand(customer_id):
        return -demands[customer_id]

    sorted_customers = sorted(routes[r], key=customer_neg_demand)
    for customer in sorted_customers:
        was_moved = _try_offload_customer(customer, r, routes, loads, demands, capacity)
        if was_moved:
            return True
    return False


def _try_swap_pair(customer_a, source_route, target_route, routes, loads, demands, capacity):
    """Try to swap customer_a with any customer on target_route to reduce source route load."""
    demand_a = demands[customer_a]
    for customer_b in routes[target_route]:
        difference = demand_a - demands[customer_b]
        if difference > 0:
            if loads[target_route] + difference <= capacity:
                index_a = routes[source_route].index(customer_a)
                index_b = routes[target_route].index(customer_b)
                routes[source_route][index_a] = customer_b
                routes[target_route][index_b] = customer_a
                loads[source_route] -= difference
                loads[target_route] += difference
                return True
    return False


def swap(routes, loads, r, demands, capacity):
    """Swap a customer on overloaded route r with a lighter customer from another route."""
    for customer in routes[r]:
        for target_route in range(len(routes)):
            if target_route == r:
                continue
            was_swapped = _try_swap_pair(
                customer, r, target_route, routes, loads, demands, capacity
            )
            if was_swapped:
                return True
    return False


def repair(chromosome, demands, capacity, num_vehicles, max_iter=200):
    """Heuristically repair an overloaded chromosome via offloading and swapping."""
    if not CheckDups(chromosome, demands):
        raise ValueError("repair() needs a valid permutation of the customers.")

    routes, loads = decode(chromosome, demands, capacity, num_vehicles)

    for _ in range(max_iter):
        overloaded_vehicles = []
        for vehicle_index in range(num_vehicles):
            if loads[vehicle_index] > capacity:
                overloaded_vehicles.append(vehicle_index)

        if len(overloaded_vehicles) == 0:
            break

        route_index = overloaded_vehicles[0]

        # Try offloading a customer first; if that fails, try swapping
        repaired = Offload(routes, loads, route_index, demands, capacity)
        if not repaired:
            repaired = swap(routes, loads, route_index, demands, capacity)

        if not repaired:
            break

    # Flatten routes back into a single chromosome sequence
    repaired_chromosome = []
    for route in routes:
        for customer in route:
            repaired_chromosome.append(customer)

    old_excess = OverWeight(chromosome, demands, capacity, num_vehicles)
    new_excess = OverWeight(repaired_chromosome, demands, capacity, num_vehicles)

    # Only accept the repaired solution if it reduced the total overweight
    if new_excess < old_excess:
        return repaired_chromosome

    fallback_chromosome = []
    for customer in chromosome:
        fallback_chromosome.append(customer)
    return fallback_chromosome
