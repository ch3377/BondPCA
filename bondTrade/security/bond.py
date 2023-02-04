from utils.utils import *

class Bond:
    '''
    semi-annual bond for US with 1 day settle lag, to be configed for other bonds
    '''

    def __init__(self, isin, coupon, issue, maturity, yield_curve="US_BOND"):
        self._isin = isin
        self._coupon = coupon
        self._issue_date = issue
        self._maturity = maturity
        self._yield_curve = yield_curve
        self._coupon_pay = coupon / 2.0
        self.coupon_schedule()

    def coupon_schedule(self):
        date_list = [self._maturity]

        t_date = self._maturity - relativedelta(months=6)
        while t_date > self._issue_date + timedelta(90):
            date_list.append(modify_no_weekday(t_date))
            t_date = t_date - relativedelta(months=6)
        date_list.sort()
        self._coupon_schedule = date_list

    def get_remaining_dates(self, asOf):
        return [d for d in self._coupon_schedule if d > asOf]

    def depend_curve(self):
        return "yield_curve"
