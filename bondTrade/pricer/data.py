from utils.utils import *
from security.bond import Bond

def get_mkt_price_map():
    df1 = pd.read_csv(ROOT_DIR+"/pricer/usbonddata.csv")

    mkt_price_map = {}

    for r in df1.iterrows():
        envD = datetime.strptime(r[1]["Date"],"%Y-%m-%d").date()
        tgt = {}
        for i in r[1].keys():
            if i == "Date":
                continue
            if not pd.isna(r[1][i]):
                tgt[i] = r[1][i]
        mkt_price_map[envD] = tgt

    return mkt_price_map

def get_bond_map():
    df2 = pd.read_csv(ROOT_DIR+"/pricer/usbondstatic.csv")
    df2
    bond_map = {}
    for r in df2.iterrows():
        bond = Bond(r[1]["Isin"],r[1]["Coupon"], datetime.strptime(r[1]["issueDate"],"%Y-%m-%d").date(),datetime.strptime(r[1]["maturityDate"],"%Y-%m-%d").date())
        bond_map[r[1]["Isin"]] = bond
    return bond_map

mkt_price_map = get_mkt_price_map()
bond_map = get_bond_map()