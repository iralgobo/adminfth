from django.shortcuts import render

from apps.strategies.models import Strategy
from apps.strategies import get_strategy_class
from django.http import JsonResponse

# Create your views here.


def get_strategy_schema(request, strategy_id):  # Ahora recibe strategy_id como parámetro
    strategy_instance = Strategy.objects.filter(id=strategy_id).first()
    
    if not strategy_instance:
        return JsonResponse({'error': 'Strategy not found'}, status=404)
    
    strategy_class = get_strategy_class(strategy_instance.strategy_type)
    strategy = strategy_class()
    
    return JsonResponse(strategy.get_parameters_schema())