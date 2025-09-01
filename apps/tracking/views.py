
from django.shortcuts import render, redirect, get_object_or_404
from .models import Candle, TrackingConfiguration
from .forms import TrackingConfigurationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.urls import reverse
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.html import mark_safe


def tracking_configuration_list(request):  
    return render(request, 'tracking/configuration_list.html')

@csrf_exempt
def tracking_configuration_list_ajax(request):
    try:
        if request.method == 'GET':
            # Manejar parámetros con validación
            try:
                start = int(request.GET.get('start', 0))
            except (ValueError, TypeError):
                start = 0
            
            try:
                length = int(request.GET.get('length', 10))
            except (ValueError, TypeError):
                length = 10
                
            try:
                draw = int(request.GET.get('draw', 1))
            except (ValueError, TypeError):
                draw = 1
            
            # Resto del código igual...
            search_value = request.GET.get('search[value]', '')
            queryset = TrackingConfiguration.objects.all()
            
            if search_value:
                queryset = queryset.filter(
                    Q(par__icontains=search_value) |
                    Q(timeframe__icontains=search_value)
                )
            
            total_records = queryset.count()
            tracking_configurations = queryset[start:start + length]
            
            data = []
            for config in tracking_configurations:
                data.append({
                    'par': config.par,
                    'timeframe': config.timeframe,
                    'actions': render_configuration_actions(config)
                })
            
            return JsonResponse({
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': total_records,
                'data': data
            })
    
    except Exception as e:
        return JsonResponse({
            'draw': 1,
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
            'error': str(e)
        }, status=400)
    
def tracking_configuration_detail(request, pk):
    tracking_configuration = TrackingConfiguration.objects.get(pk=pk)
    context = {
        'tracking_configuration': tracking_configuration
    }
    return render(request, 'tracking_configuration_detail.html', context)

def tracking_configuration_create(request):
    if request.method == 'POST':
        form = TrackingConfigurationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracking_configuration_list')
    else:
        form = TrackingConfigurationForm()
    context = {
        'form': form
    }
    return render(request, 'tracking/configuration_form.html', context)

def tracking_configuration_update(request, pk):
    tracking_configuration = TrackingConfiguration.objects.get(pk=pk)
    if request.method == 'POST':
        form = TrackingConfigurationForm(request.POST, instance=tracking_configuration)
        if form.is_valid():
            form.save()
            return redirect('tracking_configuration_list')
                   
    else:
        form = TrackingConfigurationForm(instance=tracking_configuration)
    context = {
        'form': form
    }
    return render(request, 'tracking/configuration_form.html', context)

@require_POST
@csrf_exempt
def tracking_configuration_delete(request):

    try:
        print(request)
        data = json.loads(request.body)
        config_id = data.get('id')
        tracking_configuration = get_object_or_404(TrackingConfiguration, id=config_id)
        
      
        tracking_configuration.delete()
        return JsonResponse({'success': True}) 
       
    except TrackingConfiguration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'TrackingConfiguration does not exist'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
       
   



def candle_list_view(request, tracking_configuration_id):
    configuration = TrackingConfiguration.objects.get(id=tracking_configuration_id)
    return render(request, 'tracking/candle_list.html', {'configuration': configuration})

@csrf_exempt
def candle_list_ajax(request, tracking_configuration_id):
    try:
        if request.method == 'GET':
            # Manejar parámetros con validación
            try:
                start = int(request.GET.get('start', 0))
            except (ValueError, TypeError):
                start = 0
            
            try:
                length = int(request.GET.get('length', 10))
            except (ValueError, TypeError):
                length = 10
                
            try:
                draw = int(request.GET.get('draw', 1))
            except (ValueError, TypeError):
                draw = 1
            
            queryset = Candle.objects.filter(tracking_configuration_id=tracking_configuration_id).order_by('-time')
            
            total_records = queryset.count()
            candles = queryset[start:start + length]
            
            data = []
            for candle in candles:
                data.append({
                    'open': candle.open,
                    'close': candle.close,
                    'high': candle.high,
                    'low': candle.low,
                    'quoteVol': candle.quoteVol,
                    'baseVol': candle.baseVol,
                    'timestamp': candle.timestamp,
                    'time': candle.time  
                })
            
            return JsonResponse({
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': total_records,
                'data': data
            })
    
    except Exception as e:
        return JsonResponse({
            'draw': 1,
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
            'error': str(e)
        }, status=400)



def render_configuration_actions(config):
    """Renderiza las acciones para una configuración usando template partial"""
    context = {
        'config_id': config.pk,
        'config_name': f"{config.par} - {config.timeframe}",
        #'config_active': config.active  # Asumiendo que tienes un campo active
    }
    
    html = render_to_string('tracking/partials/configuration_actions.html', context)
    return mark_safe(html)