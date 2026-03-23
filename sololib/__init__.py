"""sololib - A simple Python library."""

__version__ = "0.1.0"


def greet(name: str) -> str:
    """Return a greeting message.

    Args:
        name: The name to greet.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"


def main():
    print(greet("World"))


if __name__ == "__main__":
    main()