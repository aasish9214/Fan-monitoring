"""Safe, bounded fan-speed policies for the demonstration prototype."""

def threshold_controller(temp_c: float, low_c: float = 28.0, high_c: float = 36.0) -> int:
    """Simple baseline: linear fan speed between low/high thresholds."""
    if temp_c <= low_c:
        return 0
    if temp_c >= high_c:
        return 100
    return int(round((temp_c - low_c) / (high_c - low_c) * 100))


def adaptive_controller(predicted_temp_c: float, current_speed_pct: float = 0.0,
                        low_c: float = 28.0, high_c: float = 36.0,
                        max_step_pct: int = 20) -> int:
    """Use predicted next temperature to set fan speed, limiting abrupt changes."""
    target = threshold_controller(predicted_temp_c, low_c, high_c)
    lower = max(0, int(round(current_speed_pct)) - max_step_pct)
    upper = min(100, int(round(current_speed_pct)) + max_step_pct)
    return int(max(lower, min(upper, target)))


def pwm_duty_from_percent(speed_pct: float, resolution: int = 255) -> int:
    """Convert 0..100 percent to PWM duty 0..resolution."""
    if not 0 <= speed_pct <= 100:
        raise ValueError("speed_pct must be between 0 and 100")
    return int(round(speed_pct / 100 * resolution))
