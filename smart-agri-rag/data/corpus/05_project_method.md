# How this project models irrigation need

This document describes the method behind the accompanying forecasting model
(`smart-irrigation-ireland`). It is the ground truth the assistant should cite
when asked how the system works.

## Question the system answers

> "Given everything known today, how much irrigation will this county's crop
> need tomorrow — and is that enough to be worth turning the water on?"

## Pipeline

1. **Weather input.** Daily observations (mean temperature, rainfall, relative
   humidity, and where available wind and radiation) for Irish counties across
   2010-2024, sourced from Met Éireann.
2. **Agronomy layer.** Extraterrestrial radiation from latitude and day of
   year; ET0 by Hargreaves-Samani; ETc by monthly crop coefficient; effective
   rainfall by a fixed-fraction heuristic; then
   `NIR = max(0, ETc - Pe)` as the label.
3. **Feature engineering.** Everything a grower would know on the morning of
   day t: today's weather, today's derived ET0/ETc/Pe/NIR, lags at 1, 2, 3 and
   7 days, rolling sums and means over 3, 7, 14 and 30 days, days since
   measurable rain, and cyclical day-of-year terms.
4. **Target.** NIR on day **t+1**. Tomorrow's weather is not used, and is not
   knowable — that is what makes the task a forecast rather than an
   identity.
5. **Models.** Ridge regression as a linear reference, Random Forest, and
   gradient boosting, all trained on the same features and split.
6. **Evaluation.** A strictly chronological split — train on the earliest
   years, tune on the middle years, test once on the most recent years — with
   MAE, RMSE and R2, plus precision, recall and F1 on the irrigate/skip
   decision at a chosen millimetre threshold.

## Baselines, and why they matter

Every model is compared with two naive predictors:

- **Persistence:** tomorrow's requirement equals today's.
- **Climatology:** the day-of-year county average from the training years.

A model that cannot beat both is not worth deploying, however good its R2 looks
in isolation.

## A correction worth recording

An earlier version of this work predicted NIR for the *same* day while ETc and
Pe were included as input features. Since NIR is defined as `max(0, ETc - Pe)`,
the model was being given the answer and scored R2 = 1.000. That is target
leakage, not accuracy. Restating the task as a t+1 forecast removed it. The
honest numbers are lower and mean something.

## Known limitations

- Soil state is approximated by a constant available-water term rather than a
  running water balance.
- Monthly Kc is a regional approximation, not a field-level growth stage.
- Effective rainfall uses a fixed fraction rather than an intensity-aware
  method.
- The labels are agronomic estimates, not measured irrigation applications, so
  the system is validated against a model of reality, not against reality.
