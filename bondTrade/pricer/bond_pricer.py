from utils.utils import *
from security.bond import Bond
from pricer.market import Market


class BondPricer:

    def __init__(self, bond, mkt):
        self._bond = bond
        self._market = mkt
        self._settle = modify_no_weekday(mkt._envDate + timedelta(1))  # 1 day settle lag
        self._remaining = bond.get_remaining_dates(self._settle)
        self._accrued = self.accrued()

    def pv_from_curve(self, zsp=0, crv="US_BOND", cp=None):
        cp = self._bond._coupon_pay if cp is None else cp
        yield_curve = self._market.get_curve(crv)
        pvSum = 0
        settle_df = yield_curve.get_df(self._settle)
        for d in self._remaining:
            df_zsp = math.exp(-zsp * (d - self._settle).days / 365.0)
            pvSum += yield_curve.get_df(d) / settle_df * df_zsp * cp

        lastD = max(self._remaining)
        pvSum += yield_curve.get_df(lastD) * math.exp(-zsp * (lastD - self._settle).days / 365.0) * 100

        return pvSum

    def clean_from_curve(self, zsp=0, crv="US_BOND"):
        return self.pv_from_curve(zsp, crv) - self._accrued

    def clean_price(self):
        return self._market.get_bond_clean_price(self._bond._isin)

    def dirty_price(self):
        return self.clean_price() + self._accrued

    def accrued(self):
        index = self._bond._coupon_schedule.index(self._remaining[0])
        last_d = self._settle if index == 0 else self._bond._coupon_schedule[index - 1]

        return self._bond._coupon * (
                    (self._remaining[0] - last_d).days / 365.0 - (self._remaining[0] - self._settle).days / 365.0)

    def dv01(self):
        '''
        bond math dv01
        '''
        ytm = self.YTM()
        dvSum = 0
        for d in self._remaining:
            dcf = (d - self._settle).days / 365.0
            dvSum += -dcf * self._bond._coupon_pay * math.pow(1 + ytm / 2.0, -dcf * 2 - 1)

        lastD = max(self._remaining)
        last_dcf = (lastD - self._settle).days / 365.0
        dvSum += -100 * last_dcf * math.pow(1 + ytm / 2.0, -last_dcf * 2 - 1)
        return dvSum

    def theory_price(self, ytm):

        '''
        bond math clean price with yield, not very useful
        '''
        pvSum = 0
        for d in self._remaining:
            dcf = (d - self._settle).days / 365.0
            pvSum += self._bond._coupon_pay * math.pow(1 + ytm / 2.0, -dcf * 2)
        lastD = max(self._remaining)
        last_dcf = (lastD - self._settle).days / 365.0
        pvSum += 100 * math.pow(1 + ytm / 2.0, -last_dcf * 2)

        return pvSum - self._accrued

    def YTM(self, isPar=False):
        '''
        bond math yield
        '''
        clean = 100 if isPar else self.clean_price()
        func = lambda x: self.theory_price(x) - clean
        return fsolve(func, 0)[0]

    def z_spread(self, curve_name):
        clean = self.clean_price()
        func = lambda x: self.clean_from_curve(x, curve_name) - clean
        return fsolve(func, 0)[0]

    def par_coupon(self):
        func = lambda x: self.pv_from_curve(cp=x) - self._accrued - 100
        return fsolve(func, 0)[0] / 50

    def cash(self):
        return self._bond._coupon_pay if self._settle in self._bond._coupon_schedule else 0


