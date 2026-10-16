"""RAV4-sized drift wheels and explicit factory TC-off, from verified 1.0.1.

Only the dedicated rav4_drift car is changed. Native physics INI syntax is
preserved, including the suspension file confirmed working by the owner.
"""
import copy
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np

from build_rav4_drift import MODELS, model_fit, readini
from fix_drift_native_ini_101 import native_bytes, strict_view
from kn5 import Kn5
from validate_revision_08 import check_configuration, check_model, parse_ini

ROOT = Path('/workspace/Assetto-Corsa-Rav4')
ART = ROOT / 'artifacts'
CAR = ROOT / 'content/cars/rav4_drift'
PREFIX = 'content/cars/rav4_drift/'
SOURCE = ART / 'Rav4_Drift_1.0.1.zip'
SOURCE_SHA = 'f618128facbba5c16aa7c1a6ae3c990727acef494203e3ea53bd94bebe408468'
SCALE = 1.14


def sha(data):
    return hashlib.sha256(data).hexdigest()


def patch_values(data, values):
    """Change selected native keys, retaining comments, BOM and CRLF."""
    section = None
    seen = set()
    lines = []
    for line in data.decode('utf-8-sig').splitlines(keepends=True):
        if line.startswith('['):
            section = line[1:line.index(']')]
        if '=' in line:
            key, value = line.split('=', 1)
            entry = (section, key)
            if entry in values:
                raw = value.rstrip('\r\n')
                comment = ''
                if ';' in raw:
                    before, tail = raw.split(';', 1)
                    comment = before[len(before.rstrip()):] + ';' + tail
                ending = '\r\n' if line.endswith('\r\n') else '\n'
                line = key + '=' + str(values[entry]) + comment + ending
                seen.add(entry)
        lines.append(line)
    assert seen == set(values)
    return (b'\xef\xbb\xbf' if data.startswith(b'\xef\xbb\xbf') else b'') + ''.join(lines).encode()


def main():
    assert sha(SOURCE.read_bytes()) == SOURCE_SHA
    report = {'release': 'Rav4 Drift 1.0.2', 'status': 'passed_offline_checks',
              'assetto_corsa_runtime_tested': False,
              'baseline_1_0_1_launch_confirmed_by_owner': True,
              'source_archive_sha256': SOURCE_SHA, 'diameter_scale': SCALE,
              'models': {}, 'tyres': {}}
    with ZipFile(SOURCE) as source:
        replacements = {}
        old_tyres = parse_ini(source.read(PREFIX + 'data/tyres.ini').decode('utf-8-sig'))
        tyre_values = {}
        targets = copy.deepcopy(old_tyres)
        for axle in ('FRONT', 'REAR'):
            for key in ('RADIUS', 'RIM_RADIUS', 'ANGULAR_INERTIA'):
                power = 2 if key == 'ANGULAR_INERTIA' else 1
                value = float(old_tyres[axle][key]) * SCALE ** power
                targets[axle][key] = f'{value:.12f}'
                tyre_values[axle, key] = targets[axle][key]
            report['tyres'][axle] = {
                'old_radius_m': float(old_tyres[axle]['RADIUS']),
                'new_radius_m': float(targets[axle]['RADIUS']),
                'new_diameter_inches': float(targets[axle]['RADIUS']) * 2 / .0254,
                'width_m_unchanged': float(targets[axle]['WIDTH']),
                'angular_inertia_kg_m2': float(targets[axle]['ANGULAR_INERTIA'])}
        replacements[PREFIX + 'data/tyres.ini'] = patch_values(
            source.read(PREFIX + 'data/tyres.ini'), tyre_values)
        old_drive = parse_ini(source.read(PREFIX + 'data/drivetrain.ini').decode())
        final = float(old_drive['GEARS']['FINAL']) * SCALE
        replacements[PREFIX + 'data/drivetrain.ini'] = patch_values(
            source.read(PREFIX + 'data/drivetrain.ini'), {('GEARS', 'FINAL'): f'{final:.4f}'})
        ratios = source.read(PREFIX + 'data/final.rto').decode().splitlines()
        ratios.append(f'{final:.4f}|{final:.4f}')
        ratios.sort(key=lambda line: float(line.split('|')[1]))
        replacements[PREFIX + 'data/final.rto'] = ('\r\n'.join(ratios) + '\r\n').encode()
        assert abs(final / float(targets['REAR']['RADIUS']) -
                   float(old_drive['GEARS']['FINAL']) / float(old_tyres['REAR']['RADIUS'])) < 1e-9
        replacements[PREFIX + 'data/electronics.ini'] = native_bytes({
            'TRACTION_CONTROL': {'PRESENT': '0', 'ACTIVE': '0',
                                 'SLIP_RATIO_LIMIT': '0.10', 'CURVE': '',
                                 'RATE_HZ': '100', 'MIN_SPEED_KMH': '0'}})
        report['traction_control'] = {'PRESENT': 0, 'ACTIVE': 0,
            'scope': 'Car factory assist configuration; player/server forced assists remain external.'}
        report['final_drive'] = {'before': float(old_drive['GEARS']['FINAL']),
                                'after': final, 'final_drive_per_tyre_radius_preserved': True}

        for filename in MODELS:
            path = CAR / filename
            path.write_bytes(source.read(PREFIX + filename))
            before = Kn5(path)
            after = Kn5(path)
            model_fit.sizes = {}
            changes = model_fit(after, targets)
            changed = {mesh for item in changes.values() for mesh in item['meshes']}
            old_nodes = {n['name']: n for n, _ in before.nodes()}
            for n, _ in after.nodes():
                old = old_nodes[n['name']]
                if n['kind'] == 1:
                    assert np.array_equal(n['matrix'], old['matrix'])
                else:
                    assert n['material'] == old['material']
                    assert np.array_equal(n['indices'], old['indices'])
                    if n['name'] not in changed:
                        assert np.array_equal(n['vertices'], old['vertices'])
                    else:
                        assert np.array_equal(n['vertices'][:, 6:8], old['vertices'][:, 6:8])
            assert after.materials == before.materials and after.textures == before.textures
            measured = {}
            for node, _ in after.nodes():
                if node['kind'] != 1 or not node['name'].startswith('WHEEL_'):
                    continue
                side = node['name'][6:]
                axle = 'FRONT' if side[1] == 'F' else 'REAR'
                points = np.concatenate([n['vertices'][:, :3] for n in node['children']
                    if n['kind'] == 2 and ('TYRE' in n['name'] or 'Tires' in n['name'])])
                radius = float(np.linalg.norm(points[:, 1:3], axis=1).max())
                width = float(np.ptp(points[:, 0]))
                assert abs(radius - float(targets[axle]['RADIUS'])) < 2e-6
                assert abs(width - float(targets[axle]['WIDTH'])) < 2e-6
                measured[side] = {'radius_m': radius, 'width_m': width}
            assert len(measured) == 4
            after.save(path)
            checked, names, checks = check_model(path)
            check_configuration(CAR, names, checked)
            replacements[PREFIX + filename] = path.read_bytes()
            report['models'][filename] = {'tyre_measurements': measured,
                'wheel_and_suspension_scaling': changes,
                'all_materials_textures_body_cabin_glass_mirrors_badges_unchanged': True,
                'structural_checks': checks}
            print(filename, 'wheel dimensions and preserved materials checked', flush=True)

        # Strict keys and validated launch-fix files must survive unmodified.
        assert strict_view(source.read(PREFIX + 'data/suspensions.ini'))['FRONT']['TYPE'] == 'STRUT'
        for name, data in replacements.items():
            if name.endswith('.ini'):
                assert all(k == k.strip() and v == v.lstrip()
                    for section in strict_view(data).values() for k, v in section.items())
        notes = '''Rav4 Drift 1.0.2 — larger wheels and factory traction control off

PATCH: requires the working Rav4 Drift 1.0.1 installation. Close Assetto
Corsa. Extract this ZIP into the Assetto Corsa folder containing acs.exe,
merging content/cars/rav4_drift and replacing files. Start a new session.
FULL ZIP: install through Content Manager, including the shared gauge font.

Wheels/tyres are 14% taller: approximately 29.3 inches front / 29.5 rear,
close to the original RAV4 model's wheel envelope. Tyre widths retain the
Supra drift setup: 245 mm front / 285 mm rear. All four visual LODs, rim,
rotor, hub/badge and caliper fit are updated together. Original matte wheel
materials are byte-preserved. Tyre/rim physics radii match the enlargement;
wheel angular inertia increases with radius squared. The final drive is
4.0014 instead of 3.510 to preserve gearing relative to road speed.
All donor grip, thermal/wear curves, gears, differential and engine remain.

The car explicitly has traction control PRESENT=0, ACTIVE=0. Use Factory
or Off for traction control in Content Manager's driving assists; a global
or server-forced On setting is outside the car's factory configuration.
No per-frame script changes or automatic overrides of your controls.

The native car.ini and suspensions.ini from the owner-confirmed working
1.0.1 are byte-preserved. Cabin, Android Auto, lights, mirrors, rear matte
badge, paint shop and audio files are unchanged. The separate BMW-powered
RAV4 is unchanged. Loose physics data; no data.acd is supplied.

Offline checks cover all four model LODs, wheel dimensions, preserved
materials/geometry, native INI keys, gearing and package integrity.
Assetto Corsa is unavailable here. Dynamic clearance at full steering lock
and suspension compression still needs checking in-game.
'''
        ui = json.loads(source.read(PREFIX + 'ui/ui_car.json'))
        ui['version'] = '1.0.2 - RAV4-sized tyres / factory TC off'
        ui['description'] = ('1.0.2: 14% taller wheels/tyres, matched physics radii/inertia, '
            '4.0014 final drive preserves road-speed gearing; factory traction control disabled. '
            'Matte rims and confirmed 1.0.1 launch fix retained. ' + ui['description'])
        replacements[PREFIX + 'ui/ui_car.json'] = (json.dumps(ui, indent=2) + '\n').encode()
        replacements[PREFIX + 'INSTALL_README.txt'] = notes.encode()
        replacements[PREFIX + 'VISUAL_REVISION_NOTES.md'] = notes.encode()
        manifest = json.loads(source.read(PREFIX + 'INSTALL_MANIFEST.json'))
        manifest.update(release='Rav4 Drift 1.0.2', runtime_tested=False)
        replacements[PREFIX + 'INSTALL_MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
        report['preserved_native_launch_files'] = {name: sha(source.read(PREFIX + 'data/' + name))
                                                  for name in ('car.ini', 'suspensions.ini')}
        report['baseline_validation_report_sha256'] = sha(source.read(PREFIX + 'VALIDATION_REPORT.json'))
        report['unchanged_baseline_archive_members'] = len(set(source.namelist()) - set(replacements) -
                                                          {PREFIX + 'VALIDATION_REPORT.json'})
        replacements[PREFIX + 'VALIDATION_REPORT.json'] = (json.dumps(report, indent=2) + '\n').encode()
        for name, data in replacements.items():
            (ROOT / name).write_bytes(data)
        assert readini(CAR / 'data/tyres.ini') == targets
        full = ART / 'Rav4_Drift_1.0.2.zip'
        patch = ART / 'Rav4_Drift_1.0.2_Larger_Tyres_TC_Off_Patch.zip'
        with ZipFile(full, 'w', ZIP_DEFLATED, compresslevel=9) as out:
            for name in source.namelist():
                out.writestr(name, replacements.get(name, source.read(name)))
        with ZipFile(patch, 'w', ZIP_DEFLATED, compresslevel=9) as out:
            for name, data in replacements.items():
                out.writestr(name, data)
        outputs = []
        for path in (full, patch):
            with ZipFile(path) as out:
                assert out.testzip() is None
                assert len(out.namelist()) == len({n.lower() for n in out.namelist()})
                for name in out.namelist():
                    assert out.read(name) == replacements.get(name, source.read(name))
            digest = sha(path.read_bytes())
            (ART / (path.name + '.sha256')).write_text(digest + '  ' + path.name + '\n')
            outputs.append({'file': path.name, 'bytes': path.stat().st_size, 'sha256': digest})
        result = {'release': '1.0.2', 'outputs': outputs, 'status': 'passed_offline_checks',
                  'runtime_tested': False, 'diameter_scale': SCALE,
                  'changed_members': sorted(replacements)}
        (ART / 'release_drift_102_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
        (ROOT / 'rav4-drift-tyres-102.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
