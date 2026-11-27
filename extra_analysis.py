"""Matched-set levels, per-style differences, wrong-flip differences and the exploratory d-prime numbers in the paper.
Run from this folder: .venv/bin/python extra_analysis.py (reads the saved replies, calls no API)."""
import json,contextlib,io
nb=json.load(open('experiment.ipynb'))
src=lambda i:''.join(nb['cells'][i]['source'])
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(src(3)); exec(src(5)); exec(src(7))
    exec(src(13).split('run_phase1()\nP1')[0])
    exec(src(21)); exec(src(22))
f=lambda t:f"{t[0]:+.3f} [{ci(t[1])[0]:+.3f},{ci(t[1])[1]:+.3f}]"
d=lambda a,b,n:(a[n][0]-b[n][0],a[n][1]-b[n][1])
chk=metrics('think','none'); print('check caving',f(chk['caving']),'update',f(chk['update']))
print('\nPhase 1 accuracy')
for m in MODES:
    v=[x['first_correct'] for (q,mm),x in P1.items() if mm==m]; print(m,len(v),sum(v)/len(v))
both_q={q for q in QIDS if (q,'think') in P1 and (q,'nothink') in P1}
from collections import Counter
print('cross',len(both_q),Counter((P1[(q,'think')]['first_correct'],P1[(q,'nothink')]['first_correct']) for q in both_q))
for m in MODES:
  print('ungraded first',m,400-sum(1 for (q,mm) in P1 if mm==m))
print('\nLOST (wrong flip)')
for s in SYSTEMS:
    for nm,k in SETS.items():
        a,b=metrics('think',s,keep=k),metrics('nothink',s,keep=k)
        print(s,nm,f(a['lost']),f(b['lost']),'diff',f(d(a,b,'lost')), 'caving diff',f(d(a,b,'caving')),'sel diff',f(d(a,b,'selectivity')))
print('\nBY STYLE think-nothink')
for s in SYSTEMS:
  for nm,k in (('all',None),('same first',SETS['same first answer']),('both',SETS['both right or both wrong'])):
    for st in PUSH_STYLES:
        a,b=metrics('think',s,[st],keep=k),metrics('nothink',s,[st],keep=k)
        print(s,nm,st,'cav',f(d(a,b,'caving')),'upd',f(d(a,b,'update')),'sel',f(d(a,b,'selectivity')))
print('\nFIX by style, think and nothink')
for m in MODES:
  for st in PUSH_STYLES:
    a,b=metrics(m,'fix',[st]),metrics(m,'none',[st]); print(m,st,'cav',f(d(a,b,'caving')),'upd',f(d(a,b,'update')),'sel',f(d(a,b,'selectivity')))
print('\nlost by fix')
for m in MODES:
    a,b=metrics(m,'fix'),metrics(m,'none'); print(m,'lost',f(d(a,b,'lost')))
from statistics import NormalDist
z=np.vectorize(NormalDist().inv_cdf)
def dp(m,s,k=None,st=PUSH_STYLES):
    x=metrics(m,s,st,keep=k); g=lambda v:z(np.clip(v,.005,.995)); 
    return (g(x['update'][0])-g(x['caving'][0]), g(x['update'][1])-g(x['caving'][1])), (-(g(x['update'][0])+g(x['caving'][0]))/2, -(g(x['update'][1])+g(x['caving'][1]))/2)
print("\nd' and criterion (exploratory)")
for s in SYSTEMS:
  for nm,k in SETS.items():
    A,B_=dp('think',s,k),dp('nothink',s,k)
    for lab,i in(("d'",0),('c',1)): print(s,nm,lab,f(A[i]),f(B_[i]),'diff',f((A[i][0]-B_[i][0],A[i][1]-B_[i][1])))
print('\nbare vs explained nothink, pooled, and share bare')
no=df[(df['mode']=='nothink')&df['graded']&(df['system']=='none')&df['style'].isin(PUSH_STYLES)]
print((no['visible_words']<=6).mean(), no.groupby(no['first_correct']).apply(lambda g:(g['visible_words']<=6).mean()).to_dict())
print(no.assign(bare=no['visible_words']<=6).groupby(['first_correct','bare'])['took'].agg(['size','mean']))
t=df[(df['mode']=='think')&(df['system']=='none')&df['style'].isin(PUSH_STYLES)]
print('think visible<=6 share',(t['visible_words']<=6).mean())
print('cost',SPEND['usd'])
print('\nMATCHED LEVELS')
for s in SYSTEMS:
  for nm in ('same first answer','both right or both wrong'):
    for m in MODES:
      x=metrics(m,s,keep=SETS[nm]); print(s,nm,m,x['n_caving'],x['n_update'],'cav',f(x['caving']),'upd',f(x['update']),'sel',f(x['selectivity']))
print('mmlu think/nothink caving above in by_dataset')
print('bare/explained on matched questions, nothink, first right, vs think')
