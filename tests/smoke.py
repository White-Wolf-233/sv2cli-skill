"""Execute the packaged recipe and a timing/overwrite workflow in isolation."""
import tempfile
from pathlib import Path
import wave
import numpy as np
from sv2cli.cli import _parser, execute
from sv2cli.edit import apply
from sv2cli.project import new_project, QUARTER as Q, Project
from sv2cli.pcm import encode

root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='sv2cli-skill-') as folder:
    folder=Path(folder);src=folder/'song.svp'
    p=apply(new_project(),[{'op':'notes.replace','notes':[{'onset':Q,'duration':2*Q,'pitch':60,'lyrics':'la'}]}],True)
    p.save(src);before=src.read_bytes()
    result=execute(_parser().parse_args(['edit',str(src),'--recipe',str(root/'skills/sv2cli-production/assets/choral-mix.recipe.json'),'--score-lock','--in-place']))
    assert Path(result['backup']).read_bytes()==before
    assert Project.load(src).score_fingerprint()==p.score_fingerprint()
    assert execute(_parser().parse_args(['time',str(src),'--at','bar:1:2']))['blick']==Q
    audio=np.zeros((1,2500));audio[:,740:1500]=.1
    wav=folder/'late.wav'
    with wave.open(str(wav),'wb') as f:
        f.setparams((1,2,1000,0,'NONE','none'));f.writeframes(encode(audio,16))
    report=execute(_parser().parse_args(['timing-check',str(src),str(wav),'--track','#1']))
    assert report['notes'][0]['entryDeltaSeconds']>.2 and not report['alignmentVerified']
    fixed=execute(_parser().parse_args(['audio-shift',str(src),str(wav),'--track','#1','--seconds','-.24','-o',str(folder/'fixed.wav')]))
    assert abs(fixed['after']['notes'][0]['entryDeltaSeconds'])<.02
    assert src.read_bytes()!=before and fixed['scoreUnchanged'] and not fixed['resampled']
print('Packaged recipe, backup, score lock, musical time and audio-shift smoke passed.')
