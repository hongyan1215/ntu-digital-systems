#!/usr/bin/env python3
"""Render a GTKWave-style waveform PNG from a VCD file.

Matches the signal order in lab2.sav. Time window configurable.
"""
import sys
from vcdvcd import VCDVCD
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

VCD_FILE = sys.argv[1]
OUT_PNG  = sys.argv[2]
T0 = int(sys.argv[3])
T1 = int(sys.argv[4])
TITLE = sys.argv[5] if len(sys.argv) > 5 else ""

# signals from lab2.sav, in display order
SIGS = [
    ("A",         "mult_tb.A[3:0]",          "bus"),
    ("B",         "mult_tb.B[3:0]",          "bus"),
    ("clock",     "mult_tb.clock",           "bit"),
    ("pp0[3:0]",  "mult_tb.mult.pp0[3:0]",   "bus"),
    ("pp1[4:1]",  "mult_tb.mult.pp1[4:1]",   "bus"),
    ("pp2[5:2]",  "mult_tb.mult.pp2[5:2]",   "bus"),
    ("pp3[6:3]",  "mult_tb.mult.pp3[6:3]",   "bus"),
    ("sum1[5:1]", "mult_tb.mult.sum1[5:1]",  "bus"),
    ("sum3[7:3]", "mult_tb.mult.sum3[7:3]",  "bus"),
    ("sum1_s1[5:0]","mult_tb.mult.sum1_s1[5:0]","bus"),
    ("sum3_s1[7:2]","mult_tb.mult.sum3_s1[7:2]","bus"),
    ("sum2[7:2]", "mult_tb.mult.sum2[7:2]",  "bus"),
    ("P[7:0]",    "mult_tb.P[7:0]",          "bus"),
    ("P_ref[7:0]","mult_tb.P_ref[7:0]",      "bus"),
]

vcd = VCDVCD(VCD_FILE)
refs = vcd.references_to_ids

def fetch(sig):
    # match best
    cand = [r for r in refs if r == sig]
    if not cand:
        # try without index suffix
        base = sig.split("[")[0]
        cand = [r for r in refs if r.startswith(base)]
    if not cand:
        return None
    return vcd[cand[0]].tv  # list of (time, value)

def val_str(v):
    if v is None: return "X"
    if isinstance(v, str):
        if all(c in "01" for c in v):
            try: return f"{int(v,2)}"
            except: return v
        return v
    return str(v)

def transitions_in(tv, t0, t1):
    """Return list of (t, value) covering [t0,t1] including the boundary state."""
    out = []
    last_val = None
    for t, v in tv:
        if t <= t0:
            last_val = v
        elif t0 < t <= t1:
            if not out:
                out.append((t0, last_val))
            out.append((t, v))
        else:
            break
    if not out:
        out.append((t0, last_val))
    out.append((t1, out[-1][1]))
    return out

fig, ax = plt.subplots(figsize=(14, 0.55 * len(SIGS) + 1.2))
row_h = 0.8
y_pos = {}
for idx, (name, full, kind) in enumerate(SIGS):
    y = len(SIGS) - 1 - idx
    y_pos[name] = y
    ax.text(T0 - (T1 - T0) * 0.005, y + 0.4, name, ha='right', va='center',
            fontsize=9, family='monospace')

# draw signals
for idx, (name, full, kind) in enumerate(SIGS):
    y = y_pos[name]
    tv = fetch(full)
    if tv is None:
        ax.text((T0+T1)/2, y+0.4, "(missing)", ha='center', va='center', color='red')
        continue
    segs = transitions_in(tv, T0, T1)
    if kind == "bit":
        # binary square wave
        for i in range(len(segs)-1):
            t_a, v_a = segs[i]
            t_b, _   = segs[i+1]
            level = 0.8 if v_a == "1" else 0.05
            ax.plot([t_a, t_b], [y+level, y+level], color="lime", lw=1.4)
            if i+1 < len(segs)-0:
                next_v = segs[i+1][1]
                if next_v != v_a:
                    nl = 0.8 if next_v == "1" else 0.05
                    ax.plot([t_b, t_b], [y+level, y+nl], color="lime", lw=1.4)
    else:
        # bus: hexagons with value label
        for i in range(len(segs)-1):
            t_a, v_a = segs[i]
            t_b, _   = segs[i+1]
            if v_a is None: continue
            label = val_str(v_a)
            edge = min((t_b-t_a)*0.05, (T1-T0)*0.005)
            # hexagon outline
            ax.plot([t_a+edge, t_b-edge, t_b, t_b-edge, t_a+edge, t_a, t_a+edge],
                    [y+0.05, y+0.05, y+0.4, y+0.8, y+0.8, y+0.4, y+0.05],
                    color="cyan", lw=1.0)
            ax.text((t_a+t_b)/2, y+0.42, label, ha='center', va='center',
                    fontsize=7, color='white', family='monospace')

# clock cycle gridlines
# detect from clock signal
clk_tv = fetch("mult_tb.clock")
if clk_tv:
    for t,v in clk_tv:
        if T0 <= t <= T1 and v == "1":
            ax.axvline(t, color="#333", lw=0.4, zorder=-1)

ax.set_xlim(T0, T1)
ax.set_ylim(-0.3, len(SIGS) + 0.3)
ax.set_yticks([])
ax.set_xlabel("Time (ticks)")
ax.set_title(TITLE)
ax.set_facecolor("#111")
fig.patch.set_facecolor("#222")
ax.tick_params(colors='white')
ax.xaxis.label.set_color('white')
ax.title.set_color('white')
for s in ax.spines.values():
    s.set_color('#666')

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=150, facecolor=fig.get_facecolor())
print(f"wrote {OUT_PNG}")
