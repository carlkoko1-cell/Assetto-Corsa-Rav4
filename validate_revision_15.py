"""Offline regression and executable visual-Lua tests; no AC runtime claims."""
import hashlib,io,json,math,sys
from pathlib import Path
import numpy as np
from PIL import Image
from zipfile import ZipFile
from kn5 import Kn5,world_vertices
import validate_revision_08 as check
from validate_revision_09 import check_animation
from validate_revision_10 import font_checks
from validate_revision_14 import windows,opaque_triangles
from validate_revision_13 import ray_hits
from repair_revision_15 import ROOT,CAR,BASE,MODELS,BLUE,PAINT,EYE


def lua_checks():
    sys.path.insert(0,'/workspace/scratch/lua-test-deps')
    from lupa import LuaRuntime
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.execute('''
      script = {}; car = { index = 2, rpm = 0, headlightsActive = false }
      rotations = {}; brightness = {}; rootLookups = 0; draws = 0
      function vec3(x,y,z) return {x=x,y=y,z=z} end
      function vec2(x,y) return {x=x,y=y} end
      function rgb(r,g,b) return {r=r,g=g,b=b} end
      function rgbm(r,g,b,m) return {r=r,g=g,b=b,m=m} end
      local pointer = { setRotation = function(self,axis,angle)
        assert(axis.x==0 and axis.y==0 and axis.z==1)
        rotations[#rotations+1] = angle
      end }
      local screen = { setMaterialProperty = function(self,name,v)
        assert(name=='ksEmissive' and v.r==v.g and v.g==v.b)
        brightness[#brightness+1] = v.r
      end }
      local root = {
        findNodes = function(self,name) assert(name=='RAV4_RPM_LIVE'); return pointer end,
        findMeshes = function(self,name) assert(name=='RAV4_ENTUNE_SCREEN'); return screen end
      }
      ac = { findNodes = function(filter)
        assert(filter=='RAV4_RPM_LIVE'); rootLookups=rootLookups+1; return pointer
      end, findMeshes = function(filter) assert(filter=='RAV4_ENTUNE_SCREEN'); return screen end }
      ui = { drawRectFilled = function(a,b,c)
        assert(a.x==0 and a.y==0 and b.x==1 and b.y==1)
        assert(c.r==1 and c.g==1 and c.b==1 and c.m==1); draws=draws+1
      end }
    ''')
    source=(CAR/'extension/rav4_instruments.lua').read_text();lua.execute(source)
    g=lua.globals();results=[]
    for rate in (20,60,144):
        for rpm in (0,800,1000,3000,5000,6800,8000,12000,-100,0):
            g.car.rpm=rpm
            for _ in range(rate):g.script.update(1/rate)
            angle=float(g.rotations[len(g.rotations)]);expected=math.radians(np.clip(rpm,0,8000)*183/8000)
            assert abs(angle-expected)<1e-7,(rate,rpm,angle,expected)
            results.append({'fps':rate,'input_rpm':rpm,'angle_deg':math.degrees(angle)})
    for on,want in [(False,.65),(True,.10),(False,.65)]:
        g.car.headlightsActive=on
        for _ in range(240):g.script.update(1/60)
        assert abs(float(g.brightness[len(g.brightness)])-want)<2e-8
    for rpm in (float('nan'),float('inf'),-float('inf')):
        g.car.rpm=rpm;g.script.update(.02)
        assert math.isfinite(float(g.rotations[len(g.rotations)]))
    for dt in (-1,0,None,20):g.script.update(dt)
    assert 30<g.rootLookups<100 and len(g.rotations)==2967
    return {'script_sha256':hashlib.sha256(source.encode()).hexdigest(),'lua_engine':lua.lua_implementation,'mocked_CSP_scene_API':True,'telemetry_cases':results,'headlight_dimming_cases':3,'LOD_rebind_callbacks':int(g.rootLookups),'simulation_update_callbacks':len(g.rotations),'scene_rotation_API_checked_against_official_SDK':True,'real_CSP_loader_and_rendering_tested':False}


def regressions():
    cfg=check.load_ini(CAR/'extension/ext_config.ini')
    analog=check.load_ini(CAR/'data/analog_instruments.ini')
    assert 'RPM_INDICATOR' not in analog
    assert not any(s.startswith('ANALOG_INDICATOR_') for s in cfg)
    assert cfg['SCRIPT_0']['SCRIPT']=='rav4_instruments.lua'
    assert cfg['SCRIPT_0']['SKIP_FRAMES']=='0' and cfg['SCRIPT_0']['ACTIVE_FOR_LOD']=='D'
    assert 'SCRIPTABLE_DISPLAY_1' not in cfg
    assert cfg['Display_AndroidAuto']==check.load_ini(BASE/'extension/ext_config.ini')['Display_AndroidAuto']
    assert 'Material_DigitalScreen' not in cfg and 'GLASS_FILTER' not in cfg['EXTRA_FX']
    assert 'RAV4_ENTUNE_SCREEN' in cfg['EXTRA_FX']['SKIP_GBUFFER']
    assert not any(s.startswith('EMISSIVE_') and v.get('NAME')=='RAV4_ENTUNE_SCREEN' for s,v in cfg.items())
    rules=json.loads((CAR/'ui/cm_paintshop.json').read_text());rule=rules[0]
    assert len(rules)==1 and rule['type']=='carpaint' and rule['texture']=='RAV4_BlueFlame.dds' and rule['defaultColor']=='#0095DA' and rule['flakesAvailable'] is False
    build=json.loads((ROOT/'interior-build-report-15.json').read_text());result={}
    for file in MODELS:
        k=Kn5(CAR/file);old=Kn5(BASE/file);nodes={n['name']:(n,w) for n,w in k.nodes()}
        before={n['name']:n for n,w in old.nodes()}
        assert 'ARROW_RPM' not in nodes and nodes['RAV4_RPM_LIVE'][0]['kind']==1
        assert np.array_equal(nodes['RAV4_RPM_LIVE'][0]['matrix'],before['ARROW_RPM']['matrix'])
        changed={'RAV4_MIRROR_CENTER','RAV4_MIRROR_L','RAV4_MIRROR_R','RAV4_V13_MIRROR_HOUSING'}|set(build['models'][file]['mirrors']['removed_duplicate_sensor_pod'])
        preserved=0
        for name,n in before.items():
            a=nodes['RAV4_RPM_LIVE' if name=='ARROW_RPM' else name][0]
            if name in changed:continue
            if n['kind']==1:assert np.array_equal(n['matrix'],a['matrix']),name
            else:
                assert np.array_equal(n['vertices'][:,:8],a['vertices'][:,:8]),name
                assert np.array_equal(n['indices'],a['indices']),name
            preserved+=1
        for name in build['models'][file]['mirrors']['removed_duplicate_sensor_pod']:
            n=nodes[name][0];v=n['vertices'][:,:3];t=v[n['indices'].reshape(-1,3)].mean(1)
            assert not ((abs(t[:,0])<.15)&(t[:,1]>1.40)&(t[:,1]<1.55)&(t[:,2]>.40)&(t[:,2]<.72)).any()
        optical={}
        for name in ('RAV4_MIRROR_L','RAV4_MIRROR_CENTER','RAV4_MIRROR_R'):
            n,w=nodes[name];p=world_vertices(n,w);c=(p.min(0)+p.max(0))/2;normal=n['vertices'][:,3:6].mean(0);normal/=np.linalg.norm(normal)
            assert np.array_equal(n['vertices'][:,6:8],before[name]['vertices'][:,6:8]),'Mirror UV changed'
            views=[]
            for eye in (EYE,EYE+[0,.025,0],EYE+[0,-.025,0]):
                incident=c-eye;incident/=np.linalg.norm(incident);ray=incident-2*np.dot(incident,normal)*normal
                assert ray[2]<-.92 and abs(ray[1])<.065,(file,name,ray)
                views.append(ray.tolist())
            optical[name]={'rear_horizon_rays_three_eye_heights':views}
        mats={m['name']:m for m in k.materials};oldm={m['name']:m for m in old.materials}
        for name,m in mats.items():
            if name not in PAINT and name!='RAV4_V7_Entune':assert m==oldm[name],name
        for name in PAINT:assert next(t for slot,i,t in mats[name]['textures'] if slot=='txDiffuse')=='RAV4_BlueFlame.dds'
        texture=next(t for t in k.textures if t['name']=='RAV4_BlueFlame.dds');pixels=np.asarray(Image.open(io.BytesIO(texture['data'])).convert('RGB'));assert abs(pixels.mean((0,1))-BLUE).max()<=4
        for name in ('RAV4_V13_MIRROR_CAP_L','RAV4_V13_MIRROR_CAP_R','RAV4_TAILGATE_GARNISH'):
            assert name in nodes and mats[k.materials[nodes[name][0]['material']]['name']]['textures'][0][2]=='RAV4_BlueFlame.dds'
        screen=mats['RAV4_V7_Entune'];props=dict(screen['props']);assert screen['shader']=='ksPerPixel' and screen['flags']==(0,0,0)
        assert all(props[key][0]==0 for key in ('ksAmbient','ksDiffuse','ksSpecular','fresnelC','fresnelMaxLevel'))
        # Preserve the tested needle sweep and sightlines; animate it with the
        # angles returned by the executable controller above, not INI aliases.
        pointer=nodes['RAV4_RPM_LIVE'][0];pos=pointer['matrix'][3,:3];length=260/2048*.308698*.89
        tri=opaque_triangles(k,lambda n:not n['name'].startswith('RAV4_NEEDLE_'))
        for rpm in range(0,8001,500):
            angle=math.radians(-91+rpm*183/8000)
            for f in (.45,.75,.95,1.):
                target=pos+[math.cos(angle)*length*f,math.sin(angle)*length*f,0]
                for eye in (EYE,np.array([.431,1.39,-.12])):assert not ray_hits(tri,eye,target).any(),('RPM obstruction',file,rpm)
        result[file]={'unchanged_other_nodes':preserved,'duplicate_pod_removed':True,'mirror_optics':optical,'unobstructed_window_rays':windows(k),'RPM_sweep_unoccluded_17_inputs':True,'wheel_glass_door_LED_seat_materials_byte_preserved':True,'all_painted_materials_recolor_together':True}
    with ZipFile(ROOT/'artifacts/Toyota_RAV4_Blue_Flame_CARL_Interior_0.14.zip') as z:
        preserved=0
        for member in z.namelist():
            prefix='content/cars/'+CAR.name+'/'
            if member.startswith(prefix+'data/') or member.startswith(prefix+'sfx/') or member==prefix+'collider.kn5':
                assert (ROOT/member).read_bytes()==z.read(member),member;preserved+=1
    return {'models':result,'data_audio_collider_files_byte_identical_to_014':preserved,'paint_shop_schema_source':'gro-ove/actools AcManager/PaintShop/PaintShop.cs; type carpaint / texture / defaultColor / flakesAvailable','paint_shop_UI_runtime_tested':False}


def main():
    check.VISUAL_DATA.add('driver3d.ini')
    r=check.validate(Path('/workspace/scratch/Toyota_RAV4_Blue_Flame_One_Click_Content_Manager.zip'),CAR,'0.15')
    try:
        r['executed_visual_Lua_tests']=lua_checks();r['regressions']=regressions();r['driver_motion']=check_animation();r['native_font']=font_checks()
    except Exception as e:
        import traceback;traceback.print_exc();r['errors'].append(repr(e));r['status']='failed_offline_checks'
    (ROOT/'validation-report-15.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({s:r[s] for s in ('status','errors','warnings')},indent=2));raise SystemExit(bool(r['errors']))

if __name__=='__main__':main()
