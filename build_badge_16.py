"""Rear Toyota emblem only: checksum-pinned 0.15.1 -> matte-badge 0.16."""
import hashlib,json,copy
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import numpy as np
from PIL import Image
from kn5 import Kn5
from build_visual_revision import components,submesh,material,prop
from interior_revision import _texture

ROOT=Path('/workspace/Assetto-Corsa-Rav4');ART=ROOT/'artifacts'
CAR=ROOT/'content/cars/toyota_rav4_adventure_blueflame_x5m'
WORK=Path('/workspace/scratch/rav4_drift');BASE=WORK/'badge-baseline';MODELS=('x5.kn5','x5_lod_b.kn5','x5_lod_c.kn5','x5_lod_d.kn5')
BASE_ZIP=ART/'Toyota_RAV4_Blue_Flame_CARL_Interior_0.15.1.zip'
BASE_SHA='511bc32a84ef204c2175bf42172506f826a7920ae214eea6e3f1022afe9e8cd3'


def main():
 assert hashlib.sha256(BASE_ZIP.read_bytes()).hexdigest()==BASE_SHA
 report={'release':'0.16 matte rear Toyota emblem','status':'passed_offline_checks','errors':[],'assetto_corsa_runtime_tested':False,'runtime_tested':False,'baseline_archive_sha256':BASE_SHA,'models':{}}
 prefix=CAR.relative_to(ROOT).as_posix()+'/'
 with ZipFile(BASE_ZIP) as source:
  for file in MODELS:
   p=BASE/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(source.read(prefix+file))
   old=Kn5(p);k=Kn5(p)
   tex=_texture(k,'RAV4_V16_RearToyotaMatteBlack.dds',Image.new('RGBA',(32,32),(16,17,18,255)))
   mat=material('RAV4_V16_RearToyotaMatteBlack',tex,.015,8,ambient=.30,diffuse=.65);mat['shader']='ksPerPixel';mat['flags']=(0,0,0)
   for key,val in [('fresnelC',0),('fresnelMaxLevel',0),('ksEmissive',(0,0,0))]:prop(mat,key,val)
   mi=len(k.materials);k.materials.append(mat);changed={};badge=None
   for n,w in list(k.nodes()):
    if n['kind']!=2 or k.materials[n['material']]['name']!='ChromeTrims':continue
    mask=np.zeros(len(n['indices'])//3,bool)
    for part,lo,hi,c in components(n):
     if hi[2]<-2.30 and abs(c[0])<.15 and c[1]>1.07 and hi[1]<1.20:mask|=part
    if mask.any():
     assert badge is None
     badge=submesh(n,mask,'RAV4_REAR_TOYOTA_MATTE_BADGE',mi)
     changed[n['name']]={'badge_triangles':int(mask.sum()),'source_material':'ChromeTrims'}
     remain=submesh(n,~mask);n.update(remain)
   assert badge is not None;k.root['children'].append(badge);k.save(CAR/file)
   # No moved/resized faces: the union of the original chrome triangles is
   # identical, now divided between chrome trim and a matte badge material.
   before={n['name']:n for n,w in old.nodes()};after={n['name']:n for n,w in k.nodes()}
   for name,n in before.items():
    a=after[name]
    if name in changed:
     def rows(x):return sorted(x['vertices'][x['indices']].reshape(-1,33).tobytes()[i:i+132] for i in range(0,len(x['indices'])*44,132))
     assert rows(n)==sorted(rows(a)+rows(badge))
    elif n['kind']==1:assert np.array_equal(n['matrix'],a['matrix'])
    else:assert np.array_equal(n['vertices'],a['vertices']) and np.array_equal(n['indices'],a['indices']) and n['material']==a['material']
   assert k.materials[:-1]==old.materials
   assert all(next(t for t in k.textures if t['name']==x['name'])==x for x in old.textures)
   check=Kn5(CAR/file);tmp=WORK/('roundtrip-'+file);check.save(tmp);assert tmp.read_bytes()==(CAR/file).read_bytes();tmp.unlink()
   report['models'][file]={'sha256':hashlib.sha256((CAR/file).read_bytes()).hexdigest(),'isolated_components':changed,'other_vertices_indices_transforms_and_materials_exactly_preserved':True,'matte_shader':'ksPerPixel','specular':.015,'fresnel':0}
   print(file,'badge only saved',flush=True)
  ui=json.loads(source.read(prefix+'ui/ui_car.json'));ui.update(name='Toyota RAV4 Adventure | Blue Flame CARL (Matte Badge 0.16, X5M Tune)',version='0.16 - Matte black rear Toyota badge')
  ui['description']='0.16: only the rear Toyota oval emblem is refinished matte black. All 0.15.1 screen brightness, RPM, mirrors, interior, paint/shop, wheel finish and BMW driving systems are retained. '+ui['description']
  notes='''RAV4 Adventure Blue Flame CARL — MATTE REAR BADGE 0.16

Only the rear Toyota oval emblem is matte black. Front badge, wheel badges,
other chrome, blue tailgate trim and all 0.15.1 working behavior are retained.
This version retains the original BMW X5M tune, handling and sound.

Close AC. Install the complete ZIP through Content Manager, including the
instrument font entry, then start a fresh session. This updates the existing
RAV4 car ID; the separate Rav4 Drift installs under a different car ID.

Offline checks confirm unchanged geometry, the isolated rear-badge material,
complete archive integrity and preserved nonvisual data. AC rendering is
not available here, so matte appearance is not tested in-game.
'''
  replacements={prefix+f:(CAR/f).read_bytes() for f in MODELS}
  replacements[prefix+'ui/ui_car.json']=(json.dumps(ui,indent=2)+'\n').encode()
  replacements[prefix+'INSTALL_README.txt']=notes.encode()
  replacements[prefix+'MATTE_BADGE_16_REPORT.json']=(json.dumps(report,indent=2)+'\n').encode()
  replacements[prefix+'VALIDATION_REPORT.json']=(json.dumps(report,indent=2)+'\n').encode()
  oldmanifest=json.loads(source.read(prefix+'INSTALL_MANIFEST.json'));oldmanifest.update(release='0.16 matte black rear Toyota emblem');replacements[prefix+'INSTALL_MANIFEST.json']=(json.dumps(oldmanifest,indent=2)+'\n').encode()
  for name,data in replacements.items():(ROOT/name).write_bytes(data)
  out=ART/'Toyota_RAV4_Blue_Flame_CARL_Matte_Badge_0.16.zip'
  with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
   for item in source.infolist():z.writestr(item.filename,replacements.get(item.filename,source.read(item)))
   for name,data in replacements.items():
    if name not in source.namelist():z.writestr(name,data)
  with ZipFile(out) as z:
   assert z.testzip() is None
   preserved=0
   for name in source.namelist():
    if name not in replacements:assert z.read(name)==source.read(name),name;preserved+=1
  sha=hashlib.sha256(out.read_bytes()).hexdigest();(ART/(out.name+'.sha256')).write_text(sha+'  '+out.name+'\n')
  assert out.stat().st_size<100*1024*1024
  (ROOT/'matte-badge-report-16.json').write_text(json.dumps(report,indent=2)+'\n')
  manifest={'file':out.name,'sha256':sha,'bytes':out.stat().st_size,'zip_crc':'passed','unchanged_baseline_members':preserved,'source_baseline_sha256':BASE_SHA,'runtime_tested':False}
  (ART/'release_16_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
