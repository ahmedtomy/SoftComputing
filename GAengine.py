import random

from .infeasibility import DefaultInfeasibilityHandler

# How many times we retry before giving up when solutions keep being rejected
MAX_ATTEMPTS_FACTOR = 100


class GeneticAlgorithm:
    """The main GA loop. It only talks to the interfaces, so any chromosome,
    selection, crossover, mutation, replacement and problem can be plugged in."""

    def __init__(self, config, problem, chromosome, selection, crossover,
                 mutation, replacement, infeasibility_handler=None):
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

        self.best_solution = None   # best solution found in ALL generations
        self.history = {"best_fitness": [], "average_fitness": []}

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self, verbose=False):
        if self.config.seed is not None:
            random.seed(self.config.seed)

        self.best_solution = None
        self.history = {"best_fitness": [], "average_fitness": []}

        population = self._create_initial_population()
        self._update_best_solution(population)
        self._record_history(population)

        generations_without_improvement = 0

        for generation in range(1, self.config.generations + 1):
            offspring = self._create_offspring(population)
            population = self.replacement.replace(population, offspring, self.config)

            improved = self._update_best_solution(population)
            self._record_history(population)

            if improved:
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1

            if verbose and generation % 10 == 0:
                print("Generation", generation, "best fitness:", self.best_solution.fitness)

            patience = self.config.early_stop_patience
            if patience is not None and generations_without_improvement >= patience:
                break

        return self.best_solution, self.history

    # ------------------------------------------------------------------
    # Step 1: initial population
    # ------------------------------------------------------------------
    def _create_initial_population(self):
        population = []
        attempts = 0
        max_attempts = self.config.population_size * MAX_ATTEMPTS_FACTOR

        while len(population) < self.config.population_size:
            if attempts >= max_attempts:
                raise RuntimeError(
                    "Could not create enough acceptable solutions. "
                    "Use infeasible_strategy='penalty' or 'repair'.")
            attempts += 1

            candidate = self.chromosome.create_candidate()
            evaluated = self.infeasibility_handler.evaluate(candidate, self.problem, self.config)
            if evaluated is not None:       # None means the solution was rejected
                population.append(evaluated)

        return population

    # ------------------------------------------------------------------
    # Step 2: offspring (selection -> crossover -> mutation -> evaluation)
    # ------------------------------------------------------------------
    def _create_offspring(self, population):
        offspring = []
        attempts = 0
        max_attempts = self.config.population_size * MAX_ATTEMPTS_FACTOR

        while len(offspring) < self.config.population_size and attempts < max_attempts:
            attempts += 1

            parent1, parent2 = self.selection.select(population, 2, self.config)

            if random.random() < self.config.crossover_rate:
                child1, child2 = self.crossover.crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            for child in (child1, child2):
                child = self.mutation.mutate(child, self.config.mutation_rate)
                evaluated = self.infeasibility_handler.evaluate(child, self.problem, self.config)

                if evaluated is not None and len(offspring) < self.config.population_size:
                    offspring.append(evaluated)

        # If too many children were rejected, fill the gap with copies of old solutions
        while len(offspring) < self.config.population_size:
            offspring.append(random.choice(population).copy())

        return offspring

    # ------------------------------------------------------------------
    # Best solution and history
    # ------------------------------------------------------------------
    def _is_better(self, candidate, current_best):
        # a feasible solution always beats an infeasible one
        if candidate.feasible != current_best.feasible:
            return candidate.feasible
        return candidate.is_better_than(current_best, self.config.mode)

    def _update_best_solution(self, population):
        best_in_population = population[0]
        for solution in population[1:]:
            if self._is_better(solution, best_in_population):
                best_in_population = solution

        if self.best_solution is None or self._is_better(best_in_population, self.best_solution):
            self.best_solution = best_in_population.copy()
            return True
        return False

    def _record_history(self, population):
        total = 0
        for solution in population:
            total += solution.fitness
        self.history["best_fitness"].append(self.best_solution.fitness)
        self.history["average_fitness"].append(total / len(population))