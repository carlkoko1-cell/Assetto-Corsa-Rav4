"""Separate Rav4 Drift, based on the matte-badge RAV4 and supplied Supra.

Donor data decoded using inspected MIT-licensed philippkosarev/acd.py.
Only model fit (wheelbase and graphics offsets) differs from donor physics.
"""
import copy,hashlib,json,math,re,shutil
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import numpy as np
from kn5 import Kn5,world_vertices
from build_visual_revision import bounds
from finish_revision_13 import write_ini
from validate_revision_08 import parse_ini,check_model,check_configuration

ROOT=Path('/workspace/Assetto-Corsa-Rav4');ART=ROOT/'artifacts';WORK=Path('/workspace/scratch/rav4_drift')
SOURCE=ROOT/'content/cars/toyota_rav4_adventure_blueflame_x5m';TARGET=ROOT/'content/cars/rav4_drift'
DONOR=WORK/'donor/toyota_supra_a90_drift_games';DONOR_ID=DONOR.name
MODELS=('x5.kn5','x5_lod_b.kn5','x5_lod_c.kn5','x5_lod_d.kn5')
VISUAL={'ambient_shadows.ini','analog_instruments.ini','blurred_objects.ini','cameras.ini','dash_cam.ini','digital_instruments.ini','driver3d.ini','extra_animations.ini','lights.ini','lods.ini','mirrors.ini','proview_nodes.ini','suspension_graphics.ini','flames.ini','wing_animations.ini'}


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def readini(path):return parse_ini('\n'.join(line for line in path.read_text(encoding='utf-8-sig').splitlines() if not line.lstrip().startswith('//')))

def write_native_ini(path,config):
    path.write_bytes(''.join('['+section+']\r\n'+''.join(key+'='+str(value)+'\r\n' for key,value in values.items())+'\r\n' for section,values in config.items()).encode('utf-8'))


def model_fit(k,tyres):
    wheel_changes={}
    for n,w in k.nodes():
        if n['kind']!=1 or not n['name'].startswith(('WHEEL_','SUSP_')):continue
        side=n['name'].split('_',1)[1]
        if side not in ('LF','RF','LR','RR'):continue
        front=side[1]=='F';section=tyres['FRONT' if front else 'REAR']
        # Measure the actual original tire, not the rim or rotor bounding box.
        wheel=next(a for a,m in k.nodes() if a['name']=='WHEEL_'+side)
        tireparts=[a for a in wheel['children'] if a['kind']==2 and ('TYRE' in a['name'] or 'Tires' in a['name'])]
        if not hasattr(model_fit,'sizes'):model_fit.sizes={}
        key=side
        if key not in model_fit.sizes:
            points=np.concatenate([a['vertices'][:,:3] for a in tireparts]);radius=float(np.linalg.norm(points[:,1:3],axis=1).max());width=float(np.ptp(points[:,0]))
            model_fit.sizes[key]=(radius,width)
        radius,width=model_fit.sizes[key]
        scale=np.array([float(section['WIDTH'])/width,float(section['RADIUS'])/radius,float(section['RADIUS'])/radius])
        parts=[]
        for a,m in k.nodes(n,np.eye(4)):
            if a['kind']!=2:continue
            assert all(c['kind']==2 for c in n['children']),'Unexpected nested wheel geometry'
            a['vertices'][:,:3]*=scale
            normals=a['vertices'][:,3:6].astype(float)/scale;normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12);a['vertices'][:,3:6]=normals
            tangents=a['vertices'][:,8:11].astype(float)*scale;tangents-=np.sum(tangents*normals,axis=1)[:,None]*normals
            good=np.linalg.norm(tangents,axis=1)>1e-8;tangents[good]/=np.linalg.norm(tangents[good],axis=1)[:,None];a['vertices'][:,8:11]=np.round(tangents,5)
            bounds(a);parts.append(a['name'])
        wheel_changes[n['name']]={'scale_xyz':scale.tolist(),'target_tyre_radius_m':float(section['RADIUS']),'target_tyre_width_m':float(section['WIDTH']),'meshes':parts}
    return wheel_changes


def main():
    baseline=ART/'Toyota_RAV4_Blue_Flame_CARL_Matte_Badge_0.16.zip';manifest=json.loads((ART/'release_16_manifest.json').read_text());assert digest(baseline)==manifest['sha256']
    # Start from a clean staging tree containing only the new car ID.
    if TARGET.exists():shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True)
    fonts={}
    oldprefix=SOURCE.relative_to(ROOT).as_posix()+'/'
    with ZipFile(baseline) as z:
        for name in z.namelist():
            if name.startswith('content/fonts/'):fonts[name]=z.read(name);continue
            if not name.startswith(oldprefix):continue
            rel=name[len(oldprefix):]
            if rel.startswith(('data/','sfx/')) or rel=='data.acd':continue
            if rel.startswith(('INTERIOR_BUILD_REPORT_','MATTE_BADGE_','SCREEN_BRIGHTNESS_')) or rel in ('VALIDATION_REPORT.json','INSTALL_MANIFEST.json','INSTALL_README.txt','VISUAL_REVISION_NOTES.md'):continue
            p=TARGET/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
    data=TARGET/'data';data.mkdir()
    for p in (DONOR/'data').iterdir():
        if p.is_file() and p.name not in VISUAL:shutil.copy2(p,data/p.name)
    for name in VISUAL:
        if (SOURCE/'data'/name).is_file():shutil.copy2(SOURCE/'data'/name,data/name)
    donor_car=readini(DONOR/'data/car.ini');car=copy.deepcopy(donor_car);rav4_car=readini(SOURCE/'data/car.ini')
    car['INFO']={'SCREEN_NAME':'Rav4 Drift','SHORT_NAME':'Rav4 Drift'}
    car['GRAPHICS']=copy.deepcopy(rav4_car['GRAPHICS'])
    car['_EXTENSION']=copy.deepcopy(rav4_car['_EXTENSION'])
    source_model=Kn5(SOURCE/'x5.kn5');roots={n['name']:w[3,:3] for n,w in source_model.nodes() if n['kind']==1}
    front=roots['WHEEL_LF'];rear=roots['WHEEL_LR'];wheelbase=float(front[2]-rear[2])
    susp=readini(DONOR/'data/suspensions.ini');original_susp=copy.deepcopy(susp);susp['BASIC']['WHEELBASE']=f'{wheelbase:.9f}'
    cg=float(susp['BASIC']['CG_LOCATION']);z_offset=wheelbase*(1-cg)-float(front[2]);y_offset=-float(susp['FRONT']['BASEY'])-float((front[1]+rear[1])/2)
    car['BASIC']['GRAPHICS_OFFSET']=f'0, {y_offset:.9f}, {z_offset:.9f}'
    car['BASIC']['GRAPHICS_PITCH_ROTATION']=rav4_car['BASIC']['GRAPHICS_PITCH_ROTATION']
    for side in ('LF','RF','LR','RR'):
        sign=1 if side[0]=='L' else -1;axle='FRONT' if side[1]=='F' else 'REAR'
        offset=float(roots['WHEEL_'+side][0])-sign*float(susp[axle]['TRACK'])/2
        for prefix in ('WHEEL_','SUSP_'):susp['GRAPHICS_OFFSETS'][prefix+side]=f'{offset:.9f}'
    write_native_ini(data/'car.ini',car);write_native_ini(data/'suspensions.ini',susp)
    # Keep every other engine/drivetrain/tyre/aero/brake/setup/AI/LUT/script byte.
    report={'release':'Rav4 Drift 1.0','status':'passed_offline_checks','errors':[],'assetto_corsa_runtime_tested':False,'donor':'Drift Games Toyota A90 Supra-Jet by Klein Eid','donor_archive_sha256':digest(WORK/'supra.rar'),'source_badge_archive_sha256':digest(baseline),'exact_donor_data_files':{},'models':{}}
    for p in (DONOR/'data').iterdir():
        if p.name in VISUAL or p.name in ('car.ini','suspensions.ini'):continue
        assert (data/p.name).read_bytes()==p.read_bytes();report['exact_donor_data_files'][p.name]=digest(p)
    a=copy.deepcopy(car);b=copy.deepcopy(donor_car)
    for obj in (a,b):
        obj.pop('INFO',None);obj.pop('GRAPHICS',None);obj.pop('_EXTENSION',None)
        for key in ('GRAPHICS_OFFSET','GRAPHICS_PITCH_ROTATION'):obj['BASIC'].pop(key,None)
    assert a==b,'Physical car values must be Supra values'
    a=copy.deepcopy(susp);b=copy.deepcopy(original_susp)
    for obj in (a,b):obj['BASIC'].pop('WHEELBASE');obj.pop('GRAPHICS_OFFSETS',None)
    assert a==b,'Only wheelbase and visual offsets may differ from Supra suspension'
    tyres=readini(data/'tyres.ini')
    for file in MODELS:
        model_fit.sizes={};k=Kn5(TARGET/file);old=Kn5(TARGET/file);changes=model_fit(k,tyres)
        # The sizing cache must come from original tires even when SUSP nodes
        # are visited before their matching WHEEL node.
        k.save(TARGET/file)
        changed={name for r in changes.values() for name in r['meshes']}
        before={n['name']:n for n,w in old.nodes()};after={n['name']:n for n,w in k.nodes()}
        for name,n in before.items():
            a=after[name]
            if n['kind']==1:assert np.array_equal(n['matrix'],a['matrix']),name
            elif name not in changed:assert np.array_equal(n['vertices'],a['vertices']) and np.array_equal(n['indices'],a['indices']),name
            else:assert np.array_equal(n['indices'],a['indices']) and np.array_equal(n['vertices'][:,6:8],a['vertices'][:,6:8]),name
        assert k.materials==old.materials and k.textures==old.textures
        checked,names,checks=check_model(TARGET/file);check_configuration(TARGET,names,checked)
        report['models'][file]={'sha256':digest(TARGET/file),'wheel_size_adaptation':changes,'all_body_cabin_badge_glass_mirror_meshes_and_materials_unchanged':True,'structural_checks':checks}
        print(file,'drift visual wheel fit checked',flush=True)
    # New car identity and FMOD GUID paths; preserve bank contents exactly.
    (TARGET/'sfx').mkdir();bank=TARGET/'sfx/rav4_drift.bank';shutil.copy2(DONOR/'sfx'/(DONOR_ID+'.bank'),bank)
    guid=(DONOR/'sfx/GUIDs.txt').read_text().replace(DONOR_ID,'rav4_drift');(TARGET/'sfx/GUIDs.txt').write_text(guid)
    assert digest(bank)==digest(DONOR/'sfx'/(DONOR_ID+'.bank'))
    assert 'event:/cars/rav4_drift/engine_int' in guid and 'bank:/rav4_drift' in guid and DONOR_ID not in guid
    assert len(list((TARGET/'sfx').glob('*.bank')))==1
    cfg=readini(TARGET/'extension/ext_config.ini');cfg['EXTRA_SWITCHES']={'SWITCH_F':'Supra anti-lag'}
    fuel_sections=sorted([name for name in cfg if name.startswith('EMISSIVE_FUEL_SEGMENT_')],key=lambda name:int(name.rsplit('_',1)[1]))
    for i,name in enumerate(fuel_sections):cfg[name]['INPUT_THRESHOLD']=str(float(car['FUEL']['MAX_FUEL'])*(i+.5)/len(fuel_sections))
    write_ini(TARGET/'extension/ext_config.ini',cfg)
    # Ensure complete lookup dependencies. The donor's unused COAST_CURVE
    # filename and legacy WAV declarations do not select active LUTs.
    for p in data.glob('*.ini'):
        for section,values in readini(p).items():
            for key,value in values.items():
                if p.name=='engine.ini' and section=='COAST_CURVE' and readini(data/'engine.ini')['HEADER']['COAST_CURVE']!='FROM_COAST_LUT':continue
                if value.lower().endswith(('.lut','.rto')) and not value.startswith('('):assert (data/value).is_file(),(p.name,section,key,value)
    # Native driver animation lock already matches the donor's 450-degree control.
    assert readini(data/'driver3d.ini')['STEER_ANIMATION']['LOCK']==car['CONTROLS']['STEER_LOCK']
    assert readini(data/'drivetrain.ini')['TRACTION']['TYPE']=='RWD' and readini(data/'drivetrain.ini')['GEARS']['COUNT']=='6'
    assert (data/'script.lua').read_bytes()==(DONOR/'data/script.lua').read_bytes()
    assert not (TARGET/'data.acd').exists()
    assert set(p.name for p in data.iterdir())==((set(p.name for p in (DONOR/'data').iterdir())-VISUAL)|{n for n in VISUAL if (SOURCE/'data'/n).is_file()})
    for p in data.glob('*'):assert b'ACI' not in p.read_bytes() or p.suffix not in ('.lua',),p
    ui=json.loads((DONOR/'ui/ui_car.json').read_text());ui.update(name='Rav4 Drift',brand='Toyota',year=2019,version='1.0 - Supra drift conversion',author='RAV4 visual conversion; Supra donor by Klein Eid',**{'class':'drift'})
    ui['description']='RAV4 Adventure Blue Flame / black-orange interior / matte black rear Toyota emblem, with driving systems from the user-supplied Drift Games Toyota A90 Supra-Jet. Supra engine/turbos, RWD six-speed manual, locked differential, clutch, brakes, drift tyres/thermal curves, suspension tuning, mass/inertia, aero, AI, setup, anti-lag script and sound. Wheelbase and graphical wheel/body offsets fitted to the RAV4 shell; visual wheel sizes matched to donor tyre dimensions. Existing 0.15.1 screen brightness, Android Auto, native MID, direct RPM controller, mirror fixes, matte wheel pockets and paint-shop controls retained. Requires CSP; Extra F is donor anti-lag. Factory 8000-RPM gauge saturates above its scale; donor limiter is 8400. Structural/transfer checks only; no in-game drift test.'
    ui['tags']=['Toyota','RAV4','drift','RWD','turbo','six-speed manual','Supra physics','Blue Flame'];ui['specs']['weight']=car['BASIC']['TOTALMASS']+' kg';ui['specs']['pwratio']='1.63 kg/hp'
    (TARGET/'ui/ui_car.json').write_text(json.dumps(ui,indent=2)+'\n')
    report['physical_adaptations']={'donor_wheelbase_m':float(original_susp['BASIC']['WHEELBASE']),'rav4_model_wheelbase_m':wheelbase,'donor_tracks_m':{a:float(susp[a]['TRACK']) for a in ('FRONT','REAR')},'graphics_offset_m':[0,y_offset,z_offset],'physical_mass_kg':float(car['BASIC']['TOTALMASS']),'CG_LOCATION':cg,'all_other_donor_car_and_suspension_physics_values_unchanged':True,'rear_badge':'matte black retained from 0.16','tyre_physics':'donor data exact; visual wheel geometry resized to match'}
    report['sound']={'bank_sha256':digest(bank),'original_bank_bytes_preserved':True,'GUID_paths_remapped_to':'rav4_drift','BMW_bank_removed':True}
    notes='''Rav4 Drift 1.0 — separate car ID: rav4_drift

Install this complete ZIP through Content Manager, including the instrument
font. It appears as Rav4 Drift and can be installed alongside the BMW-powered
RAV4 Adventure matte-badge edition. No BMW engine/handling files are used.

Donor: user-supplied Drift Games Toyota A90 Supra-Jet by Klein Eid. The source
archive was downloaded from the repository release named drift. Engine,
turbos/boost control, RWD six-speed manual drivetrain and locked differential,
clutch, brakes, drift tyre model and thermal/wear curves, suspension tune,
mass/inertia, aero, setup, AI, physics anti-lag script and sound are copied.
The donor UI rates its engine at 800 hp. Physics mass is 1304 kg with driver.

The RAV4 body requires a 2.99016 m wheelbase instead of the Supra's 2.470 m.
Only that suspension dimension and visual mount offsets are adapted. Donor
tracks, geometry relative to hubs, camber, springs, dampers and ARBs remain.
Wheel/rim/rotor/caliper geometry is resized to match donor tyre size, retaining
the matte wheel materials. The RAV4 body collider, interior, cameras, driver
animation, gauges, mirror/lighting setup and paint shop are retained.

Use a six-speed manual shifter or paddles with the appropriate clutch assists.
Extra F controls the supplied Supra anti-lag behavior. The factory RPM face
ends at 8000, so its needle pegs there above that speed; donor limiter is 8400.
The engine/handling have not been detuned to the RAV4's factory specifications.

All donor data/LUT dependencies, FMOD GUID remapping, removed BMW data, wheel
fit, model structure and archive members are checked offline. Assetto Corsa,
Pure and CSP do not run in this Linux workspace. Driving balance, sound
playback, real tire contact, dynamic suspension/steering clearance and online
compatibility still need an in-game test. This is a donor-based conversion,
not a telemetry-validated match of the original Supra chassis.
'''
    for name in ('INSTALL_README.txt','VISUAL_REVISION_NOTES.md'):(TARGET/name).write_text(notes)
    (TARGET/'DRIFT_DONOR_CREDITS.txt').write_text('Driving systems and sound: Drift Games Toyota A90 Supra-Jet, mod by Klein Eid. Original donor skin by civichbdx (not used). Donor source: https://github.com/carlkoko1-cell/Assetto-Corsa-Rav4/releases/tag/drift\nRAV4 body/cabin/font source and license notes are retained in the accompanying files. No donor 3D body, cabin, skins or driver animation is copied.\nACD file format decoding: philippkosarev/acd.py, MIT, used as a local build tool.\n')
    (TARGET/'INSTALL_MANIFEST.json').write_text(json.dumps({'release':'Rav4 Drift 1.0','car_id':'rav4_drift','display_name':'Rav4 Drift','base_visuals':'RAV4 matte badge 0.16 / screen hotfix 0.15.1','driving_systems_donor':DONOR_ID,'physics_files':'unpacked data folder, no data.acd','shared_font':'rav4_adventure_mid_10','runtime_tested':False},indent=2)+'\n')
    (TARGET/'VALIDATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'rav4-drift-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    out=ART/'Rav4_Drift_1.0.zip'
    with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(TARGET.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
        for name,b in fonts.items():z.writestr(name,b)
    with ZipFile(out) as z:
        assert z.testzip() is None;names=z.namelist();assert len(names)==len(set(n.lower() for n in names))
        assert all(n.startswith('content/cars/rav4_drift/') or n in fonts for n in names)
        for p in TARGET.rglob('*'):
            if p.is_file():assert z.read(p.relative_to(ROOT).as_posix())==p.read_bytes(),p
    sha=digest(out);(ART/(out.name+'.sha256')).write_text(sha+'  '+out.name+'\n')
    manifest={'file':out.name,'sha256':sha,'bytes':out.stat().st_size,'files':len(names),'car_id':'rav4_drift','zip_crc':'passed','runtime_tested':False,'donor_archive_sha256':report['donor_archive_sha256']};(ART/'release_drift_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
