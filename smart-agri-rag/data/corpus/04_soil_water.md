# Soil water: the buffer between rainfall and crop stress

## Field capacity, wilting point, available water

After heavy rain drains for a day or two, the water a soil retains against
gravity is its **field capacity**. The point at which a plant can no longer
extract water is the **permanent wilting point**. The difference is **plant
available water (AWC)**, usually expressed in mm of water per metre of soil
depth.

Indicative AWC by texture:

| Texture | AWC (mm per m depth) |
|---|---|
| Sand | 60 – 100 |
| Sandy loam | 100 – 150 |
| Loam | 150 – 200 |
| Clay loam | 160 – 210 |
| Clay | 150 – 200 (much held too tightly to extract quickly) |

Multiply AWC by effective rooting depth to get the reservoir the crop can
actually draw on. Shallow-rooted crops on sandy soils have a small buffer and
run out fast; deep-rooted crops on loams can ride out a fortnight of dry
weather.

## Why this changes the irrigation decision

Two fields with identical weather can need different decisions on the same day.
A potato crop on a sandy loam with 60 cm of rooting has perhaps 60-90 mm of
usable water. At a demand of 4 mm/day, that is two to three weeks of buffer
from full — but if the profile is already half depleted, it is one week.

This is the main limitation of any weather-only model: it estimates atmospheric
demand well and soil state poorly. A daily water-balance term that tracks
depletion (rain in, ETc out, capped at AWC) is the standard way to close that
gap without hardware, and it is the natural next step for a sensor-free system.

## Drainage class

Poorly drained soils, common in parts of Ireland, can be waterlogged in one
season and still leave a crop short in a dry spell, because roots stay shallow.
Drainage class is therefore a useful static feature alongside AWC.
