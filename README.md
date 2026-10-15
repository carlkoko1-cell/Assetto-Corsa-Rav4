# RAV4 Adventure — Blue Flame CARL, interior revision 0.11

Complete Content Manager car package with the instrument font included. This update addresses the user's reports of backwards dashboard digits and distorted mirrors, and uses the additional instrument-cluster and climate-control close-ups to refine the cabin. Existing X5M tune, sound, collider and driving physics are preserved.

## Installation

Back up your existing car folder and personal skins/setups. Drag **Toyota_RAV4_Blue_Flame_CARL_Interior_0.11.zip** into Content Manager and **install all detected entries: car and instrument font**. Choose **Interior 0.11** and refresh the cached preview. The car ID remains `toyota_rav4_adventure_blueflame_x5m`. Manual installation: extract into the Assetto Corsa root, preserving both `content/cars/` and `content/fonts/`.

The included font retains its existing `rav4_adventure_mid_10` name for compatibility; its pixels and metrics are unchanged. No individual replacement files are necessary. The donor requires CSP build 2744. Begin in offline practice. Its original signed ACI entitlement requirement for online throttle remains.

## Repairs and reference details

- **Backwards dashboard digits:** removed the extra 180-degree rotation on the native MID parent, following the user's in-game report that 0.10 rendered backwards. Adjusted gear/clock placement and text depth to retain their positions on the driver side. The font atlas is not mirrored. Native speed in mph, gear and clock remain live bindings. The user's term “odometer” refers here to these dashboard digits; this release does not add an accumulated-distance counter. Corrected native rendering still needs confirmation in Assetto Corsa.
- **All three mirrors:** the original glass had highly repeated, non-linear UV coordinates, reaching roughly -106 to +106. Each face now has one continuous planar 0–1 projection with consistent optical normals. The glass silhouettes, source vertices, housings and native mirror bindings are retained, including the previously raised center mirror. CSP aspect multiplier remains 1 without arbitrary FOV changes. Mirror projection and live appearance still require an in-game check; side glass uses a planar optical approximation rather than a measured factory convex profile.
- **Instrument cluster:** original artwork follows the new close-up's open speed/tach arcs, red tach band and separate right-hand fuel/coolant graphics. Native speed/RPM centers, controller ownership and calibration are retained. The six existing CSP-driven fuel segments now sit along the upper fuel arc. Coolant graphics remain decorative.
- **Climate controls:** LCD-style 60/64 temperature artwork, fan bars, airflow icons, AUTO/OFF and SYNC/A-C dial legends, six raised climate buttons and separate seat-heater/airbag artwork follow the supplied close-up. The knobs retain their modeled satin edges and knurled grips. New buttons have native light bindings. The climate display and controls are decorative; the indicated temperatures are artwork, not simulated cabin temperatures.
- **Materials:** reduced console-metal specular strength for a satin finish. Black upholstery, orange shoulder stripes/storage trays, steering-wheel details and fitted hand animation from 0.10 remain. Blue Flame paint, blue tailgate garnish, solid roof, no crossbars/front plate, wheel badge attachments and Tennessee In the Black CARL plate remain.
- All four LODs receive the repairs. Geometry outside the mirror attributes, fuel-segment placement and six new climate keys is preserved.

## Validation and limits

`VALIDATION_REPORT.json` records complete KN5 parsing/roundtrips, index/normal/tangent and DDS mip checks, literal configuration references, native gauge calibration, decoded driver motion and original physics/audio/collider preservation. Additional checks verify every mirror's linear, full-range UVs, unchanged source glass positions, consistent optical normals, MID parent/placement and preservation of unrelated geometry. The complete ZIP is CRC-checked and every member compared with the final files. A downloaded copy of the published ZIP is compared with its SHA-256.

**Assetto Corsa/CSP is unavailable in this Linux environment.** Offline asset checks cannot confirm the final native digit orientation, live mirror projection, driving, CSP lighting/glass or glove clearance. Blender previews show the delivered geometry with approximate materials; native digital fields are deliberately left blank because Blender does not reproduce the AC font renderer. Mirror previews do not demonstrate the game's reflection renderer.

This is a photo-guided improvement to an existing approximate model. The source body/cabin geometry, donor dimensions and low-detail regions limit photorealism. The supplied 500px references do not provide an OEM scan or hidden geometry. No photorealistic or exact factory reproduction is claimed. Infotainment remains a decorative original map. Blue Flame is an 8W9-inspired estimate without measured paint calibration. Bebas Neue visually approximates the plate serial font; its OFL and the dashboard font license are included. Speed/RPM scales remain 0–140 mph/0–8000 RPM; the preserved BMW tune can exceed that speed scale. Existing low-LOD source boundary warnings remain in the report.

## Rebuild in the prepared workspace

Python 3, NumPy, SciPy, Pillow and Blender 4.3 are available. The builder starts from the SHA-256-verified published complete 0.10 archive, avoiding cumulative edits. Input photographs inform original artwork and are not redistributed as textures.

```bash
cd /workspace/Assetto-Corsa-Rav4
python3 tools/interior_revision_11.py
python3 tools/validate_revision_11.py
blender --background --threads 8 --factory-startup --python tools/render_release_11.py -- cockpit cluster climate mirror
python3 tools/package_revision_11.py
```
