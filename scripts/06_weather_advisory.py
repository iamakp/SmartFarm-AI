\
"""
This module intentionally does NOT claim that a simple rule is an ML model.

It gives a transparent advisory from real weather values.
Later, after we build a historical crop+weather joined dataset, this can be
replaced or complemented by a trained risk model.
"""

def irrigation_weather_advice(
    rainfall_forecast_mm,
    temperature_c,
    humidity_percent,
):
    if rainfall_forecast_mm >= 10:
        return "Rain is significant; irrigation may be unnecessary."
    if temperature_c >= 32 and humidity_percent < 50:
        return "Hot and relatively dry conditions; inspect soil moisture before irrigation."
    return "No strong weather-only irrigation signal. Check soil moisture before deciding."


if __name__ == "__main__":
    rain = float(input("Forecast rainfall (mm): "))
    temp = float(input("Temperature (°C): "))
    humidity = float(input("Humidity (%): "))

    print("\nAdvice:")
    print(irrigation_weather_advice(rain, temp, humidity))
