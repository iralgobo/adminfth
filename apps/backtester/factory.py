# backtester/factory.py
from .spot_simple_backtester import SpotSimpleBacktester
from .spot_risk_backtester import SpotRiskBacktester
from .futures_simple_backtester import FuturesSimpleBacktester
from .futures_risk_backtester import FuturesRiskBacktester

def create_backtester(backtest_config):
    backtester_type = get_backtester_type(backtest_config)
    
    if backtester_type == 'spot_simple':
        return SpotSimpleBacktester(backtest_config)
    elif backtester_type == 'spot_risk':
        return SpotRiskBacktester(backtest_config)
    elif backtester_type == 'futures_simple':
        return FuturesSimpleBacktester(backtest_config)
    elif backtester_type == 'futures_risk':
        return FuturesRiskBacktester(backtest_config)
    else:
        raise ValueError(f"Tipo de backtester no válido: {backtester_type}")
    
def get_backtester_type(backtest_config):
    """
    Maneja tanto objetos BacktestConfig como diccionarios
    """
    if isinstance(backtest_config, dict):
        # Si es diccionario, acceder con []
        return backtest_config.get("backtester_type")
    else:
        # Si es objeto, acceder con .
        return backtest_config.backtester_type