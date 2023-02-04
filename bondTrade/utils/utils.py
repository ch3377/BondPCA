'''
import all pckgs and date helper functions
'''
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from datetime import date, datetime, timedelta
import math
import pandas as pd
from dateutil.relativedelta import relativedelta
from scipy.optimize import fsolve, minimize
from numpy.linalg import inv
from sklearn.decomposition import PCA
import os

def add_tenor(envD, tenor):
    if tenor[-1] == "M":
        return envD + relativedelta(months = int(tenor[:-1]))
    elif tenor[-1] == "Y":
        return envD + relativedelta(years = int(tenor[:-1]))
    elif tenor[-1] == "D":
        return envD + timedelta(int(tenor[:-1]))

def modify_no_weekday(envDate):
    w = envDate.weekday()
    if w == 5:
        return envDate +timedelta(2)
    elif w == 6:
        return envDate + timedelta(1)
    else:
        return envDate


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

