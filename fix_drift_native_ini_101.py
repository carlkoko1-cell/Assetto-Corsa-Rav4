"""Fix strict native-INI formatting without changing Rav4 Drift tuning.

The earlier ConfigParser check trimmed key whitespace and could not reproduce
AC's missing TYPE error. Preserve donor suspension syntax and check exact keys.
"""
import hashlib,json,re
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import sys
from build_rav4_drift import readini,write_ini

ROOT=Path('/workspace/Assetto-Corsa-Rav4');ART=ROOT/'artifacts';CAR=ROOT/'content/cars/rav4_drift';WORK=Path('/workspace/scratch/rav4_drift')
DONOR=WORK/'donor/toyota_supra_a90_drift_games/data';PREFIX=CAR.relative_to(ROOT).as_posix()+'/'
SOURCE=ART/'Rav4_Drift_1.0.zip';SOURCE_SHA='e730374e128d0b744250900ba9845375b74b8f05745ed01c11d8dec8acdd5beb'


def strict_view(data):
    """Exact key names, unlike ConfigParser; used as a compatibility check.

    This is a deliberately strict approximation, not the proprietary AC parser.
    """
    result={};section=None
    for line in data.decode('utf-8-sig').splitlines():
        if line.startswith('[') and ']' in line:section=line[1:line.index(']')];result.setdefault(section,{})
        elif section and '=' in line:
            key,value=line.split('=',1);result[section][key]=value.split(';',1)[0].rstrip()
    return result


def native_bytes(config):
    return ''.join('['+section+']\r\n'+''.join(key+'='+str(value)+'\r\n' for key,value in values.items())+'\r\n' for section,values in config.items()).encode('utf-8')


def patch_donor_suspension(donor,values):
    replacements={('BASIC','WHEELBASE'):values['BASIC']['WHEELBASE']}
    replacements.update({('GRAPHICS_OFFSETS',k):v for k,v in values['GRAPHICS_OFFSETS'].items()})
    section=None;out=[];seen=set()
    for line in donor.decode('utf-8-sig').splitlines(keepends=True):
        if line.startswith('['):section=line[1:line.index(']')]
        if '=' in line:
            key,value=line.split('=',1);entry=(section,key)
            if entry in replacements:
                # Original tabs, comments, line endings and TYPE lines survive.
                raw=value.rstrip('\r\n');tail=raw[len(raw.rstrip()):]
                if ';' in raw:
                    before,comment=raw.split(';',1);tail=before[len(before.rstrip()):]+';'+comment
                ending='\r\n' if line.endswith('\r\n') else '\n'
                line=key+'='+str(replacements[entry])+tail+ending;seen.add(entry)
        out.append(line)
    assert seen==set(replacements)
    return ''.join(out).encode('utf-8')


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    with ZipFile(SOURCE) as source:
        old_susp=source.read(PREFIX+'data/suspensions.ini');old_car=source.read(PREFIX+'data/car.ini')
        assert 'TYPE' not in strict_view(old_susp)['FRONT']
        assert strict_view(old_susp)['FRONT']['TYPE ']==' STRUT'
        # Keep every effective physics value from 1.0, changing formatting only.
        new_car=native_bytes(readini(CAR/'data/car.ini'))
        expected_susp=readini(CAR/'data/suspensions.ini')
        new_susp=patch_donor_suspension((DONOR/'suspensions.ini').read_bytes(),expected_susp)
        (CAR/'data/car.ini').write_bytes(new_car);(CAR/'data/suspensions.ini').write_bytes(new_susp)
        assert readini(CAR/'data/suspensions.ini')==expected_susp
        from validate_revision_08 import parse_ini
        assert parse_ini(new_car.decode())==parse_ini(old_car.decode())
        for file,before,after in [('car.ini',old_car,new_car),('suspensions.ini',old_susp,new_susp)]:
            parsed=strict_view(after)
            assert all(key==key.strip() and value==value.lstrip() for entries in parsed.values() for key,value in entries.items()),file
            assert parse_ini(before.decode())==parse_ini(after.decode()),file
        exact=strict_view(new_susp)
        assert exact['FRONT']['TYPE']=='STRUT' and exact['REAR']['TYPE']=='DWB'
        for axle in ('FRONT','REAR'):
            for key in ('BASEY','TRACK','ROD_LENGTH','HUB_MASS','SPRING_RATE','DAMP_BUMP','DAMP_REBOUND'):float(exact[axle][key])
            vectors=('STRUT_CAR','STRUT_TYRE','WBCAR_BOTTOM_FRONT','WBCAR_BOTTOM_REAR','WBTYRE_BOTTOM','WBCAR_STEER','WBTYRE_STEER') if axle=='FRONT' else ('WBCAR_TOP_FRONT','WBCAR_TOP_REAR','WBCAR_BOTTOM_FRONT','WBCAR_BOTTOM_REAR','WBTYRE_TOP','WBTYRE_BOTTOM','WBCAR_STEER','WBTYRE_STEER')
            for key in vectors:assert len([float(v) for v in exact[axle][key].split(',')])==3
        exact_car=strict_view(new_car)
        assert exact_car['HEADER']['VERSION']=='extended-2' and float(exact_car['BASIC']['TOTALMASS'])==1304
        assert float(exact_car['CONTROLS']['STEER_LOCK'])==450
        # Identical TYPE syntax to the original packed donor, not just a trim.
        donor_types=[line for line in (DONOR/'suspensions.ini').read_bytes().splitlines() if line.startswith(b'TYPE=')]
        assert [line for line in new_susp.splitlines() if line.startswith(b'TYPE=')]==donor_types
        report={'release':'Rav4 Drift 1.0.1 native INI launch fix','status':'passed_offline_checks','errors':[],'assetto_corsa_runtime_tested':False,'source_archive_sha256':SOURCE_SHA,'reported_error':'Cannot create suspension type: for wheel:0','regression_reproduced_under_exact_key_lookup':True,'front_TYPE_exact':'STRUT','rear_TYPE_exact':'DWB','donor_TYPE_lines_byte_identical':True,'car_and_suspension_effective_values_unchanged':True,'native_car_and_suspension_keys_no_spaces_around_equals':True,'all_required_front_STRUT_and_rear_DWB_geometry_vectors_present':True,'limitation':'Exact-key check is a compatibility regression check; Assetto Corsa runtime unavailable.'}
        ui=json.loads(source.read(PREFIX+'ui/ui_car.json'));ui['version']='1.0.1 - Native suspension/car INI launch fix';ui['description']='1.0.1: restore native suspension TYPE/key formatting and car.ini formatting to address the wheel:0 suspension initialization error; driving values unchanged. '+ui['description']
        notes='''Rav4 Drift 1.0.1 — native INI launch fix

Addresses: ERROR: Cannot create suspension type: for wheel:0.
The 1.0 build rewrote car.ini and suspensions.ini using spaces around equals.
This fix restores exact native KEY=VALUE names, preserving donor suspension
comments/CRLF and TYPE lines. Physics/tuning values are unchanged.

SMALL PATCH, requires Rav4 Drift 1.0 already installed:
Close AC. Extract into the Assetto Corsa folder containing acs.exe, merging
content/cars/rav4_drift and allowing overwrites. Start a new session.

COMPLETE ZIP: close AC, install all car/font entries through Content Manager,
then start a new session. Car name stays Rav4 Drift, car ID rav4_drift.
The separate BMW-powered matte-badge RAV4 is unchanged.

The original failure is reproduced by an exact-key compatibility check; the
corrected TYPE values and STRUT/DWB geometry keys resolve without trimming.
All effective car/suspension values match 1.0, including the adapted RAV4
wheelbase. Other data/models/audio/controller files are byte-preserved.
Assetto Corsa is unavailable here; a successful in-game launch is unverified.
'''
        replacements={PREFIX+'data/car.ini':new_car,PREFIX+'data/suspensions.ini':new_susp,PREFIX+'ui/ui_car.json':(json.dumps(ui,indent=2)+'\n').encode(),PREFIX+'LAUNCH_FIX_101_REPORT.json':(json.dumps(report,indent=2)+'\n').encode()}
        manifest=json.loads(source.read(PREFIX+'INSTALL_MANIFEST.json'));manifest['release']='Rav4 Drift 1.0.1 native INI launch fix';replacements[PREFIX+'INSTALL_MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
        old_validation=json.loads(source.read(PREFIX+'VALIDATION_REPORT.json'));old_validation['release']='Rav4 Drift 1.0.1';old_validation['native_ini_launch_fix']=report;replacements[PREFIX+'VALIDATION_REPORT.json']=(json.dumps(old_validation,indent=2)+'\n').encode()
        replacements[PREFIX+'INSTALL_README.txt']=notes.encode()
        replacements[PREFIX+'VISUAL_REVISION_NOTES.md']=(notes+'\n--- Previous conversion notes ---\n'+source.read(PREFIX+'VISUAL_REVISION_NOTES.md').decode()).encode()
        for name,data in replacements.items():(ROOT/name).write_bytes(data)
        full=ART/'Rav4_Drift_1.0.1.zip'
        with ZipFile(full,'w',ZIP_DEFLATED,compresslevel=9) as out:
            for item in source.infolist():out.writestr(item.filename,replacements.get(item.filename,source.read(item)))
            for name,data in replacements.items():
                if name not in source.namelist():out.writestr(name,data)
        with ZipFile(full) as out:
            assert out.testzip() is None;preserved=0
            for name in source.namelist():
                if name not in replacements:assert out.read(name)==source.read(name),name;preserved+=1
            assert len(out.namelist())==len(set(n.lower() for n in out.namelist()))
        patch=ART/'Rav4_Drift_1.0.1_Launch_Fix_Patch.zip'
        with ZipFile(patch,'w',ZIP_DEFLATED,compresslevel=9) as out:
            for name,data in replacements.items():out.writestr(name,data)
        with ZipFile(patch) as out:
            assert out.testzip() is None
            for name in out.namelist():assert out.read(name)==replacements[name]
        outputs=[]
        for file in (full,patch):
            digest=hashlib.sha256(file.read_bytes()).hexdigest();(ART/(file.name+'.sha256')).write_text(digest+'  '+file.name+'\n');outputs.append({'file':file.name,'bytes':file.stat().st_size,'sha256':digest})
        report['unchanged_archive_members']=preserved
        (ROOT/'rav4-drift-launch-fix-101.json').write_text(json.dumps(report,indent=2)+'\n')
        (ART/'release_drift_101_manifest.json').write_text(json.dumps({'release':'1.0.1','outputs':outputs,'unchanged_baseline_members':preserved,'status':'passed_offline_checks','runtime_tested':False},indent=2)+'\n')
        print(json.dumps({'outputs':outputs,'regression_checks':report},indent=2))

if __name__=='__main__':main()
