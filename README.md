# RAV4 Adventure Blue Flame CARL — Interior 0.15

Corrections for the white Android Auto screen in tunnels, mirror aim/duplicate housing, frozen left RPM needle, and editable Blue Flame paint. Retains the 0.14 door/window fixes, headlight-switched grille LEDs, matte wheel pockets, Adventure black/orange cabin, CARL plate, BMW tune/audio/collider and driver animation.

## Download and install

[Download complete 0.15 ZIP](https://raw.githubusercontent.com/carlkoko1-cell/Assetto-Corsa-Rav4/rav4-interior-v0.15-download/Toyota_RAV4_Blue_Flame_CARL_Interior_0.15.zip)

[Offline inspection previews](https://raw.githubusercontent.com/carlkoko1-cell/Assetto-Corsa-Rav4/rav4-interior-v0.15-download/RAV4_Adventure_Interior_0.15_Previews.jpg)

Exit Assetto Corsa before updating. Back up personal skins/setups, drag the complete ZIP into Content Manager, and install **all** detected entries: the car and `rav4_adventure_mid_10` font. Select Interior 0.15 and start a fresh session. Manual install: extract into the Assetto Corsa root, preserving `content/cars/` and `content/fonts/`.

Use current CSP, at least the existing required build 2744, with its shared Android Auto assets. Real Mirrors must be enabled for independent mirror views. Reset any saved mirror adjustments for this car before judging the new default aim; personal adjustments can override defaults. The blue grille lights use the normal headlights. Extra A still controls fogs.

## Changes

- **Screen:** retains CSP's full interactive Android Auto interface and reverse-camera configuration. Removes the digital-monitor shader and screen glass/SSR classification. The screen now uses an opaque material with zero diffuse, ambient and specular contribution. A visual script controls a neutral, texture-modulated backlight: 0.65 with headlights off, smoothly dimming to 0.10 with headlights on. The software's black pixels do not receive an added reflective/diffuse white layer. This targets the reported tunnel whiteout; the actual Pure/CSP output needs in-game confirmation.
- **RPM:** removes the nonresponding declarative CSP RPM indicator. A separate visual script reads the associated car's `car.rpm` and directly rotates the uniquely named `RAV4_RPM_LIVE` pivot around its local Z axis. Its 0–8000 RPM range maps to the existing 183-degree scale, with a short 45 ms response. The documented CSP `[SCRIPT_0]` visual loader supplies a callback every simulation frame, independently of display visibility or Android Auto. It does not overwrite the pointer texture. References refresh every second for LOD changes. The pivot translation and needle geometry stay unchanged. The native speed/gear/clock bindings and physics script stay byte-identical to 0.14. Live CSP script loading remains untested here.
- **Mirrors:** removes the disconnected donor sensor/mirror pod hidden inside the dashboard's plastic mesh, which was hanging below the new rearview mirror. Keeps the existing compact case, stem and windshield mount. Adjusts the reflective glass planes to reflect rearward horizon rays from the configured driver-eye position; the center case moves with its glass. Existing mirror UVs remain unchanged. Smart Mirror defaults use zero additional rotation and 10-degree FOV in CSP's left/center/right ordering, allowing normal user adjustment.
- **Blue Flame / Paint Shop:** updates the solid base color to a brighter, saturated blue approximation of Toyota 8W9, sRGB `#0095DA` before DDS compression, with neutral glossy clearcoat and no metallic flakes. The body, mirror caps and tailgate accent share `RAV4_BlueFlame.dds` in every LOD. Adds `ui/cm_paintshop.json` using Content Manager's documented-in-source `carpaint` format and includes the actual skin DDS override. Paint Shop therefore has a named body-color control instead of relying on texture guessing. This is a visual color match, not a calibrated paint measurement.

To recolor: open the car in Content Manager's **Custom Showroom → Paint Shop**, change **Body paint (includes mirror caps and tailgate trim)**, and save as a skin. Blue Flame remains the supplied default. Refresh the skin/showroom if a cached preview shows the old color. Real game appearance depends on lighting and the selected post-processing filter.

## Validation and limits

The executable Lua controller is tested with mocked official CSP scene APIs at 20, 60 and 144 Hz over RPM steps from zero to redline, clipping, invalid inputs, day/night backlight changes, and LOD-reference refresh. This runs the shipped controller itself, but does not run CSP. Geometry checks cover the complete pointer sweep from two eye positions, unobstructed window apertures, removal of the duplicate pod, and reflected horizon rays at three driver-eye heights. The Paint Shop schema is checked against Content Manager's actual `PaintShop.cs` and `CarPaint.cs`; the Windows Paint Shop UI is not available here.

All four KN5 models undergo structural/index/normal/tangent/texture/mipmap checks and lossless binary roundtrip. Other mesh positions, normals, UVs and indices are compared with 0.14, including doors, steering, wheel badges, grille modules, roof and cluster enclosure. Non-paint/non-screen materials remain unchanged. All 0.14 data/audio/collider files are byte-identical, and the original drivetrain/audio/collider, decoded driver animation and native MID font are checked again. Full ZIP CRC and member equality checks precede publication; the public download is then checked by SHA-256.

**Assetto Corsa, Pure and CSP cannot run in this Linux workspace.** Screen exposure, real mirror projection, live needle motion and Content Manager UI operation require in-game confirmation. Blender previews show actual geometry with the body/windows present; RPM poses are manual illustrations, not proof of live telemetry. The fallback card is shown instead of fabricating a live Android Auto screenshot. The donor-derived 2023 cabin still approximates 2019 Adventure; climate/economy/ODO placeholder graphics remain decorative. Existing coarse exterior LOD boundary warnings and donor ACI online entitlement behavior are retained.

## Prepared-workspace rebuild

Python 3, NumPy, SciPy, Pillow, Blender 4.3 and a scratch-only Lupa test dependency are installed. The verified 0.14 archive is the rebuild baseline. The visual script is `extension/rav4_instruments.lua`; the preserved drivetrain script is `data/script.lua`.

```bash
python3 tools/repair_revision_15.py
python3 tools/validate_revision_15.py
blender -b -t 8 -P tools/render_release_15.py -- mirror front_on cockpit rpm_1000 rpm_5000
python3 tools/package_revision_15.py
```

Source/license notes are retained. No proprietary BMW software or Google phone operating system is bundled: Android Auto here is CSP's shared simulated interface.
