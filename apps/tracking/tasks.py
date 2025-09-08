# tasks.py en tu app
from celery import shared_task
from django.utils import timezone
from .models import TrackingConfiguration, Candle
from decimal import Decimal
import requests
from django.db.models import Max



@shared_task
def get_candles():
    print(f"🚀 Iniciando get_candles a las {timezone.now()}")
    
    results = []
    for tracking_configuration in TrackingConfiguration.objects.all():
        try:
            print(f"📊 Procesando: {tracking_configuration.par} - {tracking_configuration.timeframe}")

            # Obtener último timestamp de forma más eficiente
            last_timestamp = Candle.objects.filter(
                tracking_configuration=tracking_configuration
            ).aggregate(Max('timestamp'))['timestamp__max'] or 0
            
            print(f"⏰ Último timestamp en DB: {last_timestamp}")

            # Construir URL con parámetros más robustos
            symbol = tracking_configuration.par.replace('/', '').upper()
            url = "https://fapi.bitunix.com/api/v1/futures/market/kline"
            params = {
                'symbol': symbol,
                'interval': tracking_configuration.timeframe,
                'limit': 1000  # Añadir límite para evitar respuestas muy grandes
            }
            
            print(f"🌐 Consultando: {url} con params: {params}")

            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json().get("data", [])
            print(f"📦 Datos recibidos: {len(data)} candles")

            if not data:
                print("⚠️ No se recibieron datos de la API")
                continue

            # Filtrar y procesar datos
            nuevos_candles = process_candles(data, tracking_configuration, last_timestamp)
            
            print(f"🎯 Total nuevos candles para {tracking_configuration.par}: {nuevos_candles}")
            
            results.append({
                "par": tracking_configuration.par,
                "timeframe": tracking_configuration.timeframe,
                "nuevos_candles": nuevos_candles,
            })
            
        except Exception as e:
            print(f"❌ Error procesando {tracking_configuration.par}: {e}")
            import traceback
            traceback.print_exc()

    return {"status": "OK", "results": results}

def process_candles(data, tracking_configuration, last_timestamp):
    """Procesar candles de forma más eficiente"""
    nuevos_candles = 0
    candles_to_create = []
    
    for candle_data in data:
        try:
            candle_time = int(candle_data["time"])
            
            # Saltar candles antiguos
            if candle_time <= last_timestamp:
                continue
            
            candle_datetime = timezone.datetime.fromtimestamp(candle_time / 1000)
            
            # Preparar candle para bulk_create
            candles_to_create.append(Candle(
                tracking_configuration=tracking_configuration,
                timestamp=candle_time,
                open=Decimal(candle_data["open"]),
                high=Decimal(candle_data["high"]),
                low=Decimal(candle_data["low"]),
                close=Decimal(candle_data["close"]),
                quoteVol=Decimal(candle_data.get("quoteVol", 0)),
                baseVol=Decimal(candle_data.get("baseVol", 0)),
                time=candle_datetime,
            ))
            
            nuevos_candles += 1
            
        except (KeyError, ValueError) as e:
            print(f"⚠️ Error procesando candle: {e}, datos: {candle_data}")
            continue
    
    # Crear todos los candles de una vez (más eficiente)
    if candles_to_create:
        Candle.objects.bulk_create(candles_to_create, ignore_conflicts=True)
        print(f"✅ Creados {nuevos_candles} nuevos candles en lote")
    
    return nuevos_candles
