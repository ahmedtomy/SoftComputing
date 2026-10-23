"""CVRP distance objective and adapter for the generic GA Problem interface."""

import math
from collections import Counter

from .Problem import Problem
from .cvrpTools import DEPOT, CorrectOption, Iproblem, OverWeight, decode, repair


def _validate_instance(coordinates, demands, capacity, num_vehicles):
    if not isinstance(num_vehicles, int) or num_vehicles < 1:
        raise ValueError("num_vehicles must be a positive integer")
    if not isinstance(capacity, (int, float)) or not math.isfinite(capacity) or capacity <= 0:
        raise ValueError("capacity must be positive and finite")
    if not demands or any(
        not isinstance(d, (int, float)) or not math.isfinite(d) or d < 0 for d in demands
    ):
        raise ValueError("demands must be non-negative finite numbers")
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


def route_distance(route, coordinates):
    """Euclidean depot -> customers -> depot distance; an empty route costs zero."""
    stops = [DEPOT, *route, DEPOT]
    return sum(
        math.dist(coordinates[a], coordinates[b])
        for a, b in zip(stops, stops[1:])
    )


def total_distance(chromosome, coordinates, demands, capacity, num_vehicles):
    """Decode the customer ordering and sum the distances of all vehicle trips."""
    if any(not isinstance(c, int) or c < 1 or c >= len(demands) for c in chromosome):
        raise ValueError("genes must be customer indices from 1 to len(demands) - 1")
    routes, _ = decode(chromosome, demands, capacity, num_vehicles)
    return sum(route_distance(route, coordinates) for route in routes)


def build_cvrp_problem(coordinates, demands, capacity, num_vehicles):
    """Connect CVRP to the GA's Problem interface (use with GAConfig(mode='min'))."""
    _validate_instance(coordinates, demands, capacity, num_vehicles)
    coordinates = tuple(tuple(point) for point in coordinates)
    demands = tuple(demands)
    expected = Counter(range(1, len(demands)))

    def violation(genes):
        # Duplicate/missing customers also need a positive penalty, even at zero demand.
        counts = Counter(genes)
        invalid = sum((expected - counts).values()) + sum((counts - expected).values())
        if invalid:
            return invalid
        return OverWeight(genes, demands, capacity, num_vehicles)

    return Problem(
        fitness_fn=lambda genes: total_distance(
            genes, coordinates, demands, capacity, num_vehicles
        ),
        feasibility_fn=lambda genes: CorrectOption(genes, demands, capacity, num_vehicles),
        violation_fn=violation,
        repair_fn=lambda genes: repair(genes, demands, capacity, num_vehicles),
    )


def format_cvrp_solution(chromosome, coordinates, demands, capacity, num_vehicles):
    """Human-readable routes, loads, feasibility and total distance."""
    distance = total_distance(chromosome, coordinates, demands, capacity, num_vehicles)
    routes, loads = decode(chromosome, demands, capacity, num_vehicles)
    lines = [
        f"Vehicle {i}: " + " -> ".join(map(str, [DEPOT, *route, DEPOT]))
        + f" | load {load}/{capacity}"
        for i, (route, load) in enumerate(zip(routes, loads), start=1)
    ]
    lines.extend(
        [
            f"Total distance: {distance:.2f}",
            f"Feasible: {CorrectOption(chromosome, demands, capacity, num_vehicles)}",
        ]
    )
    return "\n".join(lines)
