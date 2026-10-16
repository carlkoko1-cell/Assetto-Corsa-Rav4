"""Brightness-only hotfix built from the verified 0.15 ZIP.

Keep all models, materials, RPM logic, mirrors, paint, physics and audio intact.
"""
import hashlib,json,sys
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path('/workspace/Assetto-Corsa-Rav4');ART=ROOT/'artifacts'
CAR=ROOT/'content/cars/toyota_rav4_adventure_blueflame_x5m'
PREFIX=CAR.relative_to(ROOT).as_posix()+'/'
BASE=ART/'Toyota_RAV4_Blue_Flame_CARL_Interior_0.15.zip'
BASE_SHA='0d76bd7b2713d4d53ea959671f648dd1f0fba9bfc76fe01619c6c3aef29cbd77'
VERSION='0.15.1'
DAY=2.4;NIGHT=1.6


def sha(data):return hashlib.sha256(data).hexdigest()


def run_lua(source):
    sys.path.insert(0,'/workspace/scratch/lua-test-deps')
    from lupa import LuaRuntime
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.execute('''
      script={}; car={rpm=0,headlightsActive=false}; angles={}; values={}
      function vec3(x,y,z) return {x=x,y=y,z=z} end
      function rgb(r,g,b) return {r=r,g=g,b=b} end
      local pointer={setRotation=function(self,axis,angle)
        assert(axis.x==0 and axis.y==0 and axis.z==1);angles[#angles+1]=angle
      end}
      local screen={setMaterialProperty=function(self,key,value)
        assert(key=='ksEmissive' and value.r==value.g and value.g==value.b)
        values[#values+1]=value.r
      end}
      ac={findNodes=function(name) assert(name=='RAV4_RPM_LIVE');return pointer end,
          findMeshes=function(name) assert(name=='RAV4_ENTUNE_SCREEN');return screen end}
    ''')
    lua.execute(source);g=lua.globals();profiles=[]
    for fps in (20,60,144):
        for lights,rpm in ((False,0),(True,3000),(False,6500),(True,800),(False,8000)):
            g.car.headlightsActive=lights;g.car.rpm=rpm
            for _ in range(fps*4):g.script.update(1/fps)
            profiles.append({'fps':fps,'headlights':lights,'rpm':rpm,'emission':float(g['values'][len(g['values'])]),'angle_rad':float(g.angles[len(g.angles)])})
    return [float(g.angles[i]) for i in range(1,len(g.angles)+1)],profiles,[float(g['values'][i]) for i in range(1,len(g['values'])+1)]


def main():
    assert sha(BASE.read_bytes())==BASE_SHA
    with ZipFile(BASE) as source:
        old_lua=source.read(PREFIX+'extension/rav4_instruments.lua').decode()
        old_cfg=source.read(PREFIX+'extension/ext_config.ini').decode()
        lua=old_lua
        for a,b in [('local brightness = 0.65','local brightness = 2.4'),('local emission = rgb(0.65, 0.65, 0.65)','local emission = rgb(2.4, 2.4, 2.4)'),('local target = car.headlightsActive and 0.10 or 0.65','local target = car.headlightsActive and 1.6 or 2.4')]:
            assert lua.count(a)==1;lua=lua.replace(a,b)
        assert old_cfg.count('PROP_5 = ksEmissive, .65, .65, .65')==1
        cfg=old_cfg.replace('PROP_5 = ksEmissive, .65, .65, .65','PROP_5 = ksEmissive, 2.4, 2.4, 2.4')
        # Execute both complete scripts over the same telemetry/light trace.
        old_angles,old_profile,_=run_lua(old_lua);angles,profile,values=run_lua(lua)
        assert angles==old_angles,'RPM response changed'
        assert all(NIGHT-1e-9<=v<=DAY+1e-9 for v in values)
        for p in profile:assert abs(p['emission']-(NIGHT if p['headlights'] else DAY))<2e-8
        for a,b in zip(old_profile,profile):assert b['emission']>a['emission']*3
        ui=json.loads(source.read(PREFIX+'ui/ui_car.json'))
        ui['name']=ui['name'].replace('Interior 0.15,','Interior 0.15.1,');ui['version']='0.15.1 - Infotainment brightness hotfix'
        ui['description']='0.15.1 brightness-only hotfix: higher infotainment backlight and gentler headlight dimming. All 0.15 model geometry, mirror aim, direct RPM logic, paint/shop, wheels, doors, grille lighting and drivetrain/audio are retained. '+ui['description']
        base_url='https://raw.githubusercontent.com/carlkoko1-cell/Assetto-Corsa-Rav4/rav4-interior-v0.15.1-download/'
        notes=f'''RAV4 Adventure Blue Flame CARL — 0.15.1 SCREEN BRIGHTNESS HOTFIX

The 0.15 screen was too dark, especially with headlights on. The daytime
emission increases from 0.65 to {DAY}; headlights-on emission increases from
0.10 to {NIGHT}. Headlights now reduce the backlight by one-third instead of
about 85%. The opaque screen shader is retained to avoid reintroducing the
reflective white layer. Android Auto and all other 0.15 behavior are retained.

SMALL PATCH (requires the installed 0.15 car): close AC, extract the ZIP into
the main Assetto Corsa folder containing acs.exe, and allow file overwrites.
The included content folder must merge with the game's content folder.
Start a fresh session. The patch does not replace your skins or any KN5/data.

COMPLETE ZIP: close AC, drag the complete ZIP into Content Manager, install
all detected car/font entries, then start a fresh session.

Both controller scripts were executed with mocked CSP APIs at 20/60/144 Hz.
The new brightness converges to the intended day/night settings and the RPM
rotation trace is exactly unchanged. Every unchanged ZIP member is compared
byte for byte with the checksum-verified 0.15 package. AC/Pure/CSP cannot run
in this workspace, so the exact perceived screen luminance is untested here.

Complete ZIP: {base_url}Toyota_RAV4_Blue_Flame_CARL_Interior_0.15.1.zip
Small patch: {base_url}Toyota_RAV4_Screen_Brightness_0.15.1_Patch.zip
'''
        manifest=json.loads(source.read(PREFIX+'INSTALL_MANIFEST.json'));manifest.update(release='0.15.1 infotainment brightness hotfix',screen_day_emission=DAY,screen_headlights_on_emission=NIGHT)
        changes={'extension/rav4_instruments.lua':lua.encode(),'extension/ext_config.ini':cfg.encode(),'ui/ui_car.json':(json.dumps(ui,indent=2)+'\n').encode(),'SCREEN_BRIGHTNESS_HOTFIX.txt':notes.encode(),'INSTALL_README.txt':notes.encode(),'INSTALL_MANIFEST.json':(json.dumps(manifest,indent=2)+'\n').encode()}
        # Keep the baseline engineering notes with an explicit current addendum.
        prior=source.read(PREFIX+'VISUAL_REVISION_NOTES.md').decode()
        changes['VISUAL_REVISION_NOTES.md']=(notes+'\n\n--- BASELINE 0.15 NOTES (previous brightness values superseded above) ---\n\n'+prior).encode()
        baseline_report=json.loads(source.read(PREFIX+'VALIDATION_REPORT.json'))
        report={'release':VERSION,'status':'passed_offline_checks','errors':[],'assetto_corsa_runtime_tested':False,'baseline_015_archive_sha256':BASE_SHA,'baseline_geometry_validation_status':baseline_report['status'],'scope':'Screen backlight values, release labels and documentation only','day_emission':DAY,'headlights_on_emission':NIGHT,'day_increase_multiplier':DAY/.65,'headlights_increase_multiplier':NIGHT/.10,'lua_script_sha256':sha(lua.encode()),'rpm_frame_trace_exactly_unchanged':True,'simulation_updates_compared':len(angles),'brightness_profiles':profile,'models_physics_audio_mirrors_paint_wheels_and_door_assets_unchanged':True,'baseline_user_feedback':'User reports all other 0.15 behavior is perfect','runtime_notes':'Pure/CSP luminance untested; mocked controller and archive checks only'}
        changes['VALIDATION_REPORT.json']=(json.dumps(report,indent=2)+'\n').encode()
        entries={PREFIX+k:v for k,v in changes.items()}
        # Reflect the changed files in the workspace too, without rebuilding models.
        for name,data in entries.items():
            path=ROOT/name;path.parent.mkdir(exist_ok=True,parents=True);path.write_bytes(data)
        full=ART/'Toyota_RAV4_Blue_Flame_CARL_Interior_0.15.1.zip'
        with ZipFile(full,'w',ZIP_DEFLATED,compresslevel=9) as out:
            for item in source.infolist():out.writestr(item.filename,entries.get(item.filename,source.read(item)))
            for name,data in entries.items():
                if name not in source.namelist():out.writestr(name,data)
        with ZipFile(full) as out:
            assert out.testzip() is None
            preserved=0
            for name in source.namelist():
                if name in entries:assert out.read(name)==entries[name]
                else:assert out.read(name)==source.read(name),name;preserved+=1
            assert len(out.namelist())==len(set(n.lower() for n in out.namelist()))
        patch=ART/'Toyota_RAV4_Screen_Brightness_0.15.1_Patch.zip'
        patch_names=['extension/rav4_instruments.lua','extension/ext_config.ini','ui/ui_car.json','SCREEN_BRIGHTNESS_HOTFIX.txt','VALIDATION_REPORT.json','INSTALL_README.txt','INSTALL_MANIFEST.json','VISUAL_REVISION_NOTES.md']
        with ZipFile(patch,'w',ZIP_DEFLATED,compresslevel=9) as out:
            for relative in patch_names:out.writestr(PREFIX+relative,changes[relative])
        with ZipFile(patch) as out:
            assert out.testzip() is None
            for name in out.namelist():assert out.read(name)==entries[name]
        outputs=[]
        for file in (full,patch):
            digest=sha(file.read_bytes());(ART/(file.name+'.sha256')).write_text(digest+'  '+file.name+'\n')
            outputs.append({'file':file.name,'bytes':file.stat().st_size,'sha256':digest})
        assert full.stat().st_size<100*1024*1024
        report['unchanged_baseline_archive_members']=preserved
        (ROOT/'validation-report-151.json').write_text(json.dumps(report,indent=2)+'\n')
        (ART/'release_151_manifest.json').write_text(json.dumps({'release':VERSION,'outputs':outputs,'runtime_tested':False,'unchanged_baseline_members':preserved,'all_unchanged_members_byte_identical':True,'zip_crc':'passed','changed_car_files':list(changes)},indent=2)+'\n')
        (ROOT/'README.md').write_text(notes)
        print(json.dumps({'outputs':outputs,'unchanged_baseline_members':preserved,'rpm_updates_compared':len(angles)},indent=2),flush=True)


if __name__=='__main__':main()
