# backtester/factory.py
from .spot_simple_backtester import SpotSimpleBacktester
from .spot_risk_backtester import SpotRiskBacktester
from .futures_simple_backtester import FuturesSimpleBacktester
from .futures_risk_backtester import FuturesRiskBacktester

def create_backtester(backtest_config):
    backtester_type = backtest_config.backtester_type
    
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