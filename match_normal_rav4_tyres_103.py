"""Restore exact normal-RAV4 wheel geometry to the separate drift edition.

Use immutable, checksum-verified full ZIPs; retain the owner's working drift
configuration and native suspension syntax. No BMW physics are transferred.
"""
import copy
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np

from build_rav4_drift import MODELS
from fix_drift_native_ini_101 import strict_view
from kn5 import Kn5
from resize_drift_tyres_102 import patch_values
from validate_revision_08 import check_configuration, check_model, parse_ini

ROOT = Path('/workspace/Assetto-Corsa-Rav4')
ART = ROOT / 'artifacts'
CAR = ROOT / 'content/cars/rav4_drift'
PREFIX = 'content/cars/rav4_drift/'
NORMAL_PREFIX = 'content/cars/toyota_rav4_adventure_blueflame_x5m/'
SOURCE = ART / 'Rav4_Drift_1.0.2.zip'
NORMAL = ART / 'Toyota_RAV4_Blue_Flame_CARL_Matte_Badge_0.16.zip'
BASE_DONOR = ART / 'Rav4_Drift_1.0.1.zip'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def wheel_dimensions(k):
    result = {}
    for n, _ in k.nodes():
        if n['kind'] != 1 or n['name'] not in {'WHEEL_LF', 'WHEEL_RF', 'WHEEL_LR', 'WHEEL_RR'}:
            continue
        tyres = np.concatenate([c['vertices'][:, :3] for c in n['children']
            if c['kind'] == 2 and ('TYRE' in c['name'] or 'Tires' in c['name'])])
        rims = np.concatenate([c['vertices'][:, :3] for c in n['children']
            if c['kind'] == 2 and 'Rims' in c['name']])
        result[n['name'][6:]] = {
            'radius_m': float(np.linalg.norm(tyres[:, 1:3], axis=1).max()),
            'width_m': float(np.ptp(tyres[:, 0])),
            'rim_outer_radius_m': float(np.linalg.norm(rims[:, 1:3], axis=1).max())}
    assert len(result) == 4
    return result


def main():
    assert sha(SOURCE.read_bytes()) == 'f645cdda5f3db3f16fc24a821e96e203b32ae611719c81893d10e22c849408e0'
    assert sha(NORMAL.read_bytes()) == '0387057f840096194ed6fe7435026bb381f8aae55a2b37dd4541ce989fe79be7'
    assert sha(BASE_DONOR.read_bytes()) == 'f618128facbba5c16aa7c1a6ae3c990727acef494203e3ea53bd94bebe408468'
    report = {'release': 'Rav4 Drift 1.0.3', 'status': 'passed_offline_checks',
              'assetto_corsa_runtime_tested': False,
              'normal_visual_source': NORMAL.name,
              'normal_source_sha256': sha(NORMAL.read_bytes()),
              'drift_source_sha256': sha(SOURCE.read_bytes()), 'models': {}}
    with ZipFile(SOURCE) as source, ZipFile(NORMAL) as normal, ZipFile(BASE_DONOR) as donor:
        replacements = {}
        main_dimensions = None
        for filename in MODELS:
            path = CAR / filename
            # Verify differences from the existing drift model are confined to
            # wheel/caliper geometry before restoring complete normal KN5 bytes.
            path.write_bytes(source.read(PREFIX + filename))
            old = Kn5(path)
            normal_bytes = normal.read(NORMAL_PREFIX + filename)
            path.write_bytes(normal_bytes)
            new = Kn5(path)
            assert new.materials == old.materials and new.textures == old.textures
            old_nodes = {n['name']: n for n, _ in old.nodes()}
            new_nodes = {n['name']: n for n, _ in new.nodes()}
            assert old_nodes.keys() == new_nodes.keys()
            wheel_parts = set()
            for n, _ in new.nodes():
                if n['kind'] == 1 and n['name'] in {
                    prefix + side for prefix in ('WHEEL_', 'SUSP_') for side in ('LF', 'RF', 'LR', 'RR')}:
                    wheel_parts.update(child['name'] for child, _ in new.nodes(n) if child['kind'] != 1)
            for name, n in new_nodes.items():
                before = old_nodes[name]
                if n['kind'] == 1:
                    assert np.array_equal(n['matrix'], before['matrix']), name
                else:
                    assert n['material'] == before['material'], name
                    assert np.array_equal(n['indices'], before['indices']), name
                    assert np.array_equal(n['vertices'][:, 6:8], before['vertices'][:, 6:8]), name
                    if name not in wheel_parts:
                        assert np.array_equal(n['vertices'], before['vertices']), name
            dimensions = wheel_dimensions(new)
            if filename == 'x5.kn5':
                main_dimensions = dimensions
            checked, names, checks = check_model(path)
            check_configuration(CAR, names, checked)
            replacements[PREFIX + filename] = normal_bytes
            report['models'][filename] = {
                'sha256': sha(normal_bytes), 'byte_identical_to_normal_rav4': True,
                'dimensions': dimensions, 'structural_checks': checks,
                'all_materials_and_nonwheel_geometry_preserved_from_1_0_2': True}
            print(filename, 'exact normal-RAV4 model verified', flush=True)

        # Match native contact dimensions to the actual normal-RAV4 meshes.
        # Keep donor grip/wear/thermal curves rather than importing BMW tyres.
        old_tyres = parse_ini(source.read(PREFIX + 'data/tyres.ini').decode('utf-8-sig'))
        original_tyres = parse_ini(donor.read(PREFIX + 'data/tyres.ini').decode('utf-8-sig'))
        values = {}
        expected = copy.deepcopy(old_tyres)
        axle_sizes = {}
        for axle, sides in [('FRONT', ('LF', 'RF')), ('REAR', ('LR', 'RR'))]:
            averaged = {key: sum(main_dimensions[s][key] for s in sides) / 2
                        for key in ('radius_m', 'width_m', 'rim_outer_radius_m')}
            base_radius = float(original_tyres[axle]['RADIUS'])
            inertia = float(original_tyres[axle]['ANGULAR_INERTIA']) * (averaged['radius_m'] / base_radius) ** 2
            settings = {'RADIUS': averaged['radius_m'], 'WIDTH': averaged['width_m'],
                        'RIM_RADIUS': averaged['rim_outer_radius_m'], 'ANGULAR_INERTIA': inertia}
            for key, value in settings.items():
                values[axle, key] = f'{value:.12f}'
                expected[axle][key] = f'{value:.12f}'
            values[axle, 'NAME'] = 'VDC RAV4-size'
            expected[axle]['NAME'] = 'VDC RAV4-size'
            axle_sizes[axle] = {**averaged, 'angular_inertia_kg_m2': inertia,
                                'diameter_inches': averaged['radius_m'] * 2 / .0254}
        replacements[PREFIX + 'data/tyres.ini'] = patch_values(
            source.read(PREFIX + 'data/tyres.ini'), values)
        assert parse_ini(replacements[PREFIX + 'data/tyres.ini'].decode('utf-8-sig')) == expected
        base_drive = parse_ini(donor.read(PREFIX + 'data/drivetrain.ini').decode())
        final = float(base_drive['GEARS']['FINAL']) * axle_sizes['REAR']['radius_m'] / float(original_tyres['REAR']['RADIUS'])
        final_string = f'{final:.10f}'
        replacements[PREFIX + 'data/drivetrain.ini'] = patch_values(
            source.read(PREFIX + 'data/drivetrain.ini'), {('GEARS', 'FINAL'): final_string})
        # Use the original donor's adjustment list and add the new default.
        ratios = donor.read(PREFIX + 'data/final.rto').decode().splitlines()
        ratios.append(final_string + '|' + final_string)
        ratios.sort(key=lambda line: float(line.split('|')[1]))
        replacements[PREFIX + 'data/final.rto'] = ('\r\n'.join(ratios) + '\r\n').encode()
        assert abs(float(final_string) / axle_sizes['REAR']['radius_m'] -
                   float(base_drive['GEARS']['FINAL']) / float(original_tyres['REAR']['RADIUS'])) < 1e-8
        tc = strict_view(source.read(PREFIX + 'data/electronics.ini'))
        assert tc['TRACTION_CONTROL']['PRESENT'] == '0' and tc['TRACTION_CONTROL']['ACTIVE'] == '0'
        report['traction_control_off_settings_preserved'] = True
        report['tyre_physics_dimensions'] = axle_sizes
        report['final_drive'] = float(final_string)
        report['native_car_and_suspension_files_byte_preserved'] = True
        notes = f'''Rav4 Drift 1.0.3 — exact normal-RAV4 wheels and tyres

COMPLETE ZIP: close Assetto Corsa, drag the ZIP into Content Manager, install
all car/font files and allow replacement of the existing Rav4 Drift.
This complete package needs no earlier patch. Car ID stays rav4_drift.

All four model LODs are byte-identical to the normal matte-badge RAV4 0.16.
The exact normal tyres, rims, width, sidewalls, rotors, calipers, wheel badges
and matte wheel materials are restored. No approximate 14% resize remains.
Tyres are approximately 29.46 inches in diameter and 254 mm wide. The normal
model has tiny left/right differences; physics uses axle averages (below
0.01 mm deviation). Its rim outer radius is measured from the actual model.

The drift tyre contact radius/width and rim radius follow that geometry.
Wheel inertia is adjusted from the Supra donor by radius squared. All
other donor drift grip/thermal/wear settings remain. Final drive {final_string}
preserves the donor's gearing relative to tyre circumference. Supra RWD
drivetrain, differential, engine/turbos, suspension tune and sound remain.
No BMW physics files are imported from the normal RAV4.

Factory traction control remains disabled: PRESENT=0, ACTIVE=0. Set TC to
Factory or Off in Content Manager's driving assists rather than forced On.
Working native car.ini/suspensions.ini, interior, Android Auto, mirrors,
lighting, matte rear badge and paint shop remain unchanged from 1.0.2.
The separate normal/BMW-powered car and previous downloads are unchanged.

Exact model-byte comparison, all four model structural checks, native INI
keys, gearing, preserved files and complete ZIP integrity are checked.
Assetto Corsa is unavailable here; full-lock/compressed suspension clearance
and driving behavior still need an in-game check.
'''
        replacements[PREFIX + 'INSTALL_README.txt'] = notes.encode()
        replacements[PREFIX + 'VISUAL_REVISION_NOTES.md'] = notes.encode()
        ui = json.loads(source.read(PREFIX + 'ui/ui_car.json'))
        ui['version'] = '1.0.3 - Exact normal RAV4 wheels and tyres / TC off'
        ui['description'] = ('Exact wheel and tyre geometry from the normal RAV4 Adventure 0.16, '
            'including front/rear widths and sidewalls; all four model LODs byte-identical. '
            'Matching contact/rim dimensions, factory traction control off, matte wheel materials. '
            'Supra drift engine, RWD six-speed/locked differential, suspension tune and sound retained. '
            'Native launch fix, black-orange interior, Android Auto, gauges, mirrors, lights, '
            'matte rear Toyota emblem and editable Blue Flame paint retained. '
            'Offline checks passed; in-game steering/compression clearance untested.')
        replacements[PREFIX + 'ui/ui_car.json'] = (json.dumps(ui, indent=2) + '\n').encode()
        manifest = json.loads(source.read(PREFIX + 'INSTALL_MANIFEST.json'))
        manifest.update(release='Rav4 Drift 1.0.3', runtime_tested=False,
                        wheels_and_tyres='exact normal RAV4 0.16 geometry, every LOD')
        replacements[PREFIX + 'INSTALL_MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
        report['unchanged_archive_members'] = len(set(source.namelist()) - set(replacements) - {PREFIX + 'VALIDATION_REPORT.json'})
        replacements[PREFIX + 'VALIDATION_REPORT.json'] = (json.dumps(report, indent=2) + '\n').encode()
        for name, data in replacements.items():
            (ROOT / name).write_bytes(data)
        for filename in ('data/car.ini', 'data/suspensions.ini', 'data/electronics.ini', 'data/engine.ini'):
            assert (CAR / filename).read_bytes() == source.read(PREFIX + filename)
        for name, data in replacements.items():
            if name.endswith('.ini'):
                assert all(k == k.strip() and v == v.lstrip()
                    for section in strict_view(data).values() for k, v in section.items())
        full = ART / 'Rav4_Drift_1.0.3_Full.zip'
        with ZipFile(full, 'w', ZIP_DEFLATED, compresslevel=9) as out:
            for name in source.namelist():
                out.writestr(name, replacements.get(name, source.read(name)))
        with ZipFile(full) as out:
            assert out.testzip() is None
            assert len(out.namelist()) == len({n.lower() for n in out.namelist()})
            for name in out.namelist():
                assert out.read(name) == replacements.get(name, source.read(name))
            assert 'content/fonts/rav4_adventure_mid_10.png' in out.namelist()
            assert PREFIX + 'sfx/rav4_drift.bank' in out.namelist()
            for filename in MODELS:
                assert out.read(PREFIX + filename) == normal.read(NORMAL_PREFIX + filename)
        digest = sha(full.read_bytes())
        (ART / (full.name + '.sha256')).write_text(digest + '  ' + full.name + '\n')
        result = {'release': '1.0.3', 'outputs': [{'file': full.name, 'bytes': full.stat().st_size,
                  'sha256': digest}], 'status': 'passed_offline_checks', 'runtime_tested': False,
                  'all_four_models_byte_identical_to_normal_rav4': True,
                  'changed_members': sorted(replacements)}
        (ART / 'release_drift_103_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
        (ROOT / 'rav4-drift-normal-tyres-103.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
