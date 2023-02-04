import utils.utils
from curves.curves import BaseCurve, SpreadCurve, ShiftCurve

def serialize_curve(name, curve):
    as_of = curve._envDate

    def parse_data(crv):
        crv_type = crv.curve_type()
        if crv_type == "base":
            return [{"pillar": crv._pillar, "value": crv._value, "method": crv._method}]
        elif crv_type == "spread":
            return parse_data(crv._curve1) + parse_data(crv._curve2)
        else:
            raise "not supported type"

    return {"Name": name, "AsOf": as_of, "Data": parse_data(curve)}


def load_curve(curve_data):
    asOf = curve_data["AsOf"]
    dList = curve_data["Data"]
    crv = BaseCurve(asOf, dList[0]["pillar"], dList[0]["value"], dList[0]["method"])
    for i in range(1, len(dList)):
        spCrv = BaseCurve(asOf, dList[i]["pillar"], dList[i]["value"], dList[i]["method"])
        crv = SpreadCurve(asOf, crv, spCrv)

    return crv


