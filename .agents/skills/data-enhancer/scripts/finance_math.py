#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融量化精算引擎 (Financial Math Engine)
提供房贷利差、黄金溢价、现金流久期、股息缓冲等量化测算函数
"""

import argparse

def calc_mortgage_prepayment(principal: float = 500000.0, rate: float = 0.040, years: int = 30) -> dict:
    """
    测算等额本息房贷提前还款的省息账本
    """
    r = rate / 12.0
    n = years * 12
    # 等额本息月供公式
    monthly_payment = principal * (r * (1 + r)**n) / ((1 + r)**n - 1)
    total_payment = monthly_payment * n
    total_interest = total_payment - principal

    # 与基准银行定存对比 (假定定存 1.8%)
    deposit_rate = 0.018
    annual_deposit_income = principal * deposit_rate
    annual_mortgage_interest = principal * rate
    net_annual_spread = annual_mortgage_interest - annual_deposit_income

    return {
        "principal": principal,
        "rate_pct": round(rate * 100, 2),
        "years": years,
        "monthly_payment_saved": round(monthly_payment, 1),
        "total_interest_saved": round(total_interest, 1),
        "deposit_rate_benchmark_pct": round(deposit_rate * 100, 2),
        "annual_interest_spread": round(net_annual_spread, 1),
        "locked_risk_free_yield_pct": round(rate * 100, 2),
        "summary_label": f"提前还款{int(principal/10000)}万，30年总共省下利息约{round(total_interest/10000, 1)}万元，每月月供减压{round(monthly_payment, 0)}元"
    }

def calc_gold_premium_and_loss(retail_price: float = 740.0, spot_price: float = 630.0, grams: float = 10.0, recycle_fee_pct: float = 2.0) -> dict:
    """
    测算黄金小金豆从买入到回购变现的完整摩擦成本
    """
    total_buy_cost = retail_price * grams
    spot_base_value = spot_price * grams
    craft_premium_total = total_buy_cost - spot_base_value
    craft_premium_pct = ((retail_price - spot_price) / spot_price) * 100.0

    recycle_unit_price = spot_price * (1.0 - recycle_fee_pct / 100.0)
    total_recycled_cash = recycle_unit_price * grams
    immediate_haircut_loss = total_buy_cost - total_recycled_cash
    immediate_loss_pct = (immediate_haircut_loss / total_buy_cost) * 100.0
    breakeven_spot_price = retail_price / (1.0 - recycle_fee_pct / 100.0)

    return {
        "retail_price": retail_price,
        "spot_price": spot_price,
        "grams": grams,
        "total_buy_cost": round(total_buy_cost, 1),
        "craft_premium_pct": round(craft_premium_pct, 1),
        "craft_premium_total": round(craft_premium_total, 1),
        "recycle_unit_price": round(recycle_unit_price, 1),
        "total_recycled_cash": round(total_recycled_cash, 1),
        "immediate_haircut_loss": round(immediate_haircut_loss, 1),
        "immediate_loss_pct": round(immediate_loss_pct, 1),
        "breakeven_spot_price": round(breakeven_spot_price, 1),
        "summary_label": f"买入{int(grams)}克金豆花费{int(total_buy_cost)}元，当日变现到手仅{int(total_recycled_cash)}元，即刻摩擦损耗{round(immediate_loss_pct, 1)}%（金价需涨至{int(breakeven_spot_price)}元才保本）"
    }

def calc_emergency_cash_runway(cash_amount: float = 500000.0, monthly_expense: float = 10000.0, monthly_mortgage: float = 8000.0) -> dict:
    """
    测算家庭在无收入极端情况下的生存生命线 (Runway)
    """
    runway_with_mortgage = cash_amount / (monthly_expense + monthly_mortgage)
    runway_without_mortgage = cash_amount / monthly_expense
    return {
        "cash_amount": cash_amount,
        "monthly_living_expense": monthly_expense,
        "monthly_mortgage": monthly_mortgage,
        "runway_months_with_mortgage": round(runway_with_mortgage, 1),
        "runway_years_with_mortgage": round(runway_with_mortgage / 12.0, 1),
        "runway_months_without_mortgage": round(runway_without_mortgage, 1),
        "summary_label": f"50万现金若留在手里，即使遭遇全家失业，亦可维持正常开销{round(runway_with_mortgage, 1)}个月（近{round(runway_with_mortgage/12, 1)}年）"
    }

def calc_dividend_vs_drawdown(dividend_yield: float = 0.052, stock_price_change: float = -0.15) -> dict:
    """
    测算高股息红利收益与资本利得回撤的抵消模型
    """
    net_total_return_pct = (dividend_yield + stock_price_change) * 100.0
    recovery_years = abs(stock_price_change) / dividend_yield if dividend_yield > 0 else 0
    return {
        "dividend_yield_pct": round(dividend_yield * 100, 2),
        "price_drawdown_pct": round(stock_price_change * 100, 2),
        "net_total_return_pct": round(net_total_return_pct, 2),
        "recovery_years": round(recovery_years, 1),
        "summary_label": f"年化股息{round(dividend_yield*100, 1)}%，若遭遇股价回撤{abs(round(stock_price_change*100, 1))}%，需持有分红{round(recovery_years, 1)}年方能填补本金回撤"
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="金融精算函数命令行测试")
    parser.add_argument("--calc", choices=["mortgage", "gold", "runway", "dividend"], default="mortgage")
    parser.add_argument("--amount", type=float, default=500000.0)
    parser.add_argument("--rate", type=float, default=0.040)
    parser.add_argument("--years", type=int, default=30)
    parser.add_argument("--retail", type=float, default=740.0)
    parser.add_argument("--spot", type=float, default=630.0)
    parser.add_argument("--grams", type=float, default=10.0)
    args = parser.parse_args()

    if args.calc == "mortgage":
        res = calc_mortgage_prepayment(args.amount, args.rate, args.years)
    elif args.calc == "gold":
        res = calc_gold_premium_and_loss(args.retail, args.spot, args.grams)
    elif args.calc == "runway":
        res = calc_emergency_cash_runway(args.amount)
    elif args.calc == "dividend":
        res = calc_dividend_vs_drawdown()
    
    print(f"📊 [{args.calc.upper()} 精算结果]")
    for k, v in res.items():
        print(f"   {k}: {v}")

