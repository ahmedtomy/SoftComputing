import random

from .infeasibility import DefaultInfeasibilityHandler

# Maximum factor multiplied by population_size before giving up on generating valid solutions
MAX_ATTEMPTS_FACTOR = 100


class GeneticAlgorithm:
    """Coordinates the genetic algorithm execution loop across modular components."""

    def __init__(self, config, problem, chromosome, selection, crossover,
                mutation, replacement, infeasibility_handler=None):
        """Initialize the GA engine with configured operators and problem specification."""
        self.config = config
        self.problem = problem
        self.chromosome = chromosome
        self.selection = selection
        self.crossover = crossover
        self.mutation = mutation
        self.replacement = replacement

        if infeasibility_handler is None:
            infeasibility_handler = DefaultInfeasibilityHandler()
        self.infeasibility_handler = infeasibility_handler

        self.best_solution = None
        self.history = {"best_fitness": [], "average_fitness": []}

    def run(self, verbose=False):
        """Execute the textbook genetic algorithm loop from initialization to convergence."""
        if self.config.seed is not None:
            random.seed(self.config.seed)

        self.best_solution = None
        self.history = {"best_fitness": [], "average_fitness": []}

        # Step 1: Create initial population and record initial state
        population = self._create_initial_population()
        self._update_best_solution(population)
        self._record_history(population)

        generations_without_improvement = 0

        # Step 2: Main generational loop
        for generation in range(1, self.config.generations + 1):
            offspring = self._create_offspring(population)
            population = self.replacement.replace(population, offspring, self.config)

            improved = self._update_best_solution(population)
            self._record_history(population)

            if improved:
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1

            if verbose:
                if generation % 10 == 0:
                    print("Generation", generation, "best fitness:", self.best_solution.fitness)

            if self._check_early_stop(generations_without_improvement):
                break

        return self.best_solution, self.history

    def _create_initial_population(self):
        """Generate and evaluate individuals until population_size acceptable solutions are collected."""
        population = []
        attempts = 0
        max_attempts = self.config.population_size * MAX_ATTEMPTS_FACTOR

        while len(population) < self.config.population_size:
            if attempts >= max_attempts:
                raise RuntimeError(
                    "Could not create enough acceptable solutions. "
                    "Use infeasible_strategy='penalty' or 'repair'."
                )
            attempts += 1

            candidate = self.chromosome.create_candidate()
            evaluated = self.infeasibility_handler.evaluate(
                candidate, self.problem, self.config
            )
            if evaluated is not None:
                population.append(evaluated)

        return population

    def _pick_parents(self, population):
        """Select a pair of parent solutions from the population using the selection operator."""
        parents = self.selection.select(population, 2, self.config)
        parent1 = parents[0]
        parent2 = parents[1]
        return parent1, parent2

    def _do_crossover(self, parent1, parent2):
        """Recombine parents if random roll meets crossover_rate; otherwise return copies."""
        roll = random.random()
        if roll < self.config.crossover_rate:
            return self.crossover.crossover(parent1, parent2)
        child1 = parent1.copy()
        child2 = parent2.copy()
        return child1, child2

    def _mutate_and_evaluate(self, child):
        """Apply mutation to a child and evaluate its fitness and constraint status."""
        mutated_child = self.mutation.mutate(child, self.config.mutation_rate)
        evaluated = self.infeasibility_handler.evaluate(
            mutated_child, self.problem, self.config
        )
        return evaluated

    def _create_offspring(self, population):
        """Generate offspring through parent selection, crossover, mutation, and evaluation."""
        offspring = []
        attempts = 0
        max_attempts = self.config.population_size * MAX_ATTEMPTS_FACTOR

        while len(offspring) < self.config.population_size:
            if attempts >= max_attempts:
                break
            attempts += 1

            parent1, parent2 = self._pick_parents(population)
            child1, child2 = self._do_crossover(parent1, parent2)

            for raw_child in (child1, child2):
                evaluated = self._mutate_and_evaluate(raw_child)
                if evaluated is not None:
                    if len(offspring) < self.config.population_size:
                        offspring.append(evaluated)

        # Fallback: fill any missing spots with copies of randomly chosen parents
        while len(offspring) < self.config.population_size:
            donor = random.choice(population)
            offspring.append(donor.copy())

        return offspring

    def _check_early_stop(self, generations_without_improvement):
        """Return True if early stop patience is set and generations without improvement reached it."""
        patience = self.config.early_stop_patience
        if patience is None:
            return False
        return generations_without_improvement >= patience

    def _is_better(self, candidate, current_best):
        """Compare candidate against current best, prioritizing feasibility over fitness."""
        if candidate.feasible != current_best.feasible:
            return candidate.feasible
        return candidate.is_better_than(current_best, self.config.mode)

    def _update_best_solution(self, population):
        """Identify best solution in current population and update global best if improved."""
        best_in_population = population[0]
        for solution in population[1:]:
            if self._is_better(solution, best_in_population):
                best_in_population = solution

        if self.best_solution is None:
            self.best_solution = best_in_population.copy()
            return True

        if self._is_better(best_in_population, self.best_solution):
            self.best_solution = best_in_population.copy()
            return True

        return False

    def _record_history(self, population):
        """Compute average fitness and log best and average fitness into history tracking."""
        total_fitness = 0.0
        for solution in population:
            total_fitness += solution.fitness

        average_fitness = total_fitness / len(population)
        self.history["best_fitness"].append(self.best_solution.fitness)
        self.history["average_fitness"].append(average_fitness)
