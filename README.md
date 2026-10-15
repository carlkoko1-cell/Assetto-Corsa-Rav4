# RAV4 Adventure — Blue Flame CARL, supplied-model interior 0.12

This complete update replaces the former approximate cabin with interior geometry from the user's **2023-toyota-rav4-hybrid.zip** upload. Its dashboard, front/rear seats, four door panels, center console, wheel and controls are fitted into the existing mod and adapted toward the 2019 Adventure's black/orange interior. The exterior, BMW X5M tune, sound and collider are retained.

## Install

Back up the existing car folder and personal skins/setups. Drag **Toyota_RAV4_Blue_Flame_CARL_Interior_0.12.zip** into Content Manager and **install all detected entries: the car and included instrument font**. Select **Interior 0.12** and refresh the cached preview. The car ID is unchanged. For manual installation, extract into the Assetto Corsa installation root, preserving both `content/cars/` and `content/fonts/`.

The instrument font retains its `rav4_adventure_mid_10` name for compatibility. The donor mod still requires CSP build 2744. Begin with offline practice. Its existing signed ACI entitlement requirement for online throttle remains.

## What changed

- **Actual replacement cabin:** imported authored FBX triangle positions, corner normals and UVs, rather than repainting the old dash. The supplied seats have shaped bolsters/headrests, modeled center panels, belt hardware and real stitch-strip geometry. Door panels, storage pockets, dashboard/vents, shifter and cupholder recesses now come from the supplied model.
- **Adventure materials:** black upholstery and molded plastics, orange stitch strips, orange shelf floors/forward storage details and graphite/satin trim. Existing fine-grain leather/dash maps replace single-color palette UVs on broad panels. Supplied texture/normal UVs remain on keys, pictograms and decorative details. The hybrid EV legend is replaced with SNOW, and its obsolete normal-map embossing is flattened.
- **Fit:** a center-preserving width adjustment aligns the driver bay and outer trim with the existing body; cabin depth follows its larger donor dimensions. Small original A-pillar trim surfaces bridge the existing windshield/body seam. The supplied tablet assembly is narrowed toward the earlier 8-inch layout. These are fitted adaptations rather than factory measurements.
- **Steering:** the supplied 380mm wheel, hub, Toyota emblem and switch pods replace the previous procedural wheel. Its plane is aligned to the existing native steering pivot/tilt with a 1.011 scale correction. The previous driver rig/362-frame animation, native lock and physics are unchanged. Offline checks compare the actual imported rim against the driver contact path; glove/skin clearance still needs a game check.
- **Instruments:** the supplied hybrid power/blue graphics and baked readings are removed. An Adventure-style face is fitted inside the supplied hood, with a black backing to seal light gaps. Native speed/RPM pointers, mph speed/gear/clock fields, turn indicators and the six CSP fuel segments are fitted to it. The 0.11 native-text identity-parent correction is retained. The coolant graphic remains decorative. There is no newly implemented accumulated-distance odometer.
- **Climate/infotainment:** supplied modeled climate knobs, keys, power sockets and shifter hardware replace the old added controls. The small LCD uses the user-reference 60/64/fan artwork. The navigation image is original decorative artwork. These displays do not simulate climate control or interactive navigation.
- **Mirrors/exterior:** the donor's lower rearview housing/stem is removed to avoid a second mirror. The previously raised source-fitted center mirror, all three repaired mirror UVs, low-reflection glass, Blue Flame paint/blue garnish, solid roof/no crossbars/no front plate, wheel badges and Tennessee In the Black CARL plate are retained.
- **LOD models:** imported cabin geometry is reduced with connected edge collapse for B/C/D while keeping the supplied moving wheel and small labels intact. Every LOD receives the same material conversion and instrument bindings; the existing exterior LOD geometry is preserved. Imported cabin attributes are quantized to five decimal places for compact storage (position change under 0.01 mm); the exterior and audio are untouched.

## Checks and limits

`VALIDATION_REPORT.json` checks the actual delivered KN5 files for roundtrip parsing, triangle indices/winding, normal/tangent bases, texture and mip closure, configuration references and preservation of original physics/audio/collider. It additionally checks the imported wheel/pivot/contact path, unchanged decoded driver motion and pointer calibration, absence of the old cabin and duplicate donor mirror, preserved exterior geometry, retained mirror UV repair and progressively smaller cabin LODs. The complete ZIP is CRC-checked and every member compared against the final files. The published ZIP is downloaded and checked against its SHA-256.

**Assetto Corsa is unavailable in this Linux environment.** Native digit orientation, live mirrors/gauges, CSP illumination, actual driver skinning/glove clearance, sound playback and LOD appearance require game testing. Blender previews use approximate materials and deliberately leave native digital fields blank; those images do not prove the AC font/reflection renderer. Seat/console cutaways hide glazing, wipers and upper trim solely for inspection. The mirror close-up also hides the windshield to inspect console/glass clearance; it does not demonstrate native game reflections.

The supplied model is a 2023 Hybrid interior adapted toward the requested 2019 Adventure. Its tablet, switch arrangements, seat shapes and some details still differ from the earlier trim. It is a substantial geometry replacement, not an OEM scan or an exact photorealistic factory reconstruction. Blue Flame remains an 8W9-inspired color estimate without measured calibration. Existing speed/RPM scales cover 0–140 mph/0–8000 RPM; the preserved high-powered tune can exceed the speed face. Previous source exterior boundary warnings remain in the validation report. Climate/infotainment artwork is static.

## Rebuild in the prepared workspace

Python 3, NumPy, SciPy, Pillow and Blender 4.3 are used. `interior_revision_12.py` starts from the SHA-256-verified complete 0.11 archive and the safely extracted user model. It writes only cabin visuals/configuration and metadata. No executable content from the uploaded archive is run. Source pictures inform the conversion and are not redistributed as photographed textures.

```bash
cd /workspace/Assetto-Corsa-Rav4
blender --background --threads 8 --factory-startup --python tools/extract_hybrid_cabin_12.py -- --export-only
blender --background --threads 8 --factory-startup --python tools/simplify_donor_12.py
python3 tools/interior_revision_12.py
python3 tools/validate_revision_12.py
blender --background --threads 8 --factory-startup --python tools/render_release_12.py -- cockpit console steering seats cluster climate mirror
python3 tools/package_revision_12.py
```

The extraction script expects the uploaded FBX/textures under `/workspace/scratch/interior12/donor/model/`; they are already staged in this workspace. The archive contains the adapted car assets, not the complete donor vehicle/FBX. Font licenses and source notes are included.
