import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from controller import adaptive_controller, threshold_controller, pwm_duty_from_percent


def test_threshold_controller_bounds():
    assert threshold_controller(20) == 0
    assert threshold_controller(40) == 100
    assert 0 <= threshold_controller(32) <= 100


def test_adaptive_controller_limits_step():
    assert adaptive_controller(45, current_speed_pct=40) == 60
    assert adaptive_controller(20, current_speed_pct=40) == 20


def test_pwm_conversion():
    assert pwm_duty_from_percent(0) == 0
    assert pwm_duty_from_percent(100) == 255


def test_pwm_rejects_invalid():
    try:
        pwm_duty_from_percent(101)
        assert False, "Expected ValueError"
    except ValueError:
        pass
