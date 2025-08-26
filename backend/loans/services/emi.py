def monthly_emi(P: float, annual_rate: float, n: int) -> float:
    r = (annual_rate / 12.0) / 100.0
    if n <= 0: return round(P, 2)
    if r == 0: return round(P / n, 2)
    emi = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return round(emi, 2)