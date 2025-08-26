def monthly_emi(principal: float, annual_rate: float, months: int) -> float:
    r = (annual_rate / 12.0) / 100.0
    if months <= 0: return round(principal, 2)
    if r == 0: return round(principal / months, 2)
    emi = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return round(emi, 2)

def round_to_nearest_lakh(amount: float) -> int:
    # 1 lakh = 100,000
    lakhs = round(amount / 100000.0)
    return int(lakhs * 100000)