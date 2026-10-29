"""Review-count-weighted blend with a Bayesian prior.

The same numbers are stated in plain language on /about/.
A 10-point score is divided by 2 before it enters the blend.
The original score is what the page shows.
"""

from decimal import Decimal, ROUND_HALF_UP

PRIOR_MEAN = 4.0
PRIOR_REVIEWS = 100


def five_point(rating, scale=5):
    scale = scale or 5
    if scale == 5:
        return float(rating)
    if scale == 10:
        return float(rating) / 2.0
    raise ValueError("unsupported scale: %s" % scale)


def blend(ratings):
    """Return the blended score, or None when there is nothing to blend."""
    usable = []
    for row in ratings:
        if row.get("review_count") is None or row.get("rating") is None:
            continue
        usable.append(row)
    if not usable:
        return None
    numerator = PRIOR_REVIEWS * PRIOR_MEAN
    denominator = PRIOR_REVIEWS
    for row in usable:
        count = int(row["review_count"])
        score = five_point(row["rating"], row.get("scale", 5))
        numerator += count * score
        denominator += count
    return numerator / denominator


def blend_display(ratings):
    value = blend(ratings)
    if value is None:
        return None
    quantized = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(quantized, "f")
