from pricer.bond_pricer import *
from curves.curves import BaseCurve,SpreadCurve,ShiftCurve

class RiskCaclulator:
    def __init__(self, base_mkt, risk_pillar):
        self._base_mkt = base_mkt
        self._risk_pillar = risk_pillar
        self._risk_remapper = None

    def get_scen_mkt(self, zcBump=None, horizon=None):
        mkt = self._base_mkt
        asOf = mkt._envDate
        crvs = mkt._curves_map

        # hard coded in this project
        bd_crv = crvs["US_BOND"]

        if not zcBump is None:
            pillars, values = zcBump
            spd = BaseCurve(asOf, pillars, values, "Linear")
            bd_crv = SpreadCurve(asOf, bd_crv, spd)

        if not horizon is None:
            asOf = modify_no_weekday(add_tenor(asOf, horizon))
            bd_crv = ShiftCurve(asOf, bd_crv)

        return Market(asOf, {"US_BOND": bd_crv}, {})

    def risk_remapper(self):

        if not self._risk_remapper is None:
            return self._risk_remapper

        cmt_list = self._risk_pillar

        asOf = self._base_mkt._envDate

        cmt_dates = [modify_no_weekday(add_tenor(asOf, t)) for t in cmt_list]
        cmt_bonds = [Bond("CMT", 5, asOf, mat) for mat in cmt_dates]

        map1 = []
        lenth = len(cmt_dates)
        for i in range(lenth):
            v1, v2 = [0 for _ in range(lenth)], [0 for _ in range(lenth)]

            dcf = (cmt_dates[i] - asOf).days / 365.0
            v1[i] = 0.0001 * dcf
            v2[i] = -0.0001 * dcf

            mkt1 = self.get_scen_mkt((cmt_dates, v1))
            mkt2 = self.get_scen_mkt((cmt_dates, v2))

            par_cp1 = [BondPricer(bd, mkt1).par_coupon() for bd in cmt_bonds]
            par_cp2 = [BondPricer(bd, mkt2).par_coupon() for bd in cmt_bonds]

            map1.append([(i - j) / 0.0002 for i, j in zip(par_cp1, par_cp2)])
        self._risk_remapper = inv(np.matrix(map1))
        return self._risk_remapper

    def bond_risk_bucket(self, bond):

        asOf = self._base_mkt._envDate
        mkt = self._base_mkt
        cmt_list = self._risk_pillar
        cmt_dates = [modify_no_weekday(add_tenor(asOf, t)) for t in cmt_list]

        remapper = self.risk_remapper()

        scen = []
        base_pricer = BondPricer(bond, mkt)
        base_pv = base_pricer.dirty_price()
        base_zsp = base_pricer.z_spread("US_BOND")

        lenth = len(cmt_dates)
        for i in range(lenth):
            v1, v2 = [0 for _ in range(lenth)], [0 for _ in range(lenth)]
            dcf = (cmt_dates[i] - asOf).days / 365.0
            v1[i] = 0.0001 * dcf
            v2[i] = -0.0001 * dcf

            mkt1 = self.get_scen_mkt((cmt_dates, v1))
            mkt2 = self.get_scen_mkt((cmt_dates, v2))

            up = BondPricer(bond, mkt1).pv_from_curve(zsp=base_zsp)
            down = BondPricer(bond, mkt2).pv_from_curve(zsp=base_zsp)
            scen.append((up - down) / 2)

        return (base_pv, np.matrix([scen]) * remapper)

    def carry_roll(self, bond, horizon):
        # asOf = self._base_mkt._envDate
        mkt = self._base_mkt

        base_pricer = BondPricer(bond, mkt)
        base_pv = base_pricer.dirty_price()
        base_zsp = base_pricer.z_spread("US_BOND")

        hz_mkt = self.get_scen_mkt(None, horizon)

        return BondPricer(bond, hz_mkt).pv_from_curve(zsp=base_zsp) - base_pv + self.cash_horizon(bond, horizon)

    def cash_horizon(self, bond, horizon):

        asOf = self._base_mkt._envDate
        as_settle = modify_no_weekday(asOf + timedelta(1))
        hz_date = modify_no_weekday(add_tenor(asOf, horizon))
        hz_settle = modify_no_weekday(hz_date + timedelta(1))

        remaining = bond.get_remaining_dates(as_settle)
        valid = [d for d in remaining if d <= hz_settle]

        return len(valid) * bond._coupon_pay

    def summarize_with_facotrs(self, bond, horizon, factors={"F1": [], "F2": []}):
        mkt = self._base_mkt
        pv, bucket = self.bond_risk_bucket(bond)
        base_pricer = BondPricer(bond, mkt)
        clean = base_pricer.clean_price()
        cash = base_pricer.cash()
        zspread = base_pricer.z_spread("US_BOND")
        maturity = bond._maturity
        carry_roll = self.carry_roll(bond, horizon)
        dv01 = bucket.sum()
        risk_f1 = (bucket * np.matrix([factors["F1"]]).T)[0, 0]
        risk_f2 = (bucket * np.matrix([factors["F2"]]).T)[0, 0]

        return {"Present Value": pv, "Clean Price": clean, "z-spread": zspread, "Cash Today": cash,"DV01": dv01,
                "Carry Roll Face Value": carry_roll, "C+R/PV": carry_roll / pv, "Risk F1": risk_f1, "Risk F2": risk_f2,
                "C+R/DV01":carry_roll / dv01,"C+R/RF1": carry_roll / risk_f1,
                "C+R/RF2": carry_roll / risk_f2, "Maturity": maturity}
