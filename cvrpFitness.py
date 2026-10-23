"""CVRP distance objective and adapter for the generic GA Problem interface."""

import math

from .Problem import Problem
from .cvrpTools import DEPOT, CorrectOption, Iproblem, OverWeight, decode, repair


def _validate_num_vehicles(num_vehicles):
    """Ensure num_vehicles is an integer of at least 1."""
    if not isinstance(num_vehicles, int):
        raise ValueError("num_vehicles must be a positive integer")
    if num_vehicles < 1:
        raise ValueError("num_vehicles must be a positive integer")


def _validate_capacity(capacity):
    """Ensure capacity is a positive, finite number."""
    if not isinstance(capacity, (int, float)):
        raise ValueError("capacity must be positive and finite")
    if not math.isfinite(capacity):
        raise ValueError("capacity must be positive and finite")
    if capacity <= 0:
        raise ValueError("capacity must be positive and finite")


def _validate_demands(demands):
    """Ensure demands list is non-empty and contains only non-negative, finite numbers."""
    if not demands:
        raise ValueError("demands must be non-negative finite numbers")
    for demand in demands:
        if not isinstance(demand, (int, float)):
            raise ValueError("demands must be non-negative finite numbers")
        if not math.isfinite(demand):
            raise ValueError("demands must be non-negative finite numbers")
        if demand < 0:
            raise ValueError("demands must be non-negative finite numbers")


def _validate_coordinates(coordinates, demands):
    """Ensure one valid (x, y) coordinate pair exists per customer demand."""
    if len(coordinates) != len(demands):
        raise ValueError("one coordinate pair is required per demand (including the depot)")

    for point in coordinates:
        if not isinstance(point, (list, tuple)):
            raise ValueError("coordinates must be finite (x, y) pairs")
        if len(point) != 2:
            raise ValueError("coordinates must be finite (x, y) pairs")

        for value in point:
            if not isinstance(value, (int, float)):
                raise ValueError("coordinates must be finite (x, y) pairs")
            if not math.isfinite(value):
                raise ValueError("coordinates must be finite (x, y) pairs")


def _validate_instance(coordinates, demands, capacity, num_vehicles):
    """Validate all CVRP parameters and ensure fleet capacity can serve all demands."""
    _validate_num_vehicles(num_vehicles)
    _validate_capacity(capacity)
    _validate_demands(demands)
    _validate_coordinates(coordinates, demands)
    Iproblem(demands, capacity, num_vehicles)


def route_distance(route, coordinates):
    """Calculate Euclidean distance of a single vehicle trip from depot and back."""
    stops = [DEPOT]
    for customer in route:
        stops.append(customer)
    stops.append(DEPOT)

    total_trip_distance = 0.0
    for index in range(len(stops) - 1):
        stop_a = stops[index]
        stop_b = stops[index + 1]
        leg_distance = math.dist(coordinates[stop_a], coordinates[stop_b])
        total_trip_distance += leg_distance

    return total_trip_distance


def total_distance(chromosome, coordinates, demands, capacity, num_vehicles):
    """Decode chromosome into routes and calculate total distance across all vehicles."""
    customer_count = len(demands)
    for gene in chromosome:
        if not isinstance(gene, int):
            raise ValueError("genes must be customer indices from 1 to len(demands) - 1")
        if gene < 1 or gene >= customer_count:
            raise ValueError("genes must be customer indices from 1 to len(demands) - 1")

    routes, _ = decode(chromosome, demands, capacity, num_vehicles)

    total_fleet_distance = 0.0
    for route in routes:
        trip_distance = route_distance(route, coordinates)
        total_fleet_distance += trip_distance

    return total_fleet_distance


def _count_permutation_violations(genes, total_locations):
    """Count missing or duplicated customers compared to expected 1 to N-1 sequence."""
    counts = {}
    for gene in genes:
        if gene in counts:
            counts[gene] += 1
        else:
            counts[gene] = 1

    invalid_count = 0

    # Check each required customer from index 1 to total_locations - 1
    for customer_id in range(1, total_locations):
        actual_count = 0
        if customer_id in counts:
            actual_count = counts[customer_id]

        if actual_count < 1:
            invalid_count += 1 - actual_count
        elif actual_count > 1:
            invalid_count += actual_count - 1

    # Check for any gene values outside the valid customer ID range
    for gene in counts:
        if gene < 1 or gene >= total_locations:
            invalid_count += counts[gene]

    return invalid_count


def build_cvrp_problem(coordinates, demands, capacity, num_vehicles):
    """Connect CVRP instance to the standard GA Problem interface."""
    _validate_instance(coordinates, demands, capacity, num_vehicles)

    coordinate_tuples = []
    for point in coordinates:
        coordinate_tuples.append((point[0], point[1]))
    frozen_coordinates = tuple(coordinate_tuples)

    demands_list = []
    for demand in demands:
        demands_list.append(demand)
    frozen_demands = tuple(demands_list)

    total_locations = len(frozen_demands)

    def cvrp_fitness(genes):
        """Compute total travel distance of decoded vehicle routes."""
        return total_distance(
            genes, frozen_coordinates, frozen_demands, capacity, num_vehicles
        )

    def cvrp_feasibility(genes):
        """Return True if chromosome is a valid customer sequence and no vehicle is overloaded."""
        return CorrectOption(genes, frozen_demands, capacity, num_vehicles)

    def cvrp_violation(genes):
        """Return missing/duplicate customer count, or total overweight if permutation is valid."""
        invalid_customers = _count_permutation_violations(genes, total_locations)
        if invalid_customers > 0:
            return invalid_customers
        return OverWeight(genes, frozen_demands, capacity, num_vehicles)

    def cvrp_repair(genes):
        """Repair capacity violations by shifting customers between routes."""
        return repair(genes, frozen_demands, capacity, num_vehicles)

    return Problem(
        fitness_fn=cvrp_fitness,
        feasibility_fn=cvrp_feasibility,
        violation_fn=cvrp_violation,
        repair_fn=cvrp_repair,
    )


def format_cvrp_solution(chromosome, coordinates, demands, capacity, num_vehicles):
    """Format solution routes, loads, total distance, and feasibility as readable text."""
    distance = total_distance(chromosome, coordinates, demands, capacity, num_vehicles)
    routes, loads = decode(chromosome, demands, capacity, num_vehicles)

    lines = []
    for vehicle_index in range(num_vehicles):
        route = routes[vehicle_index]
        load = loads[vehicle_index]
        vehicle_number = vehicle_index + 1

        stops = [str(DEPOT)]
        for customer in route:
            stops.append(str(customer))
        stops.append(str(DEPOT))

        route_string = " -> ".join(stops)
        line = f"Vehicle {vehicle_number}: {route_string} | load {load}/{capacity}"
        lines.append(line)

    lines.append(f"Total distance: {distance:.2f}")
    is_feasible = CorrectOption(chromosome, demands, capacity, num_vehicles)
    lines.append(f"Feasible: {is_feasible}")

    return "\n".join(lines)
