"""Rebuild 0.15 from the verified 0.14 install, changing visual assets only.

CSP scene APIs checked against ac-custom-shaders-patch/acc-lua-sdk.
CM Paint Shop schema checked against gro-ove/actools PaintShop.cs/CarPaint.cs.
"""
import hashlib,json,math
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation
from kn5 import Kn5,world_vertices
from build_visual_revision import components,submesh,bounds,prop
from interior_revision import _texture
from interior_revision_12 import ROOT,CAR,MODELS
from finish_revision_13 import write_ini
from validate_revision_08 import parse_ini

WORK=Path('/workspace/scratch/interior15');BASE=WORK/'baseline'
BLUE=(0,149,218)
PAINT=('lambert1','Adventure_Rock','WhiteRoof','RAV4_Tailgate_BlueFlame')
EYE=np.array([.431,1.361272,-.096665])


def baseline():
    archive=ROOT/'artifacts/Toyota_RAV4_Blue_Flame_CARL_Interior_0.14.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='625f175a7583d5fe71399903e5dca823a73ffebaf077f2dfc191f68f143eea84'
    with ZipFile(archive) as z:
        for file in (*MODELS,'extension/ext_config.ini','data/analog_instruments.ini','data/digital_instruments.ini','data/lights.ini','ui/ui_car.json','INSTALL_MANIFEST.json'):
            p=BASE/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read('content/cars/'+CAR.name+'/'+file))


def mirror_cleanup(k):
    removed={}
    # This disconnected 250-face component is the donor sensor/mirror pod.
    # It escaped the earlier donor-mirror centroid crop. Remove the connected
    # component, not a spatial slice through neighboring dashboard polygons.
    for n,_ in list(k.nodes()):
        if n['kind']!=2 or not n['name'].startswith('RAV4_V12_CABIN_part_30_PLASTIC_'):continue
        delete=np.zeros(len(n['indices'])//3,bool)
        for mask,lo,hi,center in components(n):
            if lo[1]>1.40 and hi[1]<1.55 and lo[2]>.40 and hi[2]<.72 and max(abs(lo[0]),abs(hi[0]))<.15:
                delete|=mask
        if delete.any():
            removed[n['name']]={'triangles':int(delete.sum())};n.update(submesh(n,~delete))
    assert removed,'Duplicate pod must be identified in every LOD'
    by_name={n['name']:n for n,_ in k.nodes()}
    records={}
    for name,dx in [('RAV4_MIRROR_L',.07),('RAV4_MIRROR_CENTER',0.),('RAV4_MIRROR_R',-.07)]:
        n=by_name[name];p=n['vertices'][:,:3].astype(float);center=(p.min(0)+p.max(0))/2
        source=n['vertices'][:,3:6].mean(0).astype(float);source/=np.linalg.norm(source)
        toward_eye=EYE-center;toward_eye/=np.linalg.norm(toward_eye)
        # Rays centered on the rear horizon instead of pavement. Side mirrors
        # look slightly outboard, center mirror through the rear window.
        rear=np.array([dx,0.,-1.]);rear/=np.linalg.norm(rear)
        normal=toward_eye+rear;normal/=np.linalg.norm(normal)
        rot=Rotation.align_vectors([normal],[source])[0].as_matrix().T
        targets=[n]
        if name=='RAV4_MIRROR_CENTER':targets.append(by_name['RAV4_V13_MIRROR_HOUSING'])
        for target in targets:
            target['vertices'][:,:3]=(target['vertices'][:,:3]-center)@rot+center
            target['vertices'][:,3:6]=target['vertices'][:,3:6]@rot
            target['vertices'][:,8:11]=target['vertices'][:,8:11]@rot
            bounds(target)
        incident=-toward_eye;reflected=incident-2*np.dot(incident,normal)*normal
        records[name]={'center_m':center.tolist(),'normal':normal.tolist(),'rearward_center_ray':reflected.tolist(),'pitch_degrees':float(math.degrees(math.asin(reflected[1]))),'yaw_degrees':float(math.degrees(math.atan2(reflected[0],-reflected[2]))),'glass_adjustment_degrees':float(np.linalg.norm(Rotation.from_matrix(rot).as_rotvec())*180/math.pi)}
    return {'removed_duplicate_sensor_pod':removed,'optical_aim':records,'smart_mirror_order':['left','center','right']}


def paint(k):
    tex=_texture(k,'RAV4_BlueFlame.dds',Image.new('RGBA',(128,128),(*BLUE,255)))
    for m in k.materials:
        if m['name'] not in PAINT:continue
        m['textures']=[(s,i,tex if s=='txDiffuse' else t) for s,i,t in m['textures']]
        for key,val in [('ksAmbient',.45),('ksDiffuse',.5),('ksSpecular',.35),('ksSpecularEXP',150),('fresnelC',.04),('fresnelMaxLevel',.72)]:prop(m,key,val)
    return {'srgb':BLUE,'manufacturer_reference':'Toyota Blue Flame / 8W9; visual approximation, not spectrophotometer calibrated','finish':'Solid nonmetallic base, neutral glossy clearcoat','shared_texture':tex,'materials':PAINT}


def screen(k):
    m=next(m for m in k.materials if m['name']=='RAV4_V7_Entune')
    # Keep AA's dynamic texture, use the same predictable opaque emissive
    # path as the working cluster. No glass/SSR or light-dependent diffuse.
    m['shader']='ksPerPixel';m['flags']=(0,0,0)
    for key,val in [('ksAmbient',0),('ksDiffuse',0),('ksSpecular',0),('fresnelC',0),('fresnelMaxLevel',0),('ksEmissive',(.65,.65,.65))]:prop(m,key,val)
    return {'shader':'ksPerPixel','ambient':0,'diffuse':0,'specular':0,'day_emission':.65,'headlights_on_emission':.10,'owner':'rav4_instruments.lua','runtime_tested':False}


def config():
    cfg=parse_ini((BASE/'extension/ext_config.ini').read_text())
    cfg.pop('ANALOG_INDICATOR_0',None);cfg.pop('Material_DigitalScreen',None)
    cfg['SHADER_REPLACEMENT_15_SCREEN']={'MATERIALS':'RAV4_V7_Entune','SHADER':'ksPerPixel','BLEND_MODE':'OPAQUE','DEPTH_MODE':'NORMAL','IS_TRANSPARENT':'0','CAST_SHADOWS':'0','PROP_0':'ksAmbient, 0','PROP_1':'ksDiffuse, 0','PROP_2':'ksSpecular, 0','PROP_3':'fresnelC, 0','PROP_4':'fresnelMaxLevel, 0','PROP_5':'ksEmissive, .65, .65, .65'}
    cfg['EXTRA_FX'].pop('GLASS_FILTER',None)
    cfg['EXTRA_FX']['SKIP_GBUFFER']='RAV4_GLASS_FRONT_INSIDE, RAV4_GLASS_PRIVACY_INSIDE, RAV4_ENTUNE_SCREEN'
    for i in range(3):cfg['REAL_MIRROR_'+str(i)]={'ASPECT_MULT':'1','FOV':'10','ROTATION':'0, 0'}
    cfg['Material_CarPaint_Solid'].update(FresnelC='.04',FresnelMax='.72',ClearCoatThickness='.04',SpecularBase='.35, 150',AmbientSpecular='.30',BrightnessAdjustment='1',ColoredSpecular='0',NormalsNoise='0')
    # Official CSP extra_wheels_axis example documents this visual loader.
    # Per-simulation-frame callbacks do not depend on a gauge being drawn.
    cfg['SCRIPT_0']={'SCRIPT':'rav4_instruments.lua','SKIP_FRAMES':'0','ACTIVE_FOR_UNFOCUSED':'1','ACTIVE_FOR_LOD':'D','ACTIVE_FOR_NEAREST':'12'}
    write_ini(CAR/'extension/ext_config.ini',cfg)
    # Existing working speed/gear/clock bindings are byte-preserved.
    for name in ('analog_instruments.ini','digital_instruments.ini','lights.ini'):(CAR/'data'/name).write_bytes((BASE/'data'/name).read_bytes())
    rules=[{'type':'carpaint','id':'rav4_body','name':'Body paint (includes mirror caps and tailgate trim)','texture':'RAV4_BlueFlame.dds','defaultColor':'#0095DA','colorAvailable':True,'flakesAvailable':False,'guessColorsFromPreviews':False}]
    (CAR/'ui/cm_paintshop.json').write_text(json.dumps(rules,indent=2)+'\n')
    # A real skin override makes the shipped color editable and removable;
    # every painted material in all four LODs shares this texture name.
    high=Kn5(CAR/'x5.kn5');texture=next(t for t in high.textures if t['name']=='RAV4_BlueFlame.dds')
    (CAR/'skins/all_blue_flame/RAV4_BlueFlame.dds').write_bytes(texture['data'])
    ui=json.loads((BASE/'ui/ui_car.json').read_text());ui.update(name='Toyota RAV4 Adventure | Blue Flame CARL (Interior 0.15, X5M Tune)',version='0.15 - Screen / Mirrors / Live RPM / Paint Shop')
    ui['description']='Revised opaque Android Auto display with headlight dimming; direct CSP visual Lua RPM needle driven by car telemetry, replacing the nonresponding declarative binding. Duplicate donor mirror/sensor pod removed; mirror glass aimed toward the rear horizon from the configured driving position. Brighter Blue Flame 8W9 approximation, glossy solid clearcoat, and Content Manager Paint Shop body-color editor including caps and garnish. Preserves 0.14 fitted doors, matte black wheel pockets, grille lights, Adventure black/orange cabin, working native MID, tune/audio/driver animation/collider. Offline checks only; AC/Pure/CSP runtime untested. Adapted 2023 cabin approximates 2019 Adventure; decorative ODO/economy/climate graphics remain.'
    (CAR/'ui/ui_car.json').write_text(json.dumps(ui,indent=2)+'\n')
    m=json.loads((BASE/'INSTALL_MANIFEST.json').read_text());m.update(release='0.15 screen, mirrors, direct RPM and editable Blue Flame',rpm='Direct visual Lua car.rpm -> RAV4_RPM_LIVE; no declarative RPM controller',paint_shop='ui/cm_paintshop.json; shared RAV4_BlueFlame.dds skin override',runtime_tested=False);(CAR/'INSTALL_MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')


def main():
    baseline();report={'release':'0.15','runtime_tested':False,'models':{}}
    for file in MODELS:
        k=Kn5(BASE/file)
        report['models'][file]={'mirrors':mirror_cleanup(k),'paint':paint(k),'screen':screen(k)}
        next(n for n,_ in k.nodes() if n['name']=='ARROW_RPM')['name']='RAV4_RPM_LIVE'
        for n,_ in k.nodes():
            if n['kind']==2:n['vertices'][:,8:11]=np.round(n['vertices'][:,8:11],5)
        k.save(CAR/file);print(file,'0.15 saved',flush=True)
    config();(ROOT/'interior-build-report-15.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
