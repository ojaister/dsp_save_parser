"""Read-only progress summary for a Dyson Sphere Program save (build 0.10.35.29104).

Usage (from the repository root):
    python scripts/dsp_progress.py path/to/save.dsv > progress.json

Prints JSON: game version, hours played, recipes and techs unlocked, research in
progress (hash progress), the research queue, and built / planned buildings per planet.
IDs are numeric (proto ids); names are not looked up here.

It never writes to the save. It refuses to print results unless parsing ends exactly at the
last byte of the file, which flags a layout mismatch (for example after a game update).
Only saves from the matching game build parse; older saves fail by design.
"""
import sys, os, json, importlib, importlib.util, collections


def load_parser(repo):
    outer = os.path.join(repo, 'dsp_save_parser')
    inner = os.path.join(outer, 'dsp_save_parser')
    sys.path.insert(0, outer)
    spec = importlib.util.spec_from_file_location('gen', os.path.join(inner, 'generator.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    gen.generate_parser(os.path.join(inner, 'save_format.txt'),
                        os.path.join(inner, 'save_format_generated.py'))
    return importlib.import_module('dsp_save_parser.save_format_generated')


def main(save_path, repo):
    m = load_parser(repo)
    with open(save_path, 'rb') as f:
        s = m.GameSave.parse(f)
        if f.tell() != os.path.getsize(save_path):
            raise SystemExit('parse did not consume the whole file; layout mismatch, results untrusted')
    gd = s.game_data
    h = gd.history
    ts = h.tech_state
    out = {
        'game_version': [s.major_game_version, s.minor_game_version,
                         s.release_game_version, s.build_game_version],
        'save_name': gd.game_name,
        'hours_played': round(gd.game_tick / 60 / 3600, 2),
        'recipes_unlocked': sorted(h.recipe_unlocked),
        'techs_total': len(ts),
        'techs_unlocked': sorted(t.id for t in ts if t.unlocked),
        'tech_in_progress': [{'id': t.id, 'uploaded': t.hash_uploaded, 'needed': t.hash_needed}
                             for t in ts if not t.unlocked and t.hash_uploaded > 0],
        'current_tech': h.current_tech,
        'tech_queue': [t for t in h.tech_queue if t],
        'planets': [],
    }
    for fa in gd.factories:
        built = [e for e in fa.entity_pool if getattr(e, 'id', 0) > 0]
        planned = []
        for p in fa.prebuild_pool:
            d = p.prebuild_data
            if d.id != 0 and not d.is_destroyed:
                planned.append(d.proto_id)
        out['planets'].append({
            'planet_id': fa.planet_id,
            'built': dict(collections.Counter(e.proto_id for e in built)),
            'planned_not_built': dict(collections.Counter(planned)),
        })
    json.dump(out, sys.stdout, indent=1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    repo_root = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main(sys.argv[1], repo_root)
