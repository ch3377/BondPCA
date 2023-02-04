from curves.curve_serialization import *
from pricer.data import *
from pricer.market import Market
from pricer.bond_pricer import BondPricer
import pickle

def curve_fit(mDate, path):

    pillar = ["3M","6M","1Y","2Y","3Y","5Y","7Y","10Y","15Y","30Y"]
    pillar_dates = [modify_no_weekday(add_tenor(mDate, t)) for t in pillar]
    def solver_func(values):
    #     values = [0.13 for _ in range(9)]



        crv = BaseCurve(mDate, pillar_dates,values,"Cubic")

        mkt = Market(mDate, {"US_BOND":crv}, mkt_price_map[mDate])

        diffSum = 0
        for isin in mkt._market_prices:
            bond = bond_map[isin]
            total = (bond._maturity - bond._issue_date).days
            remain = (bond._maturity - mDate).days
            if remain<10:
                continue
            w = (remain/total)**2
            pricer = BondPricer(bond, mkt)

            diffSum += w*(pricer.clean_from_curve() - pricer.clean_price())**2
        return diffSum

    func = lambda x: solver_func([_ for _ in x])
    res = minimize(func, [0.001 for _ in range(10)], method='Powell', tol=1e-3)
    if res.success:
        vs= list(res.x)
        crv = BaseCurve(mDate, pillar_dates,vs,"Cubic")
        to_save = serialize_curve("US_BOND",crv)
        neg = min(to_save["Data"][0]['value'])
        if neg<0:
            print(to_save["Data"][0]['value'])
        dStr = mDate.strftime("%Y%m%d")
        pickle.dump(to_save, open(path+"/"+dStr+".p", "wb" ) )
        print(mDate, "fitted")
    else:
        print(mDate, "failed")


def curve_load(mDate, path):
    return load_curve(pickle.load( open(path+"/"+mDate.strftime("%Y%m%d")+".p", "rb" ) ))

def curve_plot(mDate, crv):
    mkt = Market(mDate, {"US_BOND": crv}, mkt_price_map[mDate])
    yl = []
    xl = []
    for isin in mkt._market_prices:
        bond = bond_map[isin]

        remain = (bond._maturity - mDate).days
        if remain < 1:
            continue
        xl.append(bond._maturity)
        pricer = BondPricer(bond, mkt)
        yl.append(pricer.YTM())

    pDates = [mDate + relativedelta(months=3)] + [mDate + relativedelta(months=6 * i) for i in range(1, 72)]
    bdL = [Bond("1", 5, mDate, mat) for mat in pDates]
    par_cp = [BondPricer(bd, mkt).par_coupon() for bd in bdL]

    plt.plot(pDates, par_cp, label="Bond Par Coupon Curve", color="orange")
    plt.scatter(xl, yl, label="Bond Yields", color="g", alpha=0.2)
    plt.ylabel("Par Coupon From Curve/Yields")
    plt.legend()

    plt.show()

if __name__ == "__main__":

# example of load fitted curves and plot
    mDate = date(2019,6,6)
    curve = curve_load(mDate, ROOT_DIR+"/curves_data")
    curve_plot(mDate, curve)


# Run if need to test curve fitting
# Curves are fitted and saved already

# save_path = ""
# for mDate in mkt_price_map:
#     curve_fit(mDate, save_path)