"""Run the full pipeline in order, writing every public/data/*.json output."""
from pipeline import alcohol, bins, correlations, quality, statements


def main() -> None:
    quality.main()
    correlations.main()
    alcohol.main()
    bins.main()
    statements.main()


if __name__ == "__main__":
    main()
