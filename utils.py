def clearterm() -> None:
    print("\x1b[H\x1b[0J\x1b[3J", end="")