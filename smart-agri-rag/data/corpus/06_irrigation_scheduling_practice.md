# Irrigation scheduling in practice

## Reading a recommendation

A daily recommendation combines three numbers:

- **ETc** — how much water the crop wants today
- **Pe** — how much of today's rain it will actually get
- **NIR** — the shortfall, `max(0, ETc - Pe)`

A NIR of 0.4 mm is noise: no grower turns on an irrigator for less than half a
millimetre. A NIR of 4 mm sustained over several days is a real deficit. This
is why a threshold matters more than the raw prediction — the model output is
continuous, but the decision is binary.

## Choosing a threshold

A threshold set too low produces constant "irrigate" advice that gets ignored.
Set too high, it misses the short dry spells that matter. Two sensible ways to
choose one:

1. **Operationally:** the smallest application depth the equipment can apply
   efficiently, typically several mm.
2. **Statistically:** pick the threshold that maximises F1 on the irrigate
   decision in the validation years, then check it is operationally sane.

Report precision and recall separately, because their costs differ. A false
"irrigate" wastes water and money. A false "skip" costs yield.

## Timing within the day

Where irrigation is used, early morning and evening applications lose less to
direct evaporation than midday. Wind also matters for sprinkler uniformity.

## Forecast rain beats measured rain

A model trained on observations tells you about yesterday and today. The
decision is about tomorrow. Where a rainfall forecast is available, it should
override a marginal irrigate recommendation: if 8 mm is expected overnight,
skipping a 3 mm deficit is nearly always correct.

## What a grower actually wants to see

Not a number alone. A usable recommendation states the action, the size of the
deficit, and the reason:

> **Skip.** Crop demand is 3.4 mm, but 6 mm of effective rainfall fell in the
> last two days and the soil profile is near capacity.

The explanation is what builds trust in the first season. Without it, the
advice is a black box telling someone to spend money.
