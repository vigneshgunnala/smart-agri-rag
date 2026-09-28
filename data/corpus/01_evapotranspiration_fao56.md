# Reference evapotranspiration (ET0) and crop water use

**Source:** FAO Irrigation and Drainage Paper 56 (Allen et al., 1998) — "Crop
evapotranspiration: guidelines for computing crop water requirements".

## What ET0 means

Reference evapotranspiration (ET0) is the evaporation and transpiration that
would occur from a hypothetical reference surface: a uniform grass crop, 0.12 m
tall, with a fixed surface resistance of 70 s/m and albedo of 0.23, never short
of water. It expresses the evaporative demand of the atmosphere alone, and is
independent of the crop actually growing in the field. Units are mm/day.

## Calculating ET0

The FAO-56 standard method is the Penman-Monteith equation, which needs net
radiation, air temperature, humidity and wind speed. When the full set of
measurements is not available, FAO-56 recommends the Hargreaves-Samani
equation as a temperature-based alternative:

    ET0 = 0.0023 * Ra * (Tmean + 17.8) * sqrt(Tmax - Tmin)

where Ra is extraterrestrial radiation in mm/day (converted from MJ/m2/day by
dividing by 2.45), and temperatures are in degrees Celsius. Ra depends only on
latitude and day of year, so it can be computed for any location without
instruments.

Hargreaves-Samani tends to overestimate ET0 in humid, windy coastal climates
and underestimate it in arid ones. For Ireland, which is humid and maritime,
estimates should be treated as approximate and calibrated where possible
against Penman-Monteith values from synoptic stations.

## From ET0 to crop water use (ETc)

Actual crop water demand is obtained by scaling ET0 with a crop coefficient:

    ETc = ET0 * Kc

Kc varies by crop and by growth stage. FAO-56 defines four stages: initial,
crop development, mid-season and late season. Kc is lowest at the initial stage
(bare or sparse canopy, typically 0.3-0.5), peaks at mid-season when the canopy
is full, and declines during senescence.

## Effective rainfall (Pe)

Not all rainfall reaches the root zone. Some runs off, some is intercepted by
the canopy and evaporates, some drains below the roots. Effective rainfall is
the portion actually available to the crop. Simple field heuristics assume
60-80% of measured rainfall is effective for moderate daily totals, with the
fraction falling as intensity rises. More detailed methods (USDA-SCS) account
for soil water holding capacity and antecedent moisture.

## Net irrigation requirement (NIR)

The water that must be supplied by irrigation is the shortfall between crop
demand and effective rainfall:

    NIR = max(0, ETc - Pe)

NIR is zero on days when rainfall meets or exceeds crop demand. In a temperate
maritime climate such as Ireland's, NIR is zero on most days of the year, and
the interesting question is which days it is not.
