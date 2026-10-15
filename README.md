# RAV4 Adventure — Blue Flame CARL, interior revision 0.10

A complete car update guided by the user's three 2019 Adventure cabin photographs and Tennessee **In the Black** plate image. Existing X5M driving physics, sound and collider are preserved. The supplied body/cabin still limits exact factory accuracy and photorealism; no OEM scan or in-game testing is claimed.

## Install the complete package

Back up your existing `content/cars/toyota_rav4_adventure_blueflame_x5m` folder and personal skins/setups. Drag **Toyota_RAV4_Blue_Flame_CARL_Interior_0.10.zip** into Content Manager. **Install all detected entries: the car and its included `rav4_adventure_mid_10` instrument font.** No individual files need replacing. Select the car marked **Interior 0.10** and refresh its cached preview. For manual installation, extract into the Assetto Corsa installation root, retaining both `content/cars/` and `content/fonts/`.

The donor's CSP extended-physics requirement remains build 2744. Begin with offline practice. The original signed ACI entitlement requirement for online throttle is retained; offline is enabled by that script.

## Changes guided by the supplied photographs

- The complete central mirror glass, shell, swivel and mount move 72 mm upward and 180 mm rearward along the steep windshield. Their orientation and native mirror binding are retained. The old windshield sensor/frit block is removed from its former location and a smaller patch follows the upper glass behind the raised mount. A duplicate painted fragment at the old mirror base is also removed from every LOD.
- The steering wheel keeps its 0.9 rim, spindle and fitted hand animation. Dark graphite replaces the bright lower trim; the lower spoke has a real opening, and both switch pods use circular control layouts matching the reference's overall design.
- The black seat bolsters are darker. Orange stripes move to the upper centers of the front/rear backrests, with dark outer seams. Rear center inserts receive the angular technical-fabric pattern visible in the supplied rear-seat image. These are newly drawn textures and source-fitted geometry, without photographed lighting baked onto the seats.
- A narrower, silver-edged touchscreen housing has physical beveled keys and two dials. The map is original illustrative artwork; infotainment interaction and navigation are decorative.
- The center vents have recessed cavities, separate louvers, directional vanes, sliders and a hazard key. Climate dials are larger, with silver edges, knurled grips and circular labeled faces. The dual-zone LCD and airbag indicator are decorative.
- Open orange storage pockets are fitted into the passenger and driver fascia. The front console storage surface is sloped, with a 12V cap and USB/AUX detail. Broad silver rails have black molded backing. The generic forward armrest section is replaced by actual recessed cupholder wells and an orange lip.
- The instrument face follows the reference's three-zone arrangement: central speed/MID, smaller left tachometer and right fuel graphic. Existing native speed/RPM controllers remain; the central speed pointer is a short perimeter marker. Native **speed in mph, gear and clock** items now target a correctly oriented MID parent, using a bundled font atlas/metrics pair. Fuel segments retain their CSP input. Live telemetry, font orientation in AC and actual illumination require an in-game check.
- The rear plate uses the reference's gray rim, black field, Tennessee outline/header and **IN THE BLACK** legend, with **CARL** replacing the sample serial. The condensed CARL lettering uses Bebas Neue under the included OFL license; the exact government typeface was not identified. The plate mesh remains 12 × 6 inches, fitted in the existing recess with its backing and fasteners.
- Changes apply to all four LOD models. Repeated knurl/louver geometry is batched to reduce draw calls. Previous glossy solid Blue Flame paint, blue tailgate garnish, solid roof/no crossbars, no front plate, wheel-emblem attachments, low-reflection cockpit glass, calipers, mirrors, lighting and wipers remain.

## Checks and remaining limits

`VALIDATION_REPORT.json` contains complete KN5 parsing/lossless roundtrips, index/normal/tangent/texture/mip closure, glass queues, source-fitted roof/plate checks and original physics/audio/collider comparisons. Additional checks verify the complete mirror translation, unchanged steering rim and decoded driver IK, native gauge calibration, reference component presence, plate artwork regions at each LOD, and closure of the 95-character native font atlas and metrics. The ZIP is CRC-checked and every member is byte-compared with the final files. The published download is checked against its SHA-256.

**Assetto Corsa is not installed in this Linux environment.** No game load, drive, live telemetry, native font rendering, glove/driver skinning, CSP illumination/glass sorting, rain wiping, sound playback or LOD transition test is claimed. Blender previews approximate materials. Their MID text is manually illustrated from the shipped font atlas and transform; it is not live AC output.

The three cabin references are 500px photographs/renderings and do not supply exact dimensions, hidden geometry or a licensed high-detail factory cabin model. Original dash, seats, doors, body proportions and donor scale remain approximate in places. Blue Flame is an 8W9-inspired estimate, without measured paint calibration. The existing 450-degree steering lock and X5M tune remain unchanged. Dashboard needle scales cover 0–140 mph and 0–8000 RPM; the retained high-powered tune can exceed the speed face's scale.

## Rebuild in the prepared workspace

Python 3, NumPy, SciPy, Pillow and Blender 4.3 are available. `tools/interior_revision_10.py` starts from verified 0.9 ZIP model bytes, not cumulative geometry edits. Plate-lettering source and license are under `source_textures/fonts/`. The prior complete ZIP and unchanged original archive remain under `artifacts/` and `/workspace/scratch/` respectively.

```bash
cd /workspace/Assetto-Corsa-Rav4
python3 tools/interior_revision_10.py
python3 tools/validate_revision_10.py
blender --background --threads 8 --factory-startup --python tools/render_release_10.py
python3 tools/package_revision_10.py
```

Font format/installation conventions were cross-checked against AcTools `FontObjectBitmap` and `FontContentEntry`; no base-game or DLC-specific font is required. Earlier reports and scripts remain in the workspace. Input images informed the work and are not redistributed as texture photographs.
