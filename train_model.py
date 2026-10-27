from generate_data import generate
from model import train_model

if __name__ == "__main__":
    generate()
    metrics = train_model()
    print("Chronological hold-out evaluation (synthetic dataset):")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")
