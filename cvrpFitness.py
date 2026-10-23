import math
from collections import Counter

from .Problem import Problem
from .cvrpTools import DEPOT, CorrectOption, Iproblem, OverWeight, decode, repair


def _validate_instance(coordinates, demands, capacity, num_vehicles, distance_matrix):
    if not isinstance(num_vehicles, int) or num_vehicles < 1:
        raise ValueError("num_vehicles must be a positive integer")
    if not isinstance(capacity, (int, float)) or not math.isfinite(capacity) or capacity <= 0:
        raise ValueError("capacity must be positive and finite")
    if not demands or any(
        not isinstance(d, (int, float)) or not math.isfinite(d) or d < 0 for d in demands
    ):
        raise ValueError("demands must be non-negative finite numbers")
    if (coordinates is None) == (distance_matrix is None):
        raise ValueError("provide either coordinates or distance_matrix, not both")
    if distance_matrix is not None:
        if len(distance_matrix) != len(demands) or any(
            len(row) != len(demands)
            or any(
                not isinstance(cost, (int, float))
                or not math.isfinite(cost)
                or cost < 0
                for cost in row
            )
            for row in distance_matrix
        ):
            raise ValueError("distance_matrix must be square with non-negative finite costs")
    else:
        if len(coordinates) != len(demands):
            raise ValueError("one coordinate pair is required per demand (including the depot)")
        for point in coordinates:
            if (
                not isinstance(point, (list, tuple))
                or len(point) != 2
                or any(
                    not isinstance(value, (int, float)) or not math.isfinite(value)
                    for value in point
                )
            ):
                raise ValueError("coordinates must be finite (x, y) pairs")
    Iproblem(demands, capacity, num_vehicles)


def route_distance(route, coordinates, *, distance_matrix=None):
    stops = [DEPOT, *route, DEPOT]
    if distance_matrix is not None:
        return sum(distance_matrix[a][b] for a, b in zip(stops, stops[1:]))
    return sum(
        math.dist(coordinates[a], coordinates[b])
        for a, b in zip(stops, stops[1:])
    )


def total_distance(
    chromosome, coordinates, demands, capacity, num_vehicles, *, distance_matrix=None
):
    if any(not isinstance(c, int) or c < 1 or c >= len(demands) for c in chromosome):
        raise ValueError("genes must be customer indices from 1 to len(demands) - 1")
    routes, _ = decode(chromosome, demands, capacity, num_vehicles)
    return sum(
        route_distance(route, coordinates, distance_matrix=distance_matrix)
        for route in routes
    )


def build_cvrp_problem(
    coordinates, demands, capacity, num_vehicles, *, distance_matrix=None
):
    _validate_instance(coordinates, demands, capacity, num_vehicles, distance_matrix)
    if coordinates is not None:
        coordinates = tuple(tuple(point) for point in coordinates)
    if distance_matrix is not None:
        distance_matrix = tuple(tuple(row) for row in distance_matrix)
    demands = tuple(demands)
    expected = Counter(range(1, len(demands)))

    def violation(genes):
        counts = Counter(genes)
        invalid = sum((expected - counts).values()) + sum((counts - expected).values())
        if invalid:
            return invalid
        return OverWeight(genes, demands, capacity, num_vehicles)

    return Problem(
        fitness_fn=lambda genes: total_distance(
            genes, coordinates, demands, capacity, num_vehicles,
            distance_matrix=distance_matrix,
        ),
        feasibility_fn=lambda genes: CorrectOption(genes, demands, capacity, num_vehicles),
        violation_fn=violation,
        repair_fn=lambda genes: repair(genes, demands, capacity, num_vehicles),
    )


def format_cvrp_solution(
    chromosome, coordinates, demands, capacity, num_vehicles, *, distance_matrix=None,
    unit="m",
):
    """Format a decoded solution like the OR-Tools CVRP example."""
    distance = total_distance(
        chromosome, coordinates, demands, capacity, num_vehicles,
        distance_matrix=distance_matrix,
    )
    routes, loads = decode(chromosome, demands, capacity, num_vehicles)
    def display_cost(value):
        return str(value) if isinstance(value, int) else f"{value:.2f}"

    lines = [f"Objective: {display_cost(distance)}"]
    for vehicle, (route, load) in enumerate(zip(routes, loads)):
        if not route:
            continue
        cumulative = 0
        stops = [f"{DEPOT} Load(0)"]
        for customer in route:
            # The published example shows the load on arrival, before pickup.
            stops.append(f"{customer} Load({cumulative})")
            cumulative += demands[customer]
        stops.append(f"{DEPOT} Load({load})")
        cost = route_distance(route, coordinates, distance_matrix=distance_matrix)
        lines.extend([
            f"Route for vehicle {vehicle}:",
            " " + " -> ".join(stops),
            f"Distance of the route: {display_cost(cost)}{unit}",
            f"Load of the route: {load}",
            "",
        ])
    lines.extend([
        f"Total distance of all routes: {display_cost(distance)}{unit}",
        f"Total load of all routes: {sum(loads)}",
    ])
    if not CorrectOption(chromosome, demands, capacity, num_vehicles):
        lines.append("Feasible: False")
    return "\n".join(lines)