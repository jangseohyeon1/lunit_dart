from pathlib import Path
import pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/"data/processed/dart_financials_raw.csv"
OUT=ROOT/"data/processed"; REPORT=ROOT/"reports"

# 계정명은 DART 공시별 차이가 있으므로 필요시 별칭을 추가하세요.
ALIASES={
 "revenue":["매출액","수익(매출액)","영업수익"],
 "gross_profit":["매출총이익"],
 "operating_profit":["영업이익","영업이익(손실)"],
 "net_income":["당기순이익(손실)","당기순이익"],
 "assets":["자산총계"],
 "current_assets":["유동자산"],
 "current_liabilities":["유동부채"],
 "liabilities":["부채총계"],
 "equity":["자본총계"],
 "cash":["현금및현금성자산"],
 "receivables":["매출채권","매출채권및기타채권"],
 "inventory":["재고자산"],
 "debt_short":["단기차입금"],
 "debt_long":["장기차입금"],
 "interest":["이자비용"],
 "cfo":["영업활동현금흐름"],
 "capex":["유형자산의 취득","유형자산 취득"],
}

def num(s):
    if pd.isna(s): return np.nan
    s=str(s).replace(",","").strip()
    try: return float(s)
    except: return np.nan

def main():
    if not IN.exists(): raise SystemExit("Run fetch_dart.py first.")
    df=pd.read_csv(IN,dtype=str).fillna("")
    # 연간 당기 금액 우선. 원문 계정명과 fs_div는 원천 파일에 보존.
    df["amount_num"]=df["thstrm_amount"].map(num)
    rows=[]
    for year,g in df.groupby("year"):
        row={"year":int(year)}
        for key,aliases in ALIASES.items():
            hit=g[g["account_nm"].isin(aliases)]
            row[key]=hit.iloc[0]["amount_num"] if not hit.empty else np.nan
        rows.append(row)
    x=pd.DataFrame(rows).sort_values("year")
    x["gross_margin"]=x.gross_profit/x.revenue
    x["operating_margin"]=x.operating_profit/x.revenue
    x["net_margin"]=x.net_income/x.revenue
    x["current_ratio"]=x.current_assets/x.current_liabilities
    x["debt_to_equity"]=x.liabilities/x.equity
    x["equity_ratio"]=x.equity/x.assets
    x["debt_ratio_assets"]=(x.debt_short.fillna(0)+x.debt_long.fillna(0))/x.assets
    x["net_debt"]=(x.debt_short.fillna(0)+x.debt_long.fillna(0))-x.cash
    x["revenue_growth"]=x.revenue.pct_change()
    x["cfo_to_net_income"]=x.cfo/x.net_income
    x.to_csv(OUT/"financial_ratios.csv",index=False,encoding="utf-8-sig")
    REPORT.mkdir(parents=True,exist_ok=True)
    latest=x.iloc[-1]
    lines=["# Lunit 재무 요약","",f"- 기준연도: {int(latest.year)}","",
           "## 최근 연도 주요 지표","",
           "| 지표 | 값 |","|---|---:|"]
    for label,col,fmt in [
      ("매출액","revenue",",.0f"),("영업이익","operating_profit",",.0f"),
      ("당기순이익","net_income",",.0f"),("매출증가율","revenue_growth",".1%"),
      ("영업이익률","operating_margin",".1%"),("순이익률","net_margin",".1%"),
      ("유동비율","current_ratio",".2f"),("부채비율","debt_to_equity",".2f"),
      ("자기자본비율","equity_ratio",".1%"),("순차입금","net_debt",",.0f"),
      ("CFO/순이익","cfo_to_net_income",".2f")]:
        v=latest[col]
        lines.append(f"| {label} | {format(v,fmt) if pd.notna(v) else 'N/A'} |")
    lines += ["","> 금액 단위는 DART 원문(thstrm_amount)의 단위를 따릅니다. 계정과목 자동 매핑과 연결/별도 기준을 검증한 후 해석하세요."]
    (REPORT/"summary.md").write_text("\n".join(lines),encoding="utf-8")
    print("Wrote financial_ratios.csv and reports/summary.md")

if __name__=="__main__": main()
