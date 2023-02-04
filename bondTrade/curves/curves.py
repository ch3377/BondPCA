from utils.utils import *


class Curve:
    '''
    Base class of theory curve
    '''
    def __init__(self, asOf):
        self._interplator = None
        self._envDate = asOf

    def get_df(self, tgt_date):
        return math.exp(-self._interpolator(self.get_dcf(tgt_date)))

    def get_dfs(self, date_l):
        dcfL = [self.get_dcf(d) for d in date_l]
        return [math.exp(-x) for x in self._interpolator(dcfL)]

    def get_dcf(self, tgt_date):
        if tgt_date < self._envDate:
            raise "date cannot be before curve anchor date " + self._envDate.strftime("%Y%m%d")

        # Act/365 for curves
        return (tgt_date - self._envDate).days / 365.0

    def curve_type(self):
        raise "not implemented"


class BaseCurve(Curve):
    '''
        Typical curve
    '''
    def __init__(self, asOf, pillar, value, interp):
        super().__init__(asOf)

        input_x = [self.get_dcf(d) for d in [asOf] + pillar]
        input_y = [0] + value

        max_index = pillar.index(max(pillar)) + 1
        max_r = input_y[max_index] / input_x[max_index]
        input_x.append(100)
        input_y.append(100 * max_r)

        self._pillar = pillar
        self._value = value
        self._method = interp

        if interp == "Cubic":
            self._interpolator = CubicSpline(input_x, input_y, bc_type="natural")
        else:
            self._interpolator = interp1d(input_x, input_y, fill_value='extrapolate')

    def curve_type(self):
        return "base"


class SpreadCurve(Curve):
    '''
        For Risk Calc only in this project, but might be useful for swap/bond multi curves fittings, save/load supported
    '''

    def __init__(self, asOf, curve1, curve2):
        super().__init__(asOf)
        self._curve1 = curve1
        self._curve2 = curve2

    def get_df(self, tgt_date):
        return self._curve1.get_df(tgt_date) * self._curve2.get_df(tgt_date)

    def get_dfs(self, date_l):
        df1 = self._curve1.get_dfs(date_l)
        df2 = self._curve2.get_dfs(date_l)

        return [d1 * d2 for d1, d2 in zip(df1, df2)]

    def curve_type(self):
        return "spread"


class ShiftCurve(Curve):
    '''
        For Carry Roll only, no need to save/load
    '''

    def __init__(self, asOf, curve):
        super().__init__(asOf)
        self._shift = (asOf - curve._envDate).days
        self._base = curve

    def get_df(self, tgt_date):
        return self._base.get_df(tgt_date - timedelta(self._shift))

    def get_dfs(self, date_l):
        date_ll = [d - timedelta(self._shift) for d in date_l]
        return self._base.get_dfs(date_ll)

    def curve_type(self):
        return "shift"