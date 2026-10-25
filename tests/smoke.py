"""Execute the packaged recipe and a timing/overwrite workflow in isolation."""
import tempfile
import json,sys,subprocess
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
    # Independent underlay intent: reject wrong text, then match an explicit correction.
    plan={'source':{'reference':'independent smoke fixture','reviewed':True},'tracks':[{'selector':'#1','phrases':[
        {'id':'line-1','start':'1','end':'3','text':'山','notes':[{'at':'1','dur':'2','pitch':60,'lyrics':'山'}]}]}]}
    planfile=folder/'lyrics-plan.json';planfile.write_text(json.dumps(plan),'utf8')
    helper=root/'skills/sv2cli-production/scripts/audit_lyrics.py'
    checked=subprocess.run([sys.executable,str(helper),str(src),'--plan',str(planfile),'--require-full-project'],capture_output=True,text=True,encoding='utf8')
    assert checked.returncode==2 and not json.loads(checked.stdout)['valid'],checked.stderr
    corrected=folder/'corrected.svp'
    apply(Project.load(src),[{'op':'lyrics.set','tracks':['#1'],'values':['山']}],True).save(corrected)
    checked=subprocess.run([sys.executable,str(helper),str(corrected),'--plan',str(planfile),'--require-full-project'],capture_output=True,text=True,encoding='utf8')
    report=json.loads(checked.stdout)
    assert checked.returncode==0 and report['allProjectNotesMapped'],checked.stderr
    assert not report['originalScoreIndependentlyVerified'] and not report['subjectiveListeningVerified']
print('Recipe, backup, score lock, timing and independent lyric-plan rejection/correction smoke passed.')
