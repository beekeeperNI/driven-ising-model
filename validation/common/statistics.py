"""Uncertainty units are independent run means, never individual MCS/cycles."""
import numpy as np
from scipy.stats import t


def interval(values, reference=0.0, tolerance=None):
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all():
        raise ValueError('Need at least two finite independent-run summaries.')
    mean = float(x.mean())
    sem = float(x.std(ddof=1) / np.sqrt(len(x)))
    half = float(t.ppf(.975, len(x)-1) * sem)
    delta = mean - float(reference)
    out = dict(mean=mean, sem=sem, half95=half, reference=float(reference),
               difference=delta, low95=delta-half, high95=delta+half,
               run_values=x.tolist())
    if tolerance is not None:
        out['tolerance'] = float(tolerance)
        out['status'] = ('supported_at_tolerance' if abs(delta)+half <= tolerance else
                         'discrepancy' if abs(delta)-half > tolerance else 'inconclusive')
    return out


def welch_difference(x, y, tolerance):
    x, y = np.asarray(x), np.asarray(y)
    a, b = x.var(ddof=1)/len(x), y.var(ddof=1)/len(y)
    sem = float(np.sqrt(a+b))
    df = (a+b)**2/(a*a/(len(x)-1)+b*b/(len(y)-1)) if a+b else min(len(x),len(y))-1
    d = float(x.mean()-y.mean())
    half = float(t.ppf(.975,df)*sem)
    return dict(difference=d, sem=sem, half95=half, low95=d-half, high95=d+half,
                tolerance=tolerance,
                status=('supported_at_tolerance' if abs(d)+half<=tolerance else
                        'discrepancy' if abs(d)-half>tolerance else 'inconclusive'))

