# RAV4 Adventure — Blue Flame CARL, interior revision 0.9

A complete installation package, with a cabin-first revision of the supplied RAV4 conversion. Existing BMW X5M driving physics, audio and collider remain unchanged. This is an Adventure-inspired improvement of the supplied cabin, not a factory scan or a certified exact 2019 reconstruction.

## Install

Back up `content/cars/toyota_rav4_adventure_blueflame_x5m` and personal skins/setups. Drag **Toyota_RAV4_Blue_Flame_CARL_Interior_0.9.zip** into Content Manager and update the detected car. Select the entry marked **Interior 0.9** and refresh its cached preview. The ZIP already contains the full `content/cars/<car ID>/` path; for manual installation extract into the Assetto Corsa installation root. The retained donor requires CSP extended-physics build 2744. Begin with offline practice.

## New in 0.9

- Cockpit glass has separate inward-facing, low-reflection materials. Exterior glazing keeps its highlights; cheap CSP refraction is disabled. Inner alpha and Fresnel values no longer reproduce the outside reflection strength over the driver's view. Transparent queues, opposite-facing normals and backface culling are retained.
- Replaced the coarse steering wheel with a roughly 380 mm circular leather rim, shaped thumb areas, a molded three-spoke center, satin lower inlays, shallow fitted controls, dark rim stitching, a physical Toyota emblem and an SRS marking. The parked hub, spindle tilt, column and stalk locations remain aligned.
- Added black perforated SoftTex-inspired seat inserts and fine orange stitching fitted to the source seat backs, cushions and headrests. The existing black bolsters, headrests and seat shapes remain; orange passenger-shelf and console-surround accents complement them.
- Replaced the almost static donor steering animation with native KSANIM v2 keyframes fitted to the new rim. Fixed-length arm IK keeps the source bone dimensions and finger curl. Hands alternate regrips at large steering angles. Animation lock matches the unchanged 450-degree driving control. The neutral KNH pose matches the animation center.
- Removed the unsuitable automatic-transmission BMW shift-arm blend, so gear changes keep the driver on the wheel. The original shift animation files remain included.
- Speed and RPM each have one native AC controller, targeting conventional `ARROW_SPEED` and `ARROW_RPM` transform names. Removed duplicate CSP pointer controllers. Direction, local-Z pivots and 270-degree scales were checked at five inputs per gauge (0–140 mph, 0–8000 RPM). Preview gauge states are manually posed offline, not live telemetry evidence.
- Found and repaired the source wheel-emblem attachment: those chrome symbols were part of the stationary body. All four are now centered at their own hubs and attached to their rotating/steering wheel nodes; rear badge height also follows its actual hub.
- The update applies to all four LOD files. It retains the complete 0.8 solid roof, lengthwise rails, no crossbars, no front plate, black CARL rear plate, corrected body badges, glossy solid Blue Flame paint, matching tailgate garnish, lighting, mirrors, wipers and stationary calipers.

## Verification and limits

`VALIDATION_REPORT.json` contains model parsing/lossless roundtrip, texture/mip closure, index/normal/tangent/queue and hierarchy checks, physical-data/audio/collider comparisons, source-fitted roof/plate checks, gauge calibration checks, and motion checks decoded from the delivered KSANIM/KNH. The driver check verifies bone offsets/scales, normalized quaternions, neutral-pose agreement, grip-radius errors and intermediate-key contact. The complete ZIP is CRC-checked, compared byte-for-byte with the final car files and downloaded again from the public URL to verify SHA-256.

**Assetto Corsa is not installed in this Linux environment.** Actual cockpit-glass rendering, live gauge telemetry, steering direction/driver skinning/glove clearance, shuffle transitions, light switches, rain wiping, sound and LOD transitions require in-game verification. Offline Blender renders approximate the materials; the driver-alignment image shows the delivered skeleton only, not a tested glove mesh. No game load/drive test is claimed.

The supplied 2021-based body/cabin and donor proportions remain approximations. Color is an 8W9-inspired estimate, not measured Toyota paint. Seat perforation, stitching and trim are procedural interpretations. Exact Adventure factory-detail accuracy is not certified. Decorative infotainment/climate faces are not simulated electronic systems. The original signed ACI entitlement requirement for online throttle is preserved; offline is enabled by that donor script.

## Rebuild in this prepared workspace

Python 3, NumPy, SciPy, Pillow and Blender 4.3 are installed. The 0.9 build reads the byte-preserved 0.8 model/config/rig baseline saved under `/workspace/scratch/interior09/baseline`; that baseline is recoverable from the 0.8 complete ZIP in `artifacts/`. It never executes input mod scripts.

```bash
cd /workspace/Assetto-Corsa-Rav4
python3 tools/interior_revision_09.py
python3 tools/validate_revision_09.py
blender --background --threads 8 --factory-startup --python tools/render_release_09.py
python3 tools/package_revision_09.py
```

Source textures remain editable under `source_textures/`. Earlier build tools and reports remain in the workspace. The original package notes are retained as `SOURCE_RELEASE_NOTES.txt`.
