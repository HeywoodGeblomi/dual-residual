import sys, json, datetime; sys.dont_write_bytecode=True
import harness, variants_t1
vid=sys.argv[1]; fn,defn=variants_t1.VARIANTS[vid]
h=harness.code_hash(fn); res=harness.evaluate(fn)
json.dump(dict(id=vid,definition=defn,code_sha256=h,results=res),open(f'results/{vid}.json','w'),indent=1)
L=[f"\n## {vid}  ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M ET')})",f"- Definition: {defn}",f"- Code sha256 (variant fn source + harness): `{h}`"]
for N in (1024,4096):
    r=res[N]; ts=', '.join(f"{k} {v:.3f}" for k,v in r['tier_share'].items())
    L.append(f"- N={N} (n={r['windows']}): flip {r['flip']:.4f} [{'PASS' if r['bar2'] else 'FAIL'}] | sep |sd| V med {r['medS_V']:.4f} vs None med {r['medS_None']:.4f}, MW p={r['mw_p']:.3g} [{'PASS' if r['bar1'] else 'FAIL'}] | tiers {ts}; top {r['top_tier']} {r['top_share']:.3f} [{'PASS' if r['bar3'] else 'FAIL'}] | shuffle own_V {r['own_V']:.3f} vs shuf {r['own_V_shuf']:.3f}, gap {r['shuf_gap']*100:+.1f} pts, McNemar b={r['mcnemar_b']} c={r['mcnemar_c']} p={r['shuf_p']:.3g} [{'PASS' if r['bar4'] else 'FAIL'}] | owned-on-None {r['own_None']:.3f}")
L.append(f"- ALL BARS: {'PASS' if res['PASS_ALL'] else 'FAIL'}")
open('VARIANTS_LOG.md','a').write('\n'.join(L)+'\n')
print('\n'.join(L))
