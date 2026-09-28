# Crop coefficients (Kc) for common Irish crops

Kc scales reference evapotranspiration into crop-specific demand:
`ETc = ET0 * Kc`. Values below are indicative FAO-56 style ranges for
temperate conditions and should be adjusted locally.

## Growth-stage pattern

Every annual crop follows the same shape:

| Stage | Canopy | Typical Kc |
|---|---|---|
| Initial | bare soil to ~10% cover | 0.3 – 0.5 |
| Development | rapid canopy expansion | rising |
| Mid-season | full canopy, peak demand | 1.0 – 1.2 |
| Late season | senescence, harvest | falling to 0.3 – 0.6 |

## Indicative values

**Spring barley.** Mid-season Kc around 1.15, dropping sharply at ripening.
Most sensitive to water stress from stem extension through grain fill.

**Winter wheat.** Low demand through winter, rising steeply from spring
growth; mid-season Kc around 1.15. Grain filling is the critical window.

**Potatoes.** Mid-season Kc around 1.1-1.15. Shallow rooting makes potatoes
among the most irrigation-responsive crops grown in Ireland, and tuber
initiation and bulking are both moisture sensitive. Uneven moisture causes
quality defects as well as yield loss.

**Grass and grass silage.** Managed grassland is treated as a near-continuous
canopy with Kc around 0.85-1.05 over the growing season. Because grass is cut
repeatedly, demand drops after each cut and recovers as regrowth closes the
canopy.

**Field vegetables and soft fruit.** High value per hectare and usually the
only Irish crops with dedicated irrigation. Kc is crop-specific and the
economic threshold for irrigating is much lower, because the cost of stress is
higher.

## A monthly approximation

Where per-field growth stages are unknown, a monthly Kc curve that peaks in
mid-summer is a reasonable approximation for a regional model. It is coarser
than stage-based Kc, and it will misestimate demand for any field whose
planting date differs substantially from the regional norm. That trade-off
should be stated openly rather than hidden.
