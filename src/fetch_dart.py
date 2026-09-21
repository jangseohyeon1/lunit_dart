import os, io, zipfile, argparse, json
from pathlib import Path
import requests, pandas as pd
from dotenv import load_dotenv

BASE="https://opendart.fss.or.kr/api"
load_dotenv()
KEY=os.getenv("DART_API_KEY")
ROOT=Path(__file__).resolve().parents[1]

def get_corp_code():
    r=requests.get(f"{BASE}/corpCode.xml",params={"crtfc_key":KEY},timeout=60)
    r.raise_for_status()
    z=zipfile.ZipFile(io.BytesIO(r.content))
    df=pd.read_xml(z.open("CORPCODE.xml"),dtype={"corp_code":str,"stock_code":str})
    row=df[df.stock_code.astype(str).str.zfill(6)=="328130"]
    if row.empty: raise RuntimeError("Lunit stock code 328130 not found")
    return row.iloc[0].corp_code

def main(years):
    if not KEY or KEY=="YOUR_DART_API_KEY": raise SystemExit("Set DART_API_KEY in .env")
    corp=get_corp_code()
    raw=ROOT/"data/raw"; raw.mkdir(parents=True,exist_ok=True)
    this_year=pd.Timestamp.today().year
    records=[]
    for year in range(this_year-1, this_year-years-1, -1):
        for reprt, label in [("11011","annual")]:
            params={"crtfc_key":KEY,"corp_code":corp,"bsns_year":str(year),"reprt_code":reprt,"fs_div":"CFS"}
            resp=requests.get(f"{BASE}/fnlttSinglAcntAll.json",params=params,timeout=60)
            resp.raise_for_status(); data=resp.json()
            (raw/f"{year}_{label}_CFS.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
            if data.get("status")=="000":
                for x in data.get("list",[]):
                    x["year"]=year; x["fs_div_requested"]="CFS"; records.append(x)
            else:
                params["fs_div"]="OFS"
                resp=requests.get(f"{BASE}/fnlttSinglAcntAll.json",params=params,timeout=60)
                resp.raise_for_status(); data=resp.json()
                (raw/f"{year}_{label}_OFS.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
                if data.get("status")=="000":
                    for x in data.get("list",[]):
                        x["year"]=year; x["fs_div_requested"]="OFS"; records.append(x)
                else: print(f"{year}: DART response {data.get('status')} {data.get('message')}")
    if records:
        out=ROOT/"data/processed"; out.mkdir(parents=True,exist_ok=True)
        pd.DataFrame(records).to_csv(out/"dart_financials_raw.csv",index=False,encoding="utf-8-sig")
        print(f"Saved {len(records)} rows for corp_code={corp}")
    else: print("No statements retrieved. Check API key, years, and DART availability.")

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--years",type=int,default=5)
    main(p.parse_args().years)
