# RAV4 Adventure — Blue Flame CARL, visual revision 0.8

A complete visual rebuild of the supplied Assetto Corsa mod. The existing BMW X5M tune, suspension, tire physics, audio and collision mesh are preserved. This release contains the whole car, not a collection of replacement files.

## Install

1. Back up your existing `content/cars/toyota_rav4_adventure_blueflame_x5m` folder, including personal skins and setups.
2. Drag **Toyota_RAV4_Blue_Flame_CARL_Complete_0.8.zip** into Content Manager and install/update the detected car. The internal car ID is unchanged. For manual installation, extract the ZIP into the Assetto Corsa installation root; it already contains `content/cars/<car ID>/`.
3. Select **Toyota RAV4 Adventure | Blue Flame CARL (Visual 0.8, X5M Tune)**. Use CSP compatible with the retained donor's extended-physics build requirement `2744`.
4. First check the car in an offline practice session. Refresh the Content Manager preview if it displays the previous version.

## Actual changes

- Removed the source moonroof glazing, seals, opening hardware and both crossbars. A crowned painted roof and continuous interior headliner follow the source roof envelope. Lengthwise factory-style rails and the antenna remain.
- Removed the front plate, exposing the intact continuous bumper. Inspection found no separate bracket requiring removal.
- Added a fitted 305 × 152 mm black rear plate with white **CARL**, thickness, backing, rounded corners and fasteners.
- Reversed the source conversion's mirrored RAV4/Adventure assemblies. RAV4 is on the vehicle's left, Adventure on the right; lettering and UVs face correctly. Correct source Toyota emblems are retained. The chrome Toyota tailgate emblem stays chrome while the central garnish shares the blue body material.
- Repaired the paint's reflection mask: its blue channel previously disabled environment reflections. The solid, nonmetallic 8W9-inspired finish now has complete native diffuse/normal/maps/detail bindings and restrained CSP clearcoat settings.
- Added subtle cladding grain, rubber tread/sidewall materials, corrected tire UV seams and consistent molded sidewall orientation. Visual geometry changes do not alter tire physics or hub positions.
- Restored the detailed source cabin in left-hand-drive form. Refined grain and material assignments, fitted steering controls, selector markings, HVAC fascia/buttons, vents, screen housing, stitching and trim.
- Corrected the steering spindle to the measured rim plane, preserving the parked wheel position and size. The column and stalk are stationary rather than rotating with the wheel. Camera horizontal alignment follows the wheel; its height/depth remain unchanged.
- Repaired glass render-queue flags, front clear/rear privacy tint, inward-facing surfaces, neutral light lenses and all three reflective mirrors.
- Configured native speed/RPM pointers, night illumination, CSP fuel segments, turn arrows, DRLs and fog control. Decorative Entune/HVAC faces are not interactive systems.
- Isolated the original RAV4 wiper arms/blades and configured the official CSP procedural wiper mechanism against the real windshield. The legacy animation targeted absent BMW parts; existing driver animations remain unchanged.
- Moved calipers from spinning wheel nodes to suspension nodes, preserving every parked vertex. Discs and tires remain on the rotating wheel nodes.
- Rebuilt all three lower LODs with connected edge collapse, protected panel seams and preserved UVs/hierarchy. Removed collapsed zero-area faces and corrected inverted winding; rebuilt valid tangent bases.
- Removed unreferenced BMW-only instrument textures and animations, obsolete preview-node names and missing-target visual damage sections. Driving-physics sections, driver animations and flame assets remain.

## Validation and practical limits

`VALIDATION_REPORT.json` records checks performed on the delivered files: complete KN5 parsing/lossless roundtrips, index/material/texture closure, DDS mip chains, normals/tangents, solid-roof coverage, removed crossbars/front plate, plate dimensions, glass queues, light/gauge/mirror references, wheel/caliper hierarchy, LOD surface coverage and donor physics/audio/collider preservation. The ZIP is CRC-tested and its member bytes are compared with the final car files. The published download is checked against the local ZIP's SHA-256.

**Assetto Corsa is not installed in this Linux workspace.** No in-game load, drive, live steering/gauge calibration, CSP switch behavior, rain wiping, sound playback or replay/photo-mode test is claimed. Preview images are offline Blender renders; nighttime previews illustrate a lighting state and do not prove CSP operation.

The supplied source body is 2021-based and remains an approximation of a 2019 Adventure. Its donor scale/wheelbase and coarse source areas are retained to preserve the working physics and wheel alignment; this is not an OEM scan or a full replacement cabin model. The Blue Flame color is an 8W9-inspired estimate, not colorimeter-calibrated paint. Official Toyota reference image requests were blocked in this environment; no unverified AWD badge or speculative factory styling was added. Exact factory-detail accuracy and photorealism are therefore not certified.

The original physics script's signed ACI online entitlement requirement is preserved. Offline operation is enabled by that script; unrestricted online compatibility is not implied. CSP instruments/wipers and driver hand alignment need an in-game check. Entune/climate screens and decorative wheel buttons do not simulate their real electronic functions.

Suggested runtime checks: offline loading/driving and sound; cockpit position and driver hands; full steering; speed/RPM/fuel; headlights low/high, DRLs, fog Extra A, brake/tail/reverse, left/right/hazards; mirrors and glass from both sides; wipers/rain; LOD transitions, replays and photo mode.

## Rebuild in the prepared workspace

Python 3, NumPy, SciPy, Pillow and Blender 4.3 are already available.

```bash
cd /workspace/Assetto-Corsa-Rav4
python3 tools/build_revision_08.py /workspace/scratch/Toyota_RAV4_Blue_Flame_One_Click_Content_Manager.zip
python3 tools/validate_revision_08.py /workspace/scratch/Toyota_RAV4_Blue_Flame_One_Click_Content_Manager.zip content/cars/toyota_rav4_adventure_blueflame_x5m --expected-version 0.8 --report validation-report.json
python3 tools/package_revision_08.py
```

The build begins from the original model bytes. Editable procedural textures are in `source_textures/`; independent geometry/configuration/validation helpers are under `tools/`. The KN5 format and shader behavior were checked against AcTools; CSP configuration syntax uses official acc-extension-config examples. Original package notes are preserved as `SOURCE_RELEASE_NOTES.txt`.
