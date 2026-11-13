"""Exercise motif search and transactional phrase merging through their CLIs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


scripts = Path(__file__).resolve().parents[1] / 'skills/sv2cli-production/scripts'


def run(script, *args):
    return subprocess.run([sys.executable, str(scripts / script), *map(str, args)],
                          capture_output=True, text=True, encoding='utf-8')


with tempfile.TemporaryDirectory(prefix='sv2cli-helpers-') as directory:
    root = Path(directory)
    tracks = []
    for track, pitches, onsets in [(1, [60, 64, 60, 64], [0, 2, 4, 6]),
                                  (2, [62, 65], [1, 3])]:
        notes = [{'midi': pitch, 'onset_q': onset, 'duration_q': 1,
                  'beat': 1, 'lyrics': 'la'} for pitch, onset in zip(pitches, onsets)]
        tracks.append({'track': track, 'sections': [{'bars': [{'bar': 1, 'notes': notes}]}]})
    score = root / 'score.json'
    score.write_text(json.dumps({'tracks': tracks}), encoding='utf-8')
    cross = run('motif_distance.py', score, '--motif', '60 62')
    assert cross.returncode == 0 and json.loads(cross.stdout)['matchCount'] == 0
    matched = run('motif_distance.py', score, '--motif', '60 64')
    assert matched.returncode == 0, matched.stderr
    occurrences = json.loads(matched.stdout)['occurrences']
    assert len(occurrences) == 2
    assert occurrences[1]['distance_from_prev_q'] == 4
    assert occurrences[1]['gap_from_prev_q'] == 1

    master = root / 'master.json'
    first = root / 'first.json'
    phrase = {'id': 'first', 'start': '0', 'end': '2', 'text': 'la', 'notes': []}
    first.write_text(json.dumps(phrase), encoding='utf-8')
    assert run('phrase_merge.py', master, first).returncode == 0
    before = master.read_bytes()
    assert run('phrase_merge.py', master, first).returncode == 0
    assert master.read_bytes() == before
    second = root / 'second.json'
    second.write_text(json.dumps({**phrase, 'id': 'second', 'start': '3', 'end': '4'}), encoding='utf-8')
    conflicting = root / 'conflicting.json'
    conflicting.write_text(json.dumps({**phrase, 'id': 'conflict'}), encoding='utf-8')
    failed = run('phrase_merge.py', master, second, conflicting)
    assert failed.returncode == 1
    assert master.read_bytes() == before
    assert not master.with_suffix('.json.lock').exists()

print('Cross-track motif search, recurrence gaps and atomic/idempotent phrase merges passed.')
