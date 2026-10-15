# RAV4 Adventure Blue Flame CARL — Interior 0.14

Screenshot-guided repairs to the 0.13 update. Existing BMW X5M tune/audio/collider, steering animation, black/orange cabin, Blue Flame paint and CARL In the Black plate are retained.

## Download and installation

[Download the complete 0.14 ZIP](https://raw.githubusercontent.com/carlkoko1-cell/Assetto-Corsa-Rav4/rav4-interior-v0.14-download/Toyota_RAV4_Blue_Flame_CARL_Interior_0.14.zip)

[Offline preview board](https://raw.githubusercontent.com/carlkoko1-cell/Assetto-Corsa-Rav4/rav4-interior-v0.14-download/RAV4_Adventure_Interior_0.14_Previews.jpg)

Exit the running AC session before updating. Back up personal skins/setups, drag the complete ZIP into Content Manager and install all entries: car and `rav4_adventure_mid_10` font. Select Interior 0.14, refresh cached previews and start a new session. Manual install: extract into the Assetto Corsa root, preserving `content/cars/` and `content/fonts/`.

CSP build 2744 remains required. The full Android Auto interface uses CSP's shared `android_auto` package; keep CSP and its shared Lua assets current through Content Manager. If the screen shows the explicit “CSP Android Auto display required” fallback card, the shared interface has not loaded. This is CSP's simulated in-car interface, not phone projection or proprietary BMW iDrive.

**The blue grille LEDs now follow the normal headlight switch. No Extra B binding is needed.** Extra A fog-light behavior is retained.

## Corrections

- **Door cards and windows:** the 0.13 convex-hull return volumes are removed. Actual card geometry is fitted inside the retained body and extended to the appropriate pillar ends. Upper card faces are clipped 10 mm below the measured original side-window sill. Concave, triangulated backing profiles stay below the glass, with separate closed returns bridging the relief at each card end to the body. Existing upholstery, speakers, handles and molded details are kept. The previous tall triangular obstruction is gone in the body-present inspection views.
- **RPM:** a dedicated numeric CSP analog-indicator section owns the live RPM pointer; the native RPM entry is removed to avoid two controllers. The pointer has a thin 3D body, a separate material and the same calibrated 0–8000/183-degree scale. It stays close to its face to avoid parallax. Small donor hood faces which intrude into the pointer sweep are removed where necessary; the opaque face/enclosure behind them stays. Native speed/gear/clock and their known-working font/orientation are unchanged. Live game operation still requires testing.
- **Glass:** interior glazing uses alpha-blended materials with zero specular/Fresnel reflection and is excluded from the Extra FX G-buffer pass. Exterior glazing retains a much fainter reflection. Glass geometry, repaired mirror UVs and rain/wiper surface bindings are retained. No glass refraction or reflective second cockpit shell is introduced.
- **Grille lights:** four smaller 135 × 20 × 8 mm black housings follow the measured front curve of the actual upper crossbar. Their positions move inward and onto that bar; the old overhanging/floating modules are removed. Six blue lenses per module share a native light mesh. Native light sections are contiguous, and both native/CSP headlight bindings control illumination, with modest short-range blue fill. No flashing pattern is used.
- **Wheels:** original dark `Rims2` diffuse color is retained with a matte diffuse shader, very low specular and no environment reflection. The machined `Rims1` faces have restrained satin reflection; tire and badge geometry are unchanged.
- **Screen:** the 0.13 navigation-only template is replaced by CSP's full `Display_AndroidAuto` interface, including interactive shared apps/navigation and a reverse-camera position. Its 1024 × 544 canvas fits the RAV4 viewport. The display owns its shader/emission; old native screen-light writes are removed. The offline fallback is explicitly labeled, rather than presenting a fake live interface.

## Checks and limits

All four KN5 LODs undergo binary roundtrip, index/winding, normal/tangent, texture/mipmap and literal configuration-reference checks. Original drivetrain/engine/suspension/tyre data, audio and collider are compared with the original ZIP. Decoded driver motion, the native font and other unchanged geometry/transforms are checked.

New regression checks cover 288 rays through the lowest portions of the actual side-window apertures per LOD, both ends of every closed door return, and every card vertex against the measured glass sill. The same aperture test reproduces **92 blocked rays in 0.13 and zero in 0.14** on the highest LOD. The pointer sweep is checked at 17 RPM inputs from two driver-eye positions, including its tip and midsections. These checks also enforce a single RPM controller, unchanged native speed settings, contiguous native headlight entries, four correctly bound grille emitters, matte black wheel material and the full Android Auto configuration.

The complete ZIP is CRC-checked and every entry compared with the final files. Published downloads are checked by SHA-256. Previews keep the body/windows present. RPM and grille light states are manually posed in Blender solely to inspect geometry/materials; native digital fields are deliberately blank, and the Android Auto fallback shown offline is not the runtime interface.

Assetto Corsa/CSP cannot run in this Linux workspace. Live RPM/input behavior, Android Auto loading/interactions, actual glass/SSR/night appearance, light switching, mirrors and driver skinning still require an in-game check. Blender previews do not verify those systems. The cabin remains an adapted user-supplied 2023 Hybrid model, not an exact OEM 2019 scan. Climate artwork, economy/ODO placeholders and coolant marker remain decorative. Existing exterior LOD boundary warnings and original ACI online entitlement behavior are retained.

## Rebuild in the prepared workspace

Python 3, NumPy, SciPy, Pillow and Blender 4.3 are installed. The SHA-256-verified 0.13 archive is the baseline; original donor metadata and official CSP shared-interface source are staged in `/workspace/scratch`. Uploaded code is not executed.

```bash
cd /workspace/Assetto-Corsa-Rav4
python3 tools/repair_revision_14.py
python3 tools/validate_revision_14.py
blender -b -t 8 -P tools/render_release_14.py -- passenger_window rear_door driver_window wheel rpm_1000 rpm_5000 front_on grille_on cockpit
python3 tools/package_revision_14.py
```

Font licenses/source notes are included. Historical build reports remain in the workspace but are excluded from this install archive.
