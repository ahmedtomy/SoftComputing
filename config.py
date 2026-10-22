class GAConfig:
    def __init__(self,
                 population_size=100,
                 generations=200,
                 crossover_rate=0.8,
                 mutation_rate=0.05,
                 elitism_count=2,
                 tournament_size=3,
                 mode="min",                    
                 infeasible_strategy="penalty", # "penalty", "repair" or "reject"
                 penalty_weight=1000.0,
                 early_stop_patience=50,
                 seed=None):

        if not isinstance(population_size, int) or population_size < 2:
            raise ValueError("population_size must be an integer of at least 2")
        if not isinstance(generations, int) or generations < 0:
            raise ValueError("generations must be a non-negative integer")
        if mode not in ("min", "max"):
            raise ValueError("mode must be 'min' or 'max'")
        if infeasible_strategy not in ("penalty", "repair", "reject"):
            raise ValueError("infeasible_strategy must be penalty/repair/reject")
        if not (0 <= crossover_rate <= 1 and 0 <= mutation_rate <= 1):
            raise ValueError("rates must be between 0 and 1")
        if not isinstance(elitism_count, int) or not 0 <= elitism_count < population_size:
            raise ValueError("elitism_count must be between 0 and population_size - 1")
        if not isinstance(tournament_size, int) or tournament_size < 1:
            raise ValueError("tournament_size must be a positive integer")
        if penalty_weight < 0:
            raise ValueError("penalty_weight must be non-negative")
        if early_stop_patience is not None and (
            not isinstance(early_stop_patience, int) or early_stop_patience < 0
        ):
            raise ValueError("early_stop_patience must be a non-negative integer or None")

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
