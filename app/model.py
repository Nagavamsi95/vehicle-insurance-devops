def estimate_premium(vehicle_age: int, driver_age: int, vehicle_value: float) -> float:
    base = vehicle_value * 0.03
    if driver_age < 25:
        base *= 1.4
    if vehicle_age > 10:
        base *= 0.9
    return base