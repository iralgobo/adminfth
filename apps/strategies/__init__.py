STRATEGY_REGISTRY = {}


def register_strategy(strategy_type):
    def decorator(cls):
        STRATEGY_REGISTRY[strategy_type] = cls
        return cls

    return decorator


def get_strategy_class(strategy_type):
    if strategy_type not in STRATEGY_REGISTRY:
        raise ValueError(
            f"Estrategia '{strategy_type}' no encontrada. Estrategias disponibles: {list(STRATEGY_REGISTRY.keys())}"
        )
    return STRATEGY_REGISTRY[strategy_type]


def get_available_strategies():
    return list(STRATEGY_REGISTRY.keys())


# Importar y registrar estrategias automáticamente
try:
    from apps.strategies.ma_crossover import MovingAverageCrossover
    # Las estrategias se registran automáticamente con el decorador
except ImportError as e:
    print(f"Error importing strategies: {e}")
