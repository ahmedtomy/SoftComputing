def _validate_population_size(size):
    """Ensure population_size is an integer of at least 2."""
    if not isinstance(size, int):
        raise ValueError("population_size must be an integer of at least 2")
    if size < 2:
        raise ValueError("population_size must be an integer of at least 2")


def _validate_generations(generations):
    """Ensure generations is a non-negative integer."""
    if not isinstance(generations, int):
        raise ValueError("generations must be a non-negative integer")
    if generations < 0:
        raise ValueError("generations must be a non-negative integer")


def _validate_mode(mode):
    """Ensure mode is either 'min' or 'max'."""
    if mode != "min" and mode != "max":
        raise ValueError("mode must be 'min' or 'max'")


def _validate_infeasible_strategy(strategy):
    """Ensure infeasible_strategy is penalty, repair, or reject."""
    allowed = ("penalty", "repair", "reject")
    if strategy not in allowed:
        raise ValueError("infeasible_strategy must be penalty/repair/reject")


def _validate_rates(crossover_rate, mutation_rate):
    """Ensure crossover and mutation probabilities are within [0, 1]."""
    if crossover_rate < 0 or crossover_rate > 1:
        raise ValueError("rates must be between 0 and 1")
    if mutation_rate < 0 or mutation_rate > 1:
        raise ValueError("rates must be between 0 and 1")


def _validate_elitism_count(elitism_count, population_size):
    """Ensure elitism_count is an integer between 0 and population_size - 1."""
    if not isinstance(elitism_count, int):
        raise ValueError("elitism_count must be between 0 and population_size - 1")
    if elitism_count < 0:
        raise ValueError("elitism_count must be between 0 and population_size - 1")
    if elitism_count >= population_size:
        raise ValueError("elitism_count must be between 0 and population_size - 1")


def _validate_tournament_size(tournament_size):
    """Ensure tournament_size is an integer of at least 1."""
    if not isinstance(tournament_size, int):
        raise ValueError("tournament_size must be a positive integer")
    if tournament_size < 1:
        raise ValueError("tournament_size must be a positive integer")


def _validate_penalty_weight(penalty_weight):
    """Ensure penalty_weight is non-negative."""
    if penalty_weight < 0:
        raise ValueError("penalty_weight must be non-negative")


def _validate_early_stop_patience(early_stop_patience):
    """Ensure early_stop_patience is either None or a non-negative integer."""
    if early_stop_patience is not None:
        if not isinstance(early_stop_patience, int):
            raise ValueError("early_stop_patience must be a non-negative integer or None")
        if early_stop_patience < 0:
            raise ValueError("early_stop_patience must be a non-negative integer or None")


class GAConfig:
    """Stores and validates all genetic algorithm hyperparameters and settings."""

    def __init__(self,
                 population_size=100,
                 generations=200,
                 crossover_rate=0.8,
                 mutation_rate=0.05,
                 elitism_count=2,
                 tournament_size=3,
                 mode="min",
                 infeasible_strategy="penalty",
                 penalty_weight=1000.0,
                 early_stop_patience=50,
                 seed=None):
        """Validate all parameters and initialize the GA configuration object."""
        _validate_population_size(population_size)
        _validate_generations(generations)
        _validate_mode(mode)
        _validate_infeasible_strategy(infeasible_strategy)
        _validate_rates(crossover_rate, mutation_rate)
        _validate_elitism_count(elitism_count, population_size)
        _validate_tournament_size(tournament_size)
        _validate_penalty_weight(penalty_weight)
        _validate_early_stop_patience(early_stop_patience)

        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.tournament_size = tournament_size
        self.mode = mode
        self.infeasible_strategy = infeasible_strategy
        self.penalty_weight = penalty_weight
        self.early_stop_patience = early_stop_patience
        self.seed = seed
