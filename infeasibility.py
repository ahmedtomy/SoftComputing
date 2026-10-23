from .interfaces import InfeasibilityHandler


class DefaultInfeasibilityHandler(InfeasibilityHandler):
    """Standard handler that implements penalty, repair, or rejection for constraints."""

    def evaluate(self, solution, problem, config):
        """Evaluate a candidate solution and handle constraint violations according to config."""
        evaluated_solution = solution.copy()

        # Step 1: Check initial feasibility
        is_feasible = problem.is_feasible(evaluated_solution.genes)
        evaluated_solution.feasible = is_feasible

        # Step 2: Attempt repair if the solution is infeasible and strategy is "repair"
        if not evaluated_solution.feasible:
            if config.infeasible_strategy == "repair":
                evaluated_solution.genes = problem.repair(evaluated_solution.genes)
                evaluated_solution.reset()
                evaluated_solution.feasible = problem.is_feasible(evaluated_solution.genes)

        # Step 3: Reject solution if still infeasible under repair or reject strategies
        if not evaluated_solution.feasible:
            if config.infeasible_strategy == "repair" or config.infeasible_strategy == "reject":
                return None

        # Step 4: Calculate raw fitness and violation amount
        evaluated_solution.raw_fitness = problem.evaluate(evaluated_solution.genes)
        evaluated_solution.violation = problem.violation(evaluated_solution.genes)

        if evaluated_solution.violation < 0:
            raise ValueError("Violation must be non-negative")

        # Step 5: Start with raw fitness as the base fitness value
        evaluated_solution.fitness = evaluated_solution.raw_fitness

        # Step 6: Apply penalty for infeasible solutions (under penalty strategy)
        if not evaluated_solution.feasible:
            penalty_amount = config.penalty_weight * evaluated_solution.violation
            if config.mode == "min":
                evaluated_solution.fitness += penalty_amount
            else:
                evaluated_solution.fitness -= penalty_amount

        return evaluated_solution