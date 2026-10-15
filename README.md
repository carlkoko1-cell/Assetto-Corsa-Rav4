# RAV4 Adventure Blue Flame CARL — Interior 0.13

Complete Content Manager install, retaining the working 0.12 supplied-model cabin, BMW X5M tune/audio/collider, driver animation, CARL Tennessee plate and Blue Flame paint.

## Download and install

[Download the complete 0.13 ZIP](https://raw.githubusercontent.com/carlkoko1-cell/Assetto-Corsa-Rav4/rav4-interior-v0.13-download/Toyota_RAV4_Blue_Flame_CARL_Interior_0.13.zip)

[View the offline preview board](https://raw.githubusercontent.com/carlkoko1-cell/Assetto-Corsa-Rav4/rav4-interior-v0.13-download/RAV4_Adventure_Interior_0.13_Previews.jpg)

Back up personal skins/setups. Drag the complete ZIP into Content Manager and install **all** detected entries: the car and `rav4_adventure_mid_10` instrument font. Manual installation: extract into the Assetto Corsa root, preserving `content/cars/` and `content/fonts/`. Select Interior 0.13 and refresh cached previews. CSP build 2744 remains required by the original car.

## Changes

- Original vector cluster art follows the supplied Adventure photo: central 140 MPH semicircle/grey number band, left outer tachometer crescent, right fuel/temperature crescents and white pointers. Native speed/RPM controllers are calibrated to these new arcs. The known-working MID identity basis, font and negative text depth remain; speed, gear and clock stay live. Economy and ODO fields are explicitly placeholders, not fabricated readings. Temperature is decorative; fuel retains its existing six live segments.
- A closed opaque enclosure extends behind and below the instrument opening to block the road showing through. All four door cards gain opaque backing/edge returns contained within the exterior body.
- Rearview mirror: rounded factory-style case, normalized reflective UVs, windshield-aligned mount/stem, raised center and plane aimed from the actual driver eye toward the rear window. The donor center-front headliner lip is fitted upward to clear the mirror. Side-mirror reflective geometry and corrected UVs are unchanged.
- Climate LCD moved from its floating plane into the actual supplied-model recess, with matching pitch. The physical knobs and molded key legends remain. Its temperature/fan artwork is decorative.
- BMW screen: the actual supplied ASW X5M extension configuration uses CSP `Navigator_AndroidAuto`. The same renderer/theme/brightness is bound to `RAV4_ENTUNE_SCREEN`, with resolution and offsets fitted to the RAV4's 0–1 UVs. This enables CSP track navigation; it is not proprietary BMW iDrive or a transplanted multimedia OS. No separate BMW physics/Lua was imported. The static map remains the non-CSP fallback.
- Mirror upper caps now use the exact existing body paint material; lower housings stay black. Mirror indicators have dedicated smoked lenses/dark reflectors and retain independent amber turn-signal emission.
- Four black grille modules with six blue LEDs each follow the personal-car photo. Toggle steady illumination using **CSP Extra B**; assign that control in Content Manager. Existing Extra A fog controls remain. No flashing pattern is added.
- Glass retains native alpha blending with read-only depth and no PBR glass replacement. Silver trim/rims gain reflective shaders instead of diffuse-only shading. These address the reported night appearance; final AC/CSP lighting behavior still needs an in-game check.
- All four LODs receive these changes. Tangents are stored to five decimal places (component error under 0.000006) to keep the complete archive within GitHub's file limit; model positions, normals and UVs are unaffected by this storage step.

## Verification and limits

`VALIDATION_REPORT.json` checks final binary roundtrips, indices/winding, normal/tangent bases, full mip chains, material/mesh references, original physics/audio/collider preservation, unchanged steering animation and font closure. Additional checks cover nine calibrated pointer samples per dial, 63 driver-eye rays through the instrument enclosure, both ends of all four closed door volumes, 18 overhead and 15 full-cabin mirror-clearance sightlines, the rearview reflection direction and all 24 grille emitters. Source-side caps/lenses are separated only to change materials; retained cabin/exterior geometry is compared against the verified 0.12 archive. Packaging checks CRC, unique paths and every member against the delivered files; the published archive is downloaded and checked by SHA-256.

Assetto Corsa is unavailable in this Linux environment. Live navigation, native digits, mirror rendering, night transparency/lighting, driver glove clearance and LOD appearance remain untested in-game. Blender previews use approximate materials and deliberately leave native digital fields blank; they do not verify AC rendering. The mirror view hides the windshield only for inspection.

The cabin remains a user-supplied 2023 Hybrid model adapted toward the 2019 Adventure. The new art follows the reference layout within that model's hood; it is not a pixel-exact OEM scan or guaranteed photorealistic reconstruction. Blue Flame is an 8W9-inspired color estimate. The original high-power tune can exceed the 140 MPH face. Existing exterior LOD boundary warnings and original online ACI entitlement behavior remain.

## Rebuild in the prepared workspace

Python 3, NumPy, SciPy, Pillow and Blender 4.3 are installed. The checksum-verified 0.12 baseline, safely extracted donor model and supplied BMW config are staged under `/workspace/scratch`. No uploaded code is executed.

```bash
cd /workspace/Assetto-Corsa-Rav4
python3 tools/finish_revision_13.py
python3 tools/validate_revision_13.py
blender -b -t 8 -P tools/render_release_13.py -- cockpit console cluster climate mirror front
python3 tools/package_revision_13.py
```

Font licenses and source notes are included. Historical build reports remain in the workspace but are excluded from this install archive.
