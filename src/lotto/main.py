"""Entry point for the lotto project."""

from lotto import __version__


def greet(name: str = "world") -> str:
    return f"Hello, {name}! (lotto v{__version__})"


def main() -> None:
    print(greet())


if __name__ == "__main__":
    main()
