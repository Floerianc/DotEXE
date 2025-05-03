def rangespace(
    start: float, 
    stop: float, 
    steps: int = 32
) -> list:
    step_size = (stop - start) / steps
    return [start + (step_size * iteration) for iteration in range(steps)]