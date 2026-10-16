"""Set the live player-car TC mode off, without changing working physics.

Factory electronics.ini is already off in 1.0.3. Use the supported car-control
ac.setTC(0) setter, also used by official CSP car/display configurations.
"""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path('/workspace/Assetto-Corsa-Rav4')
ART = ROOT / 'artifacts'
CAR = ROOT / 'content/cars/rav4_drift'
PREFIX = 'content/cars/rav4_drift/'
SOURCE = ART / 'Rav4_Drift_1.0.3_Full.zip'
SOURCE_SHA = '6f4c21cb602c96dab191ddf0f18f2be23decf4650163e122a06b80f51daa0526'

CONTROLLER = '''-- Dedicated player-car TC controller; separate from instruments and physics.
-- ac.setTC(0) sets the live TC mode to OFF. Keep it off after session/pit resets.
-- Does not change ABS, stability control, throttle input or other cars.
local warned = false

function script.update(dt)
  if not car or car.index ~= 0 or car.isAIControlled then return end
  if sim and sim.isReplayActive then return end

  if type(ac.setTC) == 'function' then
    if car.tractionControlMode ~= 0 then ac.setTC(0) end
  elseif not warned then
    warned = true
    if type(ac.log) == 'function' then
      ac.log('Rav4 Drift: live TC-off controller requires CSP car-control ac.setTC; set TC Off in driving assists.')
    end
  end
end
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def test_controller():
    # Execute the actual shipped Lua with simulated CSP controls. The mock is
    # a logic/side-effect test, not a claim of a working Assetto Corsa runtime.
    sys.path.insert(0, '/workspace/scratch/lua-test-deps')
    from lupa.luajit21 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('''
      script = {}; sim = {isReplayActive=false}
      car = {index=0, isAIControlled=false, tractionControlMode=1}
      calls = {}; logs = {}; gas = 0.85; absMode = 3; stability = 0.4
      ac = {
        setTC=function(mode) table.insert(calls,mode); car.tractionControlMode=mode end,
        log=function(message) table.insert(logs,message) end
      }
    ''')
    lua.execute(CONTROLLER)
    lua.execute('''
      script.update(1/60)
      assert(car.tractionControlMode==0 and #calls==1 and calls[1]==0)
      -- Every nonzero mode is an absolute OFF request, never a toggle.
      for mode=1,12 do
        car.tractionControlMode=mode; script.update(1/60)
        assert(car.tractionControlMode==0 and calls[#calls]==0)
      end
      -- Already off: no redundant calls and no cycling back to maximum TC.
      local count=#calls
      for i=1,120 do script.update(1/60) end
      assert(#calls==count)
      -- A saved mode loaded later or a pit/session reset is corrected too.
      car.tractionControlMode=5; script.update(1/60)
      assert(car.tractionControlMode==0 and #calls==count+1)
      count=#calls
      -- Never control AI, other cars or replay playback.
      car.index=1; car.tractionControlMode=2; script.update(1/60)
      assert(car.tractionControlMode==2 and #calls==count)
      car.index=0; car.isAIControlled=true; script.update(1/60)
      assert(car.tractionControlMode==2 and #calls==count)
      car.isAIControlled=false; sim.isReplayActive=true; script.update(1/60)
      assert(car.tractionControlMode==2 and #calls==count)
      sim.isReplayActive=false
      -- API compatibility failure is reported once, without crashing.
      ac.setTC=nil
      script.update(1/60); script.update(1/60)
      assert(#logs==1 and #calls==count)
      assert(gas==0.85 and absMode==3 and stability==0.4)
    ''')
    return {'engine': 'LuaJIT 2.1 via lupa',
            'startup_and_modes_1_to_12_set_to_zero': True,
            'already_off_does_not_toggle_or_cycle': True,
            'late_saved_mode_and_reset_handled': True,
            'AI_other_cars_and_replays_untouched': True,
            'missing_API_logs_once_without_throwing': True,
            'scope': 'mocked car-control API; CSP/Assetto Corsa unavailable'}


def main():
    assert sha(SOURCE.read_bytes()) == SOURCE_SHA
    tests = test_controller()
    with ZipFile(SOURCE) as source:
        cfg = source.read(PREFIX + 'extension/ext_config.ini').decode()
        assert '[SCRIPT_1]' not in cfg and 'rav4_tc_off.lua' not in cfg
        cfg += '''
; Live TC-off controller for the player-driven Rav4 Drift only.
[SCRIPT_1]
SCRIPT = rav4_tc_off.lua
SKIP_FRAMES = 0
ACTIVE_FOR_UNFOCUSED = 1
ACTIVE_FOR_LOD = D
ACTIVE_FOR_NEAREST = 12
'''
        report = {'release': 'Rav4 Drift 1.0.4', 'status': 'passed_offline_checks',
                  'source_archive_sha256': SOURCE_SHA,
                  'assetto_corsa_runtime_tested': False,
                  'change': 'Dedicated CSP visual/car-control script sets live player TC mode to zero.',
                  'lua_logic_tests': tests,
                  'api_reference': 'https://github.com/ac-custom-shaders-patch/acc-extension-config/blob/master/config/cars/kunos/ks_ferrari_488_gt3.ini',
                  'all_physics_data_models_sound_and_existing_gauge_script_byte_preserved': True,
                  'normal_RAV4_exact_wheel_geometry_retained': True,
                  'limitations': 'Game runtime unavailable. A global CM assist menu or enforced server setting is not rewritten by this car package.'}
        notes = '''Rav4 Drift 1.0.4 — live traction control off

FULL ZIP: close Assetto Corsa, drag the full ZIP into Content Manager and
replace Rav4 Drift. Install all car/font files. No previous patch needed.
SMALL PATCH: requires 1.0.3. Close AC; extract into the Assetto Corsa root
containing acs.exe, merging content/cars/rav4_drift and replacing files.

The previous version set PRESENT=0 and ACTIVE=0 in electronics.ini. This
build also uses a separate CSP car-control script to set the live TC mode
to zero when it is enabled. It checks each update and reapplies after saved
settings are loaded or the car returns to pits. This is an absolute OFF
request, not a key toggle. It only runs for the player-driven car, skipping
AI, other cars and replays. Requires CSP with car-control ac.setTC support.

The gauge/infotainment script and Supra anti-lag physics script are
byte-preserved. Every physics data file, all four normal-RAV4 wheel models,
materials, sound and other assets are unchanged from 1.0.3. Factory TC-off
settings are retained. ABS, stability control and throttle are not altered.

Content Manager's global driving-assists menu is separate from this car's
live TC mode. Set its traction-control option to Off and stability control
to 0% for drift driving. Ctrl+T is AC's TC toggle if needed in-session.
This package does not change your global CM settings or server rules.

Shipped Lua executed in LuaJIT with simulated CSP controls: nonzero modes
1..12 go to zero, already-off stays off, late settings/reset are corrected,
AI/other cars/replays are skipped, and missing API reports once without
throwing. These are offline logic checks, not an Assetto Corsa runtime test.
Both archives are checked against the working 1.0.3 baseline. Installation,
actual CSP API behavior and TC intervention still need an in-game check.
'''
        ui = json.loads(source.read(PREFIX + 'ui/ui_car.json'))
        ui['version'] = '1.0.4 - Live TC-off controller / normal RAV4 wheels'
        ui['description'] = ('1.0.4 adds a dedicated CSP controller setting live player traction control to zero. '
                             'Exact normal RAV4 wheels and all Supra drift physics retained. '
                             'Lua logic checked offline; game runtime untested. ' + ui['description'])
        manifest = json.loads(source.read(PREFIX + 'INSTALL_MANIFEST.json'))
        manifest.update(release='Rav4 Drift 1.0.4', runtime_tested=False,
                        traction_control='factory off + dedicated live ac.setTC(0) controller')
        replacements = {
            PREFIX + 'extension/ext_config.ini': cfg.encode(),
            PREFIX + 'extension/rav4_tc_off.lua': CONTROLLER.encode(),
            PREFIX + 'ui/ui_car.json': (json.dumps(ui, indent=2) + '\n').encode(),
            PREFIX + 'INSTALL_MANIFEST.json': (json.dumps(manifest, indent=2) + '\n').encode(),
            PREFIX + 'INSTALL_README.txt': notes.encode(),
            PREFIX + 'VISUAL_REVISION_NOTES.md': notes.encode(),
            PREFIX + 'VALIDATION_REPORT.json': (json.dumps(report, indent=2) + '\n').encode()}
        for name, data in replacements.items():
            (ROOT / name).write_bytes(data)
        full = ART / 'Rav4_Drift_1.0.4_Full.zip'
        patch = ART / 'Rav4_Drift_1.0.4_TC_Fix_Patch.zip'
        with ZipFile(full, 'w', ZIP_DEFLATED, compresslevel=9) as out:
            for name in source.namelist():
                out.writestr(name, replacements.get(name, source.read(name)))
            for name, data in replacements.items():
                if name not in source.namelist():
                    out.writestr(name, data)
        with ZipFile(patch, 'w', ZIP_DEFLATED, compresslevel=9) as out:
            for name, data in replacements.items():
                out.writestr(name, data)
        outputs = []
        for path in (full, patch):
            with ZipFile(path) as z:
                assert z.testzip() is None
                assert len(z.namelist()) == len({n.lower() for n in z.namelist()})
                for name in z.namelist():
                    assert z.read(name) == (replacements[name] if name in replacements else source.read(name))
            digest = sha(path.read_bytes())
            (ART / (path.name + '.sha256')).write_text(digest + '  ' + path.name + '\n')
            outputs.append({'file': path.name, 'bytes': path.stat().st_size, 'sha256': digest})
        with ZipFile(full) as out:
            for name in source.namelist():
                if '/data/' in name or name.endswith(('.kn5', '.bank', 'rav4_instruments.lua')):
                    assert out.read(name) == source.read(name), name
            assert out.read(PREFIX + 'extension/ext_config.ini').decode().replace(
                cfg[len(source.read(PREFIX + 'extension/ext_config.ini').decode()):], '') == source.read(PREFIX + 'extension/ext_config.ini').decode()
        result = {'release': '1.0.4', 'outputs': outputs, 'status': 'passed_offline_checks',
                  'runtime_tested': False, 'changed_members': sorted(replacements)}
        (ART / 'release_drift_104_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
        (ROOT / 'rav4-drift-live-tc-104.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'package': result, 'tests': tests}, indent=2), flush=True)


if __name__ == '__main__':
    main()
