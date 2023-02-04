from curve_fitter.curve_fit_load import curve_load
from pricer.data import *
from pricer.market import Market
from pricer.bond_pricer import BondPricer

cmt_list = ["2Y","3Y","5Y","7Y","10Y","15Y","30Y"] # we fix cmt list here, can be passed as option

def get_cmt_data():
    par_cp_map = {}

    for mDate in mkt_price_map:
        crv = curve_load(mDate, ROOT_DIR+"/curves_data")
        mkt = Market(mDate, {"US_BOND":crv}, mkt_price_map[mDate])
        cmt_dates = [modify_no_weekday(add_tenor(mDate, t)) for t in cmt_list]
        cmt_bonds = [Bond("CMT",5, mDate, mat) for mat in cmt_dates]
        par_cp = [BondPricer(bd,mkt).par_coupon() for bd in cmt_bonds]
        par_cp_map[mDate] = par_cp
        print(mDate, "Done")

    return par_cp_map

