# tasks.py en tu app
from celery import shared_task
from datetime import datetime
from django.utils import timezone
from .models import TrackingConfiguration, Candle
import time
from decimal import Decimal
import requests


@shared_task
def mi_tarea_periodica():
    # Aquí va la lógica de tu tarea
    print(f"Tarea ejecutada el: {datetime.now()}")
    # Ejemplo: procesar datos, enviar emails, etc.

    # Retorna algún resultado si es necesario
    return "Tarea completada exitosamente"

@shared_task
def get_candles():
    print(f"🚀 Iniciando get_candles a las {timezone.now()}")
    # Sleep de 5 segundos
    time.sleep(5)

    results = []
    for tracking_configuration in TrackingConfiguration.objects.all():
        try:
            print(
                f"📊 Procesando: {tracking_configuration.par} - {tracking_configuration.timeframe}"
            )

            # Obtener último timestamp
            last_candle = (
                Candle.objects.filter(tracking_configuration=tracking_configuration)
                .order_by("-timestamp")
                .first()
            )

            last_timestamp = last_candle.timestamp if last_candle else 0
            print(f"⏰ Último timestamp en DB: {last_timestamp}")

            # Obtener datos de la API
            url = f"https://fapi.bitunix.com/api/v1/futures/market/kline?symbol={tracking_configuration.par}&interval={tracking_configuration.timeframe}"
            print(f"🌐 Consultando: {url}")

            response = requests.get(url, timeout=15)
            response.raise_for_status()

            data = response.json().get("data", [])
            print(f"📦 Datos recibidos: {len(data)} candles")

            if data:
                print(f"🔍 Primer candle: {data[0]}")

            data.sort(key=lambda x: int(x["time"]))
            nuevos_candles = 0

            for candle_data in data:
                candle_time = int(candle_data["time"])

                if candle_time <= last_timestamp:
                    continue

                candle_datetime = datetime.fromtimestamp(candle_time / 1000)

                # Crear nuevo candle
                candle, created = Candle.objects.get_or_create(
                    tracking_configuration=tracking_configuration,
                    timestamp=candle_time,
                    defaults={
                        "open": Decimal(candle_data["open"]),
                        "high": Decimal(candle_data["high"]),
                        "low": Decimal(candle_data["low"]),
                        "close": Decimal(candle_data["close"]),
                        "quoteVol": Decimal(candle_data.get("quoteVol", 0)),
                        "baseVol": Decimal(candle_data.get("baseVol", 0)),
                        "time": candle_datetime,
                    },
                )

                if created:
                    nuevos_candles += 1
                    print(
                        f"✅ Nuevo candle: {tracking_configuration.par} - {candle_datetime}"
                    )
                else:
                    print(
                        f"⏩ Candle existente: {tracking_configuration.par} - {candle_datetime}"
                    )

            print(
                f"🎯 Total nuevos candles para {tracking_configuration.par}: {nuevos_candles}"
            )
            results.append(
                {
                    "par": tracking_configuration.par,
                    "timeframe": tracking_configuration.timeframe,
                    "nuevos_candles": nuevos_candles,
                }
            )
        except requests.RequestException as e:
            print(f"❌ Error API para {tracking_configuration.par}: {e}")
        except ValueError as e:
            print(f"❌ Error de conversión para {tracking_configuration.par}: {e}")
        except KeyError as e:
            print(
                f"❌ Falta campo {e} en API response para {tracking_configuration.par}"
            )
            print(f"📋 Datos: {candle_data}")
        except Exception as e:
            print(f"❌ Error inesperado para {tracking_configuration.par}: {e}")
            import traceback

            traceback.print_exc()

    return {"status": "OK", "results": results}
