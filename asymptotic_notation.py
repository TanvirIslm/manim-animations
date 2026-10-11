from __future__ import annotations

import itertools
import json
import math
import os
from functools import lru_cache

import numpy as np
from manim import *
from manim.animation.animation import prepare_animation

# ═══════════════════════════════ 1.  CONFIG ═══════════════════════════════
FONT_BN = "Noto Sans Bengali"
FONT_EN = "Noto Sans"
SHOW_CAPTIONS = False        # burn the Bengali narration as subtitles (turn off if you add your own)

BG = "#0E1621"
C_TXT = "#F1F5F9"
C_DIM = "#7B8CA3"
C_PANEL = "#1B2636"
C_O1 = "#4ADE80"     # O(1)      green
C_LOG = "#38BDF8"    # O(log n)  blue
C_N = "#FB923C"      # O(n)      orange
C_BAD = "#F87171"    # warning / red
C_HI = "#FACC15"     # highlight / yellow

CAP_Y = -3.15        # subtitle zone  : y in [-3.9, -2.45]
STAGE_BOT = -2.40    # nothing from the stage may go below this
N_X = 0.9            # left edge of the right-hand info column (data cues)

# ═══════════════════════ 2.  TIMING TABLE  (key, seconds, caption) ═══════════════════════
CUES = [
    ("hook_q", 5.5, "একটা algorithm ১ সেকেন্ডে কাজ করছে—\nতাহলে সেটা কি ভালো algorithm?"),
    ("hook_good", 3.0, "অবশ্যই ভালো মনে হচ্ছে, তাই না?"),
    ("hook_wait", 2.0, "কিন্তু অপেক্ষা করুন..."),
    ("data_100", 3.5, "আজ আপনার কাছে আছে মাত্র ১০০টা data।"),
    ("data_1m", 3.0, "কাল সেটা হয়ে গেল ১০ লাখ।"),
    ("time_10min", 5.0, "আর আপনার সেই “১ সেকেন্ডের” algorithm\nতখন নিতে শুরু করল ১০ মিনিট!"),
    ("more_data", 2.2, "আর data যদি আরও বাড়ে?"),
    ("hours", 2.5, "হয়তো ঘণ্টার পর ঘণ্টা!"),
    ("question_intro", 1.8, "তাহলে প্রশ্ন হলো—"),
    ("question", 6.5, "একটা algorithm-এর input বাড়তে থাকলে,\nতার performance আসলে কীভাবে বদলায়?"),
    ("leads_to", 4.5, "এই প্রশ্নের উত্তরই আমাদের নিয়ে যায়\nএকটা খুব গুরুত্বপূর্ণ ধারণার কাছে—"),
    ("title", 2.0, "Asymptotic Notation।"),
    ("simple_def", 3.5, "সহজ ভাষায়, Asymptotic Notation আমাদের বলে—"),
    ("def_growth", 5.0, "input যত বড় হবে,\nalgorithm-এর কাজের পরিমাণ কত দ্রুত বাড়বে।"),
    # ---- O(1)
    ("o1_list", 2.8, "ধরুন, আপনার কাছে একটা list আছে।"),
    ("o1_first", 3.5, "আপনাকে শুধু প্রথম element-টা বের করতে হবে।"),
    ("o1_sizes", 6.0, "List-এ ১০টা data থাকুক, ১০০টা থাকুক,\nঅথবা ১০ লাখ data থাকুক—"),
    ("o1_access", 4.0, "আপনাকে শুধু সেই নির্দিষ্ট জায়গায়\nএকবার access করতে হবে।"),
    ("o1_same", 2.5, "কাজের পরিমাণ প্রায় একই।"),
    ("o1_name", 4.7, "এটা হলো— O(1), যাকে বলা হয় Constant Time।"),
    # ---- O(n)
    ("on_find", 5.0, "এবার ধরুন, একটা list-এর মধ্যে\nআপনাকে একটা নির্দিষ্ট নাম খুঁজতে হবে।"),
    ("on_check", 3.8, "আপনি যদি একটার পর একটা নাম check করেন—"),
    ("on_counts", 7.0, "১০টা data হলে সর্বোচ্চ ১০টা check, ১০০টা হলে ১০০টা,\nআর ১০ লাখ হলে?"),
    ("on_million", 2.0, "১০ লাখ check!"),
    ("on_linear", 4.5, "অর্থাৎ input যত বাড়ছে,\nকাজও প্রায় একই হারে বাড়ছে।"),
    ("on_name", 3.0, "এটা হলো— O(n), Linear Time।"),
    # ---- O(log n)
    ("ol_halve", 8.0, "কিন্তু এবার এমন একটা algorithm কল্পনা করুন,\nযেটা প্রতিবার সিদ্ধান্ত নেওয়ার পর\ndata-এর অর্ধেক বাদ দিয়ে দিতে পারে।"),
    ("ol_steps", 7.5, "১০ লাখ data থেকে—৫ লাখ বাদ,\nতারপর আবার অর্ধেক, তারপর আবার অর্ধেক..."),
    ("ol_shrink", 3.5, "প্রতিটি step-এ search space ছোট হতে থাকে।"),
    ("ol_slow", 4.5, "তাই data বিশাল হলেও\nপ্রয়োজনীয় step খুব ধীরে বাড়ে।"),
    ("ol_name", 3.5, "এটাই— O(log n), Logarithmic Time।"),
    # ---- recap
    ("sum_intro", 2.5, "তাহলে খুব সহজভাবে মনে রাখুন—"),
    ("sum_o1", 3.5, None),
    ("sum_log", 4.0, None),
    ("sum_n", 4.5, None),
    # ---- why it matters
    ("why_matters", 3.5, "আর এখানেই Asymptotic Notation-এর আসল গুরুত্ব।"),
    ("why_100", 4.5, "কারণ ১০০টা data-তে একটা algorithm\nভালো কাজ করলেই হবে না।"),
    ("why_big", 7.0, "আমাদের জানতে হবে—\ndata যদি ১০ হাজার হয়? ১০ লাখ হয়? ১০ কোটি হয়?"),
    ("why_what", 2.5, "তখন algorithm-এর কী হবে?"),
    ("prog_now", 6.0, "কারণ একজন programmer শুধু জানতে চায় না—\n“আমার code এখন কত দ্রুত?”"),
    ("prog_big", 6.5, "সে জানতে চায়—\n“Data অনেক বড় হলে, আমার code কতটা ভালো থাকবে?”"),
    ("language", 5.5, "আর algorithm-এর এই growth বোঝানোর ভাষাই হলো—\nAsymptotic Notation।"),
    ("symbols", 4.5, "O(1), O(log n), O(n)—\nএগুলো শুধু কিছু symbol নয়।"),
    ("final", 7.0, "এগুলো বলে দেয়, input বড় হলে আপনার algorithm-এর\nperformance কোথায় গিয়ে দাঁড়াতে পারে।"),
]

try:
    _current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _current_dir = os.getcwd()

_json = os.path.join(_current_dir, "durations.json")
if os.path.exists(_json):
    with open(_json, encoding="utf-8") as _f:
        _over = json.load(_f)
    CUES = [(k, float(_over.get(k, s)), c) for k, s, c in CUES]


# ═══════════════════════════ 3.  FRAME-EXACT TIME HELPERS ═══════════════════════════
@lru_cache(maxsize=None)
def frame_safe(k: int, fps: float) -> float:
    dt = 1 / fps
    base = k / fps
    sp = np.spacing(base)
    for j in range(200):
        for sgn in (-1, 1):
            c = base + sgn * j * sp
            if len(np.arange(0, c, dt)) == k:
                return float(c)
    return base


# ═══════════════════════════ 4.  SMALL DRAWING HELPERS ═══════════════════════════
def _is_bn(s: str) -> bool:
    return any("\u0980" <= ch <= "\u09FF" for ch in s)

def T(s, size=32, color=C_TXT, bold=False):
    return Text(s, font=FONT_BN if _is_bn(s) else FONT_EN, font_size=size,
                color=color, weight=BOLD if bold else NORMAL)

def overlay(m):
    m._ov_ok = True
    return m

def icon_check(col=C_O1, r=0.32):
    c = Circle(radius=r, stroke_color=col, stroke_width=4, fill_color=col, fill_opacity=0.15)
    v = VMobject(stroke_color=col, stroke_width=6)
    v.set_points_as_corners([[-.5 * r, 0, 0], [-.12 * r, -.38 * r, 0], [.55 * r, .42 * r, 0]])
    return VGroup(c, v)

def icon_cross(col=C_BAD, r=0.32):
    c = Circle(radius=r, stroke_color=col, stroke_width=4, fill_color=col, fill_opacity=0.15)
    a = Line([-.4 * r, -.4 * r, 0], [.4 * r, .4 * r, 0], stroke_color=col, stroke_width=6)
    b = Line([-.4 * r, .4 * r, 0], [.4 * r, -.4 * r, 0], stroke_color=col, stroke_width=6)
    return VGroup(c, a, b)

def icon_warn(col=C_BAD, r=0.36):
    tri = RegularPolygon(3, stroke_color=col, stroke_width=4, fill_color=col, fill_opacity=0.15).scale(r)
    ex = T("!", 26, col, bold=True).move_to(tri.get_center() + DOWN * 0.04)
    return VGroup(tri, ex)

def card(txt, color, w=3.2, h=1.0, size=34):
    rect = RoundedRectangle(width=w, height=h, corner_radius=0.18, stroke_color=color,
                            stroke_width=4, fill_color=C_PANEL, fill_opacity=1)
    t = T(txt, size, color).move_to(rect)
    g = VGroup(rect, t)
    g.rect, g.txt = rect, t
    return g

def box(txt, w, h, stroke, size=32, fill=C_PANEL):
    r = RoundedRectangle(width=w, height=h, corner_radius=0.2, stroke_color=stroke,
                         stroke_width=4, fill_color=fill, fill_opacity=1)
    return VGroup(r, T(txt, size, C_TXT).move_to(r))

def dot_grid(rows, cols, radius, buff, color):
    g = VGroup(*[Dot(radius=radius, color=color, stroke_width=0) for _ in range(rows * cols)])
    return g.arrange_in_grid(rows, cols, buff=buff)

def make_stopwatch(center):
    face = Circle(radius=1.0, stroke_color=WHITE, stroke_width=5, fill_color=C_PANEL, fill_opacity=1)
    ticks = VGroup(*[Line(UP * 0.80, UP * 0.94, stroke_width=3, color=C_DIM)
                     .rotate(-i * TAU / 12, about_point=ORIGIN) for i in range(12)])
    knob = RoundedRectangle(width=0.36, height=0.18, corner_radius=0.05, fill_color=WHITE,
                            fill_opacity=1, stroke_width=0).next_to(face, UP, buff=0)
    hub = Dot(radius=0.06, color=C_HI)
    body = VGroup(face, ticks, knob, hub).move_to(center)
    hand = overlay(Line(center, center + UP * 0.72, color=C_HI, stroke_width=6))
    return body, hand

def bracket_below(mob, buff=0.12, tick=0.15, color=C_DIM):
    l, r, y = mob.get_left()[0], mob.get_right()[0], mob.get_bottom()[1] - buff
    v = VMobject(stroke_color=color, stroke_width=4)
    v.set_points_as_corners([[l, y + tick, 0], [l, y, 0], [r, y, 0], [r, y + tick, 0]])
    return v

def make_array(vals, w, h, y, size=28, gap=0.06):
    cells = VGroup()
    for v in vals:
        r = Rectangle(width=w, height=h, stroke_color=WHITE, stroke_width=3,
                      fill_color=C_PANEL, fill_opacity=1)
        cells.add(VGroup(r, T(str(v), size).move_to(r)))
    cells.arrange(RIGHT, buff=gap).move_to([0, y, 0])
    return cells

def f_one(x): return 0.8
def f_log(x): return math.log(1 + x)
def f_lin(x): return x


# ═══════════════════════════ 5.  SYNC BASE SCENE ═══════════════════════════
class SyncScene(Scene):
    def setup(self):
        self.frames = 0
        self.fps = float(config.frame_rate)
        self._missing_sfx = set()

    def play_sfx(self, filename: str):
        """Safely play a sound effect. If file is missing, it won't crash."""
        if os.path.exists(filename):
            self.add_sound(filename)
        else:
            if filename not in self._missing_sfx:
                print(f"[AUDIO] SFX missing (skipped): {filename}")
                self._missing_sfx.add(filename)

    def play(self, *args, **kwargs):
        fps = self.fps
        anims = [prepare_animation(a) for a in args]
        rt = kwargs.get("run_time")
        if rt is not None:
            k = max(1, round(rt * fps))
            kwargs["run_time"] = frame_safe(k, fps)
            n = k
        else:
            n = 1
            for a in anims:
                k = max(1, round(a.run_time * fps))
                a.run_time = frame_safe(k, fps)
                n = max(n, k)
        self.frames += n
        super().play(*anims, **kwargs)

    def hold(self, nframes: int):
        if nframes > 0:
            self.wait(nframes / self.fps, frozen_frame=False)


class AsymptoticNotation(SyncScene):
    def construct(self):
        self.camera.background_color = BG
        self.keep_ids: set[int] = set()
        self.cap = None
        self.header = None
        fps = self.fps
        cum, self.cum_frames = 0.0, 0
        for key, secs, cap in CUES:
            self.cue_key = key
            self.cue_start = self.cum_frames
            cum += secs
            self.target = round(cum * fps)
            self.set_caption(cap)
            getattr(self, "cue_" + key)(secs)
            self.lint(key)
            rem = self.target - self.frames
            if rem < 0:
                print(f"[TIMING] cue '{key}' overran its {secs:.2f}s slot by {-rem / fps:.2f}s ")
            else:
                self.hold(rem)
            self.cum_frames = self.target
        total = self.frames / fps
        print(f"[TIMING] total = {total:.3f}s  ({self.frames} frames @ {fps:g} fps)")

    def at(self, t: float):
        want = self.cue_start + round(t * self.fps)
        rem = want - self.frames
        if rem > 0:
            self.hold(rem)

    def set_caption(self, text):
        if self.cap is not None:
            self.remove(self.cap)
            self.cap = None
        if not (SHOW_CAPTIONS and text):
            return
        lines = VGroup(*[T(s, 28, C_TXT) for s in text.split("\n")]).arrange(DOWN, buff=0.1)
        if lines.width > 12.4:
            lines.scale_to_fit_width(12.4)
        lines.move_to([0, CAP_Y, 0]).set_z_index(100)
        self.cap = lines
        self.keep_ids.add(id(lines))
        self.add(lines)

    def clear_stage(self, rt=0.4):
        gone = [m for m in self.mobjects if id(m) not in self.keep_ids]
        for m in gone:
            m.clear_updaters()
        if gone:
            self.play_sfx("sounds/whoosh.wav")  # Sound for clearing stage
            self.play(*[FadeOut(m) for m in gone], run_time=rt)

    def retext(self, old, new, rt=0.5, also=()):
        h = rt / 2
        self.play(old.animate.set_opacity(0), *also, run_time=h)
        new.set_opacity(0)
        old.become(new)
        self.play(old.animate.set_opacity(1), run_time=h)

    def swap(self, old, new, t_out=0.25, t_in=0.35):
        self.play(FadeOut(old), run_time=t_out)
        self.play(FadeIn(new), run_time=t_in)

    def lint(self, key):
        items = [m for m in self.mobjects if id(m) not in self.keep_ids and not getattr(m, "_ov_ok", False) and not isinstance(m, ValueTracker)]
        for m in items:
            l, r, b, t = self._bb(m)
            if l < -6.95 or r > 6.95 or t > 3.95 or b < -3.95: pass
        for a, c in itertools.combinations(items, 2):
            pass 

    @staticmethod
    def _bb(m):
        return m.get_left()[0], m.get_right()[0], m.get_bottom()[1], m.get_top()[1]

    def make_chart(self, center, xlen, ylen, xlab="n (input size)", ylab="work"):
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], x_length=xlen, y_length=ylen, tips=True,
                  axis_config={"include_numbers": False, "include_ticks": False,
                               "stroke_color": C_DIM, "stroke_width": 3,
                               "tip_width": 0.16, "tip_height": 0.16}).move_to(center)
        xl = T(xlab, 24, C_DIM).move_to([ax.get_right()[0] - 1.2, ax.get_bottom()[1] - 0.32, 0])
        yl = T(ylab, 24, C_DIM).move_to([ax.get_left()[0] + 1.2, ax.get_top()[1] + 0.30, 0])
        return ax, xl, yl

    def curve(self, ax, fn, color):
        return overlay(ax.plot(fn, x_range=[0, 10], color=color, stroke_width=7, use_smoothing=False))

    def badge(self, big, big_color, small, x=4.0):
        b = T(big, 76 if len(big) < 6 else 56, big_color, bold=True).move_to([x, 0.95, 0])
        s = VGroup(*[T(line, 38, C_TXT) for line in small.split("\n")]).arrange(DOWN, buff=0.12)
        s.move_to([x, 0.95 - b.height / 2 - 0.35 - s.height / 2, 0])
        return b, s

    # ═════════════════════════════ SCENES ═════════════════════════════
    def cue_hook_q(self, d):
        algo = box("Algorithm", 3.4, 1.6, C_LOG, 36).move_to([-3.4, 0.5, 0])
        sw, hand = make_stopwatch([3.4, 0.5, 0])
        arrow = Arrow([-1.5, 0.5, 0], [2.2, 0.5, 0], buff=0, color=C_DIM, stroke_width=5)
        lab = T("1 s", 36, C_O1, bold=True).move_to([3.4, -0.95, 0])
        self.hook = dict(algo=algo, sw=sw, hand=hand, arrow=arrow, lab=lab)
        self.play_sfx("sounds/pop.wav")
        self.play(FadeIn(algo, shift=RIGHT * 0.3), run_time=0.6)
        self.play(FadeIn(sw), FadeIn(hand), Create(arrow), run_time=0.6)
        self.at(1.5)
        self.play_sfx("sounds/tick.wav")
        self.play(Rotate(hand, angle=-TAU, about_point=sw[0].get_center(), rate_func=linear), run_time=1.0)
        self.play(Write(lab), run_time=0.5)
        self.at(3.4)
        self.v_q = T("Good algorithm?", 34, C_HI).move_to([0, -1.6, 0])
        self.play(FadeIn(self.v_q, shift=UP * 0.15), run_time=0.6)

    def cue_hook_good(self, d):
        self.play(FadeOut(self.v_q), run_time=0.25)
        icon = icon_check(C_O1)
        txt = T("Looks good!", 34, C_O1)
        self.v_good = VGroup(icon, txt).arrange(RIGHT, buff=0.25).move_to([0, -1.6, 0])
        self.play_sfx("sounds/success.wav")
        self.play(FadeIn(self.v_good, scale=0.6), run_time=0.5)
        self.play(Indicate(self.hook["lab"], color=C_O1, scale_factor=1.25), run_time=0.8)

    def cue_hook_wait(self, d):
        self.play(FadeOut(self.v_good), run_time=0.25)
        self.v_warn = VGroup(icon_warn(C_BAD), T("Wait...", 34, C_BAD)).arrange(RIGHT, buff=0.25)
        self.v_warn.move_to([0, -1.6, 0])
        self.play_sfx("sounds/error.wav")
        self.play(FadeIn(self.v_warn, scale=1.4), run_time=0.4)
        self.play(Indicate(self.v_warn, color=C_BAD, scale_factor=1.15), run_time=0.8)

    def n_text(self, v):
        return T(f"n = {v:,}", 46, C_TXT, bold=True).move_to([N_X, 1.0, 0], aligned_edge=LEFT)

    def count_n(self, a, b, rt):
        la, lb = math.log10(a), math.log10(b)
        def f(m, alpha):
            m.become(self.n_text(int(round(10 ** (la + (lb - la) * alpha)))))
        self.play(UpdateFromAlphaFunc(self.nlab, f, rate_func=smooth, run_time=rt))

    def cue_data_100(self, d):
        self.clear_stage(0.5)
        self.grid = dot_grid(10, 10, 0.07, 0.18, C_LOG).move_to([-3.0, 0.3, 0])
        self.nlab = self.n_text(100)
        self.tcard = card("time: 1 s", C_O1, w=3.2).move_to([N_X + 1.6, -0.4, 0])
        self.at(0.5)
        self.play_sfx("sounds/pop.wav")
        self.play(LaggedStart(*[FadeIn(x, scale=0.3) for x in self.grid], lag_ratio=0.012), run_time=1.3)
        self.at(2.0)
        self.play(Write(self.nlab), run_time=0.6)
        self.at(2.7)
        self.play(FadeIn(self.tcard, shift=LEFT * 0.3), run_time=0.6)

    def cue_data_1m(self, d):
        big = dot_grid(24, 50, 0.022, 0.05, C_LOG).move_to([-3.0, 0.3, 0])
        self.play_sfx("sounds/whoosh.wav")
        self.play(FadeOut(self.grid), FadeIn(big), run_time=0.8)
        self.grid = big
        self.count_n(100, 1_000_000, 1.6)
        self.play(Indicate(self.nlab, color=C_HI, scale_factor=1.08), run_time=0.5)

    def cue_time_10min(self, d):
        bar_bg = RoundedRectangle(width=3.2, height=0.26, corner_radius=0.13, stroke_color=C_DIM,
                                  stroke_width=2).move_to([N_X + 1.6, -1.3, 0])
        self.bar_bg = bar_bg
        self.play(Indicate(self.tcard, color=C_O1, scale_factor=1.1), run_time=0.8)
        self.at(1.5)
        self.add(bar_bg)

        def fill(m, alpha, col=C_HI):
            w = max(3.2 * alpha, 0.02)
            m.become(overlay(Rectangle(width=w, height=0.16, fill_color=col, fill_opacity=1, stroke_width=0)
                             .move_to(bar_bg.get_left() + RIGHT * w / 2)))
        self.bar_fill = overlay(Rectangle(width=0.02, height=0.16, fill_opacity=1, stroke_width=0)
                                .move_to(bar_bg.get_left()))
        self.add(self.bar_fill)
        self.play_sfx("sounds/slide.wav")
        self.play(UpdateFromAlphaFunc(self.bar_fill, fill, rate_func=linear), run_time=1.7)
        self.at(3.3)
        new_t = T("time: 10 min", 34, C_BAD).move_to(self.tcard.rect)
        self.play_sfx("sounds/error.wav")
        self.retext(self.tcard.txt, new_t, 0.7,
                    also=[self.tcard.rect.animate.set_stroke(C_BAD), self.bar_fill.animate.set_fill(C_BAD)])
        self.play(Indicate(self.tcard, color=C_BAD, scale_factor=1.1), run_time=0.8)

    def cue_more_data(self, d):
        new_t = T("time: ?", 34, C_HI).move_to(self.tcard.rect)
        self.play_sfx("sounds/pop.wav")
        self.retext(self.tcard.txt, new_t, 0.6,
                    also=[self.tcard.rect.animate.set_stroke(C_HI), FadeOut(self.bar_fill), FadeOut(self.bar_bg)])
        self.count_n(1_000_000, 100_000_000, 1.5)

    def cue_hours(self, d):
        new_t = T("time: hours...", 34, C_BAD).move_to(self.tcard.rect)
        self.play_sfx("sounds/error.wav")
        self.retext(self.tcard.txt, new_t, 0.6, also=[self.tcard.rect.animate.set_stroke(C_BAD)])
        self.play(Indicate(self.tcard, color=C_BAD, scale_factor=1.12), run_time=0.9)

    def cue_question_intro(self, d):
        self.clear_stage(0.5)
        q = T("?", 170, C_HI, bold=True).move_to([0, 0.3, 0])
        self.big_q = q
        self.play_sfx("sounds/ding.wav")
        self.play(FadeIn(q, scale=0.4), run_time=0.9)

    def cue_question(self, d):
        self.play(FadeOut(self.big_q), run_time=0.4)
        ax, xl, yl = self.make_chart([0, 0.2, 0], 8.0, 3.8, "input size (n)", "time / work")
        self.q_ax, self.q_xl, self.q_yl = ax, xl, yl
        self.play(Create(ax), run_time=0.8)
        self.play(FadeIn(xl), FadeIn(yl), run_time=0.4)
        self.at(1.9)
        dot = overlay(Dot(ax.c2p(0, 0), color=C_LOG, radius=0.1))
        self.add(dot)
        self.play_sfx("sounds/slide.wav")
        self.play(dot.animate.move_to(ax.c2p(9.6, 0)), run_time=1.6, rate_func=linear)
        self.play(FadeOut(dot), run_time=0.2)
        self.at(3.9)
        crv = overlay(DashedVMobject(ax.plot(lambda x: 0.9 + 0.08 * x ** 2, x_range=[0, 10],
                                             color=C_HI, stroke_width=7), num_dashes=30))
        self.q_curve = crv
        self.play_sfx("sounds/whoosh.wav")
        self.play(Create(crv), run_time=1.4)
        qm = T("?", 60, C_HI, bold=True).move_to(ax.c2p(10, 8.9) + RIGHT * 0.75)
        self.q_mark = qm
        self.play_sfx("sounds/pop.wav")
        self.play(FadeIn(qm, scale=0.5), run_time=0.4)
        self.play(Indicate(qm, color=C_HI, scale_factor=1.3), run_time=0.7)

    def cue_leads_to(self, d):
        grp = VGroup(self.q_ax, self.q_xl, self.q_yl, self.q_curve, self.q_mark)
        for m in grp: m._ov_ok = True
        self.play(grp.animate.scale(0.55).move_to([-3.9, 0.4, 0]), run_time=1.0)
        concept = box("A key\nconcept", 4.4, 2.2, C_HI, 38).move_to([3.3, 0.4, 0])
        arrow = Arrow([-1.2, 0.4, 0], [0.9, 0.4, 0], buff=0, color=C_HI, stroke_width=6)
        self.at(1.8)
        self.play_sfx("sounds/pop.wav")
        self.play(Create(arrow), run_time=0.6)
        self.play(FadeIn(concept, scale=0.8), run_time=0.7)
        self.play(Indicate(concept, color=C_HI, scale_factor=1.06), run_time=0.8)

    def cue_title(self, d):
        self.clear_stage(0.5)
        t = T("Asymptotic Notation", 68, C_TXT, bold=True).move_to([0, 0.3, 0])
        t.set_color_by_gradient(C_LOG, C_O1)
        ul = Line(t.get_left() + DOWN * 0.65, t.get_right() + DOWN * 0.65, color=C_HI, stroke_width=5)
        self.title_mob, self.title_ul = t, ul
        self.play_sfx("sounds/success.wav")
        self.play(Write(t), run_time=1.1)
        self.play(Create(ul), run_time=0.4)

    def cue_simple_def(self, d):
        hdr = T("Asymptotic Notation", 22, C_DIM).to_corner(UL, buff=0.3)
        self.header = hdr
        self.keep_ids.add(id(hdr))
        self.play(FadeOut(self.title_ul), ReplacementTransform(self.title_mob, hdr), run_time=0.9)
        self.at(1.6)
        tells = T("tells us ...", 62, C_HI, bold=True).move_to([0, 0.3, 0])
        self.play(Write(tells), run_time=0.9)
        self.tells = tells

    def cue_def_growth(self, d):
        self.play(FadeOut(self.tells), run_time=0.4)
        base_y, x_n, x_w = -1.4, -2.0, 2.0
        base = overlay(Line([-3.6, base_y, 0], [3.6, base_y, 0], color=C_DIM, stroke_width=4))
        lab_n = T("Input size (n)", 28, C_LOG).move_to([x_n, -1.9, 0])
        lab_w = T("Work done", 28, C_N).move_to([x_w, -1.9, 0])
        vt = ValueTracker(0)

        def bar(x, col, fn):
            def mk():
                h = fn(vt.get_value())
                return Rectangle(width=1.2, height=h, fill_color=col, fill_opacity=0.95,
                                 stroke_width=0).move_to([x, base_y + h / 2, 0])
            return overlay(always_redraw(mk))
        bn = bar(x_n, C_LOG, lambda t: 0.3 + 2.0 * t)
        bw = bar(x_w, C_N, lambda t: 0.2 + 3.0 * t ** 1.8)
        arr = Arrow([-1.2, 0.2, 0], [1.2, 0.2, 0], buff=0, color=C_DIM, stroke_width=4)
        self.play_sfx("sounds/pop.wav")
        self.play(FadeIn(base), FadeIn(lab_n), FadeIn(lab_w), FadeIn(arr), run_time=0.5)
        self.add(bn, bw)
        self.at(0.9)
        self.play_sfx("sounds/slide.wav")
        self.play(vt.animate.set_value(1), run_time=2.8, rate_func=smooth)
        self.at(3.8)
        q = T("how fast?", 36, C_HI, bold=True).move_to([x_w, 2.35, 0])
        self.play_sfx("sounds/ding.wav")
        self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.4)
        self.play(Indicate(q, color=C_HI, scale_factor=1.2), run_time=0.6)

    def cue_o1_list(self, d):
        self.clear_stage(0.4)
        cells = make_array([7, 3, 9, 1, 8, 2, 6, 4, 5, 0], 0.8, 0.8, 0.9)
        idx = VGroup(*[T(str(i), 22, C_DIM).next_to(c, DOWN, buff=0.12) for i, c in enumerate(cells)])
        lab = T("list", 28, C_LOG, bold=True).move_to([-5.15, 0.9, 0])
        self.cells, self.idx, self.listlab = cells, idx, lab
        self.play_sfx("sounds/whoosh.wav")
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cells], lag_ratio=0.1), run_time=1.3)
        self.play(FadeIn(idx), FadeIn(lab), run_time=0.5)

    def cue_o1_first(self, d):
        c0 = self.cells[0]
        x = c0.get_center()[0]
        hl = overlay(SurroundingRectangle(c0, color=C_HI, buff=0.05, stroke_width=6))
        ptr = Arrow([x, 2.2, 0], [x, c0.get_top()[1] + 0.12, 0], buff=0, color=C_HI, stroke_width=6)
        pl = T("list[0]", 30, C_HI, bold=True).move_to([x + 0.15, 2.62, 0])
        self.hl, self.ptr, self.ptrlab = hl, ptr, pl
        self.play_sfx("sounds/click.wav")
        self.play(Create(hl), run_time=0.5)
        self.play(FadeIn(ptr, shift=DOWN * 0.2), FadeIn(pl), run_time=0.6)
        self.play(Indicate(c0, color=C_HI, scale_factor=1.15), run_time=0.8)

    def cue_o1_sizes(self, d):
        grp = VGroup(self.cells, self.idx)
        br = bracket_below(grp, buff=0.24, tick=0.12)
        self.nlab1 = T("n = 10", 40, C_TXT, bold=True).move_to([0, -0.55, 0])
        self.work = card("work: 1 step", C_O1, w=3.6, h=0.9, size=32).move_to([0, -1.7, 0])
        self.play(Create(br), FadeIn(self.nlab1), run_time=0.6)
        self.br = br
        self.at(0.9)
        self.play_sfx("sounds/pop.wav")
        self.play(FadeIn(self.work, shift=UP * 0.2), run_time=0.5)
        for t_at, val in ((1.9, "n = 100"), (3.5, "n = 1,000,000")):
            self.at(t_at)
            new = T(val, 40, C_TXT, bold=True).move_to([0, -0.55, 0])
            self.play_sfx("sounds/pop.wav")
            self.retext(self.nlab1, new, 0.5)
            self.play(Indicate(self.cells[0], color=C_HI, scale_factor=1.12), run_time=0.6)

    def cue_o1_access(self, d):
        self.at(0.3)
        nt = T("accesses: 1", 32, C_O1).move_to(self.work.rect)
        self.retext(self.work.txt, nt, 0.5)
        self.play_sfx("sounds/click.wav")
        self.play(self.ptr.animate.shift(DOWN * 0.25), run_time=0.25)
        self.play(self.ptr.animate.shift(UP * 0.25), run_time=0.25)
        self.play_sfx("sounds/ding.wav")
        self.play(Flash(self.cells[0], color=C_HI, line_length=0.25, flash_radius=0.7), run_time=0.8)

    def cue_o1_same(self, d):
        self.clear_stage(0.5)
        ax, xl, yl = self.make_chart([-2.4, 0.3, 0], 6.0, 4.0)
        self.ch = (ax, xl, yl)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.7)
        line = self.curve(ax, f_one, C_O1)
        self.o1_line = line
        self.play_sfx("sounds/slide.wav")
        self.play(Create(line), run_time=1.1)

    def cue_o1_name(self, d):
        b, s = self.badge("O(1)", C_O1, "Constant\nTime")
        self.at(1.1)
        self.play_sfx("sounds/pop.wav")
        self.play(Write(b), run_time=0.7)
        self.at(2.3)
        self.play(FadeIn(s, shift=UP * 0.2), run_time=0.7)
        self.play(Indicate(b, color=C_O1, scale_factor=1.12), run_time=0.8)
        self.badges = (b, s)

    def cue_on_find(self, d):
        self.clear_stage(0.5)
        names = ["Anika", "Rafi", "Sumi", "Tania", "Arif", "Mim", "Nabil", "Rina"]
        cells = VGroup()
        for nm in names:
            r = Rectangle(width=1.45, height=0.9, stroke_color=WHITE, stroke_width=3, fill_color=C_PANEL, fill_opacity=1)
            cells.add(VGroup(r, T(nm, 28).move_to(r)))
        cells.arrange(RIGHT, buff=0.05).move_to([0, 0.3, 0])
        self.ncells = cells
        self.play_sfx("sounds/whoosh.wav")
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cells], lag_ratio=0.1), run_time=1.4)
        self.at(2.0)
        tgt = T('Find: "Rina"', 44, C_HI, bold=True).move_to([0, 1.9, 0])
        self.play_sfx("sounds/pop.wav")
        self.play(Write(tgt), run_time=0.9)
        self.play(Indicate(tgt, color=C_HI, scale_factor=1.1), run_time=0.8)

    def cue_on_check(self, d):
        cells = self.ncells
        by = cells.get_bottom()[1] - 0.3
        ptr = Triangle(color=C_HI, fill_opacity=1, stroke_width=0).scale(0.2)
        ptr.move_to([cells[0].get_center()[0], by, 0])
        counter = T("checks: 1", 40, C_N, bold=True).move_to([0, -1.4, 0])
        self.add(ptr)
        self.add(counter)
        self.at(0.2)

        def f(p, alpha):
            i = min(int(alpha * 8), 7)
            p.move_to([cells[i].get_center()[0], by, 0])
            for j, c in enumerate(cells):
                if j < i:
                    c[0].set_fill(C_BAD, opacity=0.30)
                elif j == i:
                    c[0].set_fill(C_HI, opacity=0.35)
                else:
                    c[0].set_fill(C_PANEL, opacity=1)
            counter.become(T(f"checks: {i + 1}", 40, C_N, bold=True).move_to([0, -1.4, 0]))
        
        self.play_sfx("sounds/slide.wav")
        self.play(UpdateFromAlphaFunc(ptr, f, rate_func=linear), run_time=3.0)
        self.play_sfx("sounds/success.wav")
        self.play(cells[7][0].animate.set_fill(C_O1, opacity=0.5), run_time=0.4)
        self.chk_ptr, self.chk_counter = ptr, counter

    def cue_on_counts(self, d):
        self.clear_stage(0.5)
        def row(lt, rt, y, rcol):
            l = T(lt, 34).move_to([-0.8 - T(lt, 34).width / 2, y, 0])
            a = Arrow([-0.5, y, 0], [1.0, y, 0], buff=0, color=C_DIM, stroke_width=4)
            r = T(rt, 34, rcol, bold=True).move_to([1.3 + T(rt, 34, rcol, bold=True).width / 2, y, 0])
            return l, a, r
        r1, r2, r3 = row("10 data", "10 checks", 1.4, C_N), row("100 data", "100 checks", 0.4, C_N), row("1,000,000 data", "?", -0.6, C_HI)
        self.r3 = r3
        self.at(0.6)
        self.play(FadeIn(r1[0], shift=RIGHT * 0.2), run_time=0.5)
        self.play_sfx("sounds/pop.wav")
        self.play(Create(r1[1]), FadeIn(r1[2], shift=LEFT * 0.2), run_time=0.6)
        self.at(3.1)
        self.play(FadeIn(r2[0], shift=RIGHT * 0.2), run_time=0.5)
        self.play_sfx("sounds/pop.wav")
        self.play(Create(r2[1]), FadeIn(r2[2], shift=LEFT * 0.2), run_time=0.6)
        self.at(5.1)
        self.play(FadeIn(r3[0], shift=RIGHT * 0.2), run_time=0.5)
        self.play_sfx("sounds/ding.wav")
        self.play(Create(r3[1]), FadeIn(r3[2], scale=0.6), run_time=0.6)

    def cue_on_million(self, d):
        l, a, r = self.r3
        big = T("1,000,000 checks", 34, C_BAD, bold=True)
        big.move_to([1.3 + big.width / 2, -0.6, 0])
        self.play_sfx("sounds/error.wav")
        self.retext(r, big, 0.6)
        self.play(Indicate(r, color=C_BAD, scale_factor=1.15), run_time=0.9)

    def cue_on_linear(self, d):
        self.clear_stage(0.4)
        ax, xl, yl = self.make_chart([-2.4, 0.3, 0], 6.0, 4.0)
        self.ch = (ax, xl, yl)
        self.add(ax, xl, yl)
        self.at(0.4)
        line = self.curve(ax, f_lin, C_N)
        self.play_sfx("sounds/slide.wav")
        self.play(Create(line), run_time=1.0)
        self.on_line = line
        vt = ValueTracker(1.0)
        dot = overlay(always_redraw(lambda: Dot(ax.c2p(vt.get_value(), f_lin(vt.get_value())), color=C_HI, radius=0.11)))
        guide = overlay(always_redraw(lambda: DashedLine(ax.c2p(vt.get_value(), 0), ax.c2p(vt.get_value(), f_lin(vt.get_value())), color=C_HI, stroke_width=3)))
        self.add(guide, dot)
        self.probe = (dot, guide)
        self.play(vt.animate.set_value(9), run_time=1.6, rate_func=smooth)
        self.at(3.1)
        t1 = T("n  ×2", 40, C_LOG, bold=True).move_to([4.0, 1.0, 0])
        ar = Arrow([4.0, 0.4, 0], [4.0, -0.3, 0], buff=0, color=C_DIM, stroke_width=5)
        t2 = T("work  ×2", 40, C_N, bold=True).move_to([4.0, -0.95, 0])
        self.rcol = (t1, ar, t2)
        self.play(FadeIn(t1, shift=DOWN * 0.2), run_time=0.4)
        self.play_sfx("sounds/pop.wav")
        self.play(Create(ar), FadeIn(t2, shift=DOWN * 0.2), run_time=0.6)

    def cue_on_name(self, d):
        for m in self.probe: m.clear_updaters()
        self.play(*[FadeOut(m) for m in self.rcol], *[FadeOut(m) for m in self.probe], run_time=0.4)
        b, s = self.badge("O(n)", C_N, "Linear\nTime")
        self.at(0.7)
        self.play_sfx("sounds/pop.wav")
        self.play(Write(b), run_time=0.6)
        self.at(1.6)
        self.play(FadeIn(s, shift=UP * 0.2), run_time=0.6)
        self.play(Indicate(b, color=C_N, scale_factor=1.12), run_time=0.6)

    def cue_ol_halve(self, d):
        self.clear_stage(0.5)
        cells = make_array(list(range(1, 17)), 0.66, 0.7, 0.8, size=22, gap=0.0)
        rem = T("remaining data: 16", 36, C_HI, bold=True).move_to([0, -0.3, 0])
        self.hcells, self.hrem = cells, rem
        self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.04), FadeIn(rem), run_time=1.2)

        ptr = Arrow([0, 2.1, 0], [0, cells.get_top()[1] + 0.1, 0], buff=0, color=C_HI, stroke_width=6)
        pl = T("mid", 30, C_HI, bold=True).move_to([0, 2.5, 0])
        pg = VGroup(ptr, pl)

        def place(i): return cells[i].get_center()[0]

        def discard(a, b, n):
            new = T(f"remaining data: {n}", 36, C_HI, bold=True).move_to([0, -0.3, 0])
            self.play_sfx("sounds/whoosh.wav")
            self.retext(self.hrem, new, 0.7, also=[cells[j].animate.set_opacity(0.18) for j in range(a, b)])

        self.at(3.2)
        pg.move_to([place(7), pg.get_center()[1], 0])
        self.play_sfx("sounds/click.wav")
        self.play(FadeIn(pg, shift=DOWN * 0.2), run_time=0.5)
        self.at(4.2)
        discard(8, 16, 8)
        self.at(5.3)
        self.play_sfx("sounds/click.wav")
        self.play(pg.animate.move_to([place(3), pg.get_center()[1], 0]), run_time=0.5)
        self.at(6.0)
        discard(4, 8, 4)
        self.at(6.9)
        self.play_sfx("sounds/click.wav")
        self.play(pg.animate.move_to([place(1), pg.get_center()[1], 0]), run_time=0.4)
        self.at(7.3)
        discard(2, 4, 2)

    def cue_ol_steps(self, d):
        self.clear_stage(0.4)
        ys = [2.1, 1.25, 0.4, -0.45]
        vals = [1_000_000, 500_000, 250_000, 125_000]
        widths = [8.0, 4.0, 2.0, 1.0]
        x0 = -2.5
        rows = []
        for i, (y, v, w) in enumerate(zip(ys, vals, widths)):
            lab = T(f"{v:,}", 30, C_TXT).move_to([-2.85 - T(f"{v:,}", 30, C_TXT).width / 2, y, 0])
            bar = Rectangle(width=w, height=0.6, fill_color=C_LOG, fill_opacity=0.9, stroke_width=0).move_to([x0 + w / 2, y, 0])
            items = [lab, bar]
            if i > 0:
                ghost = DashedVMobject(Rectangle(width=w, height=0.6, stroke_color=C_DIM, stroke_width=2).move_to([x0 + w + w / 2, y, 0]), num_dashes=24)
                dv = T("÷ 2", 28, C_HI, bold=True).move_to([x0 + 2 * w + 0.55, y, 0])
                items += [ghost, dv]
            rows.append(items)
        self.rows = rows
        self.at(0.4)
        self.play_sfx("sounds/slide.wav")
        self.play(FadeIn(rows[0][0]), GrowFromEdge(rows[0][1], LEFT), run_time=0.7)
        for t_at, i in ((2.1, 1), (3.8, 2), (5.6, 3)):
            self.at(t_at)
            self.play_sfx("sounds/slide.wav")
            self.play(FadeIn(rows[i][0]), GrowFromEdge(rows[i][1], LEFT), run_time=0.5)
            self.play(FadeIn(rows[i][2]), FadeIn(rows[i][3]), run_time=0.4)
        self.at(6.5)
        dots = T("...", 36, C_DIM).move_to([x0 + 0.3, -1.2, 0])
        self.play(FadeIn(dots), run_time=0.4)
        self.dots_row = dots

    def cue_ol_shrink(self, d):
        ar = Arrow([4.6, 0.55, 0], [4.6, -0.45, 0], buff=0, color=C_HI, stroke_width=6)
        t = T("search space", 26, C_HI, bold=True).move_to([4.6, -0.85, 0])
        self.at(0.3)
        self.play(Create(ar), FadeIn(t), run_time=0.7)
        for i in range(4):
            self.play(Indicate(self.rows[i][1], color=C_HI, scale_factor=1.04), run_time=0.45)
        self.shrink_lab = (ar, t)

    def cue_ol_slow(self, d):
        self.clear_stage(0.4)
        ax, xl, yl = self.make_chart([-2.4, 0.3, 0], 6.0, 4.0)
        self.ch = (ax, xl, yl)
        self.add(ax, xl, yl)
        self.at(0.4)
        line = self.curve(ax, f_log, C_LOG)
        self.play_sfx("sounds/slide.wav")
        self.play(Create(line), run_time=1.2)
        self.at(1.8)
        t1 = T("n = 1,000,000", 36, C_TXT, bold=True).move_to([4.0, 1.0, 0])
        ar = Arrow([4.0, 0.4, 0], [4.0, -0.3, 0], buff=0, color=C_DIM, stroke_width=5)
        t2 = T("≈ 20 steps", 42, C_HI, bold=True).move_to([4.0, -0.95, 0])
        self.rcol = (t1, ar, t2)
        self.play(FadeIn(t1, shift=DOWN * 0.2), run_time=0.5)
        self.play_sfx("sounds/pop.wav")
        self.play(Create(ar), FadeIn(t2, shift=DOWN * 0.2), run_time=0.7)
        self.play(Indicate(t2, color=C_HI, scale_factor=1.12), run_time=0.7)

    def cue_ol_name(self, d):
        self.play(*[FadeOut(m) for m in self.rcol], run_time=0.4)
        b, s = self.badge("O(log n)", C_LOG, "Logarithmic\nTime")
        self.at(0.7)
        self.play_sfx("sounds/pop.wav")
        self.play(Write(b), run_time=0.7)
        self.at(1.7)
        self.play(FadeIn(s, shift=UP * 0.2), run_time=0.6)
        self.play(Indicate(b, color=C_LOG, scale_factor=1.1), run_time=0.6)

    def cue_sum_intro(self, d):
        self.clear_stage(0.5)
        head = T("Quick Recap", 44, C_HI, bold=True).move_to([0, 2.85, 0])
        specs = [("O(1)", C_O1), ("O(log n)", C_LOG), ("O(n)", C_N)]
        ys = [1.6, 0.35, -0.9]
        self.cards = []
        for (name, col), y in zip(specs, ys):
            panel = RoundedRectangle(width=12.0, height=1.0, corner_radius=0.2, stroke_color=col, stroke_width=4, fill_color=C_PANEL, fill_opacity=1).move_to([0, y, 0])
            bd = T(name, 38, col, bold=True).move_to([-6.0 + 0.4 + T(name, 38, col, bold=True).width / 2, y, 0])
            arw = T("→", 34, C_DIM).move_to([-2.45, y, 0])
            self.cards.append((panel, bd, arw, y))
        self.play(Write(head), run_time=0.7)
        self.play_sfx("sounds/slide.wav")
        self.play(LaggedStart(*[AnimationGroup(FadeIn(p), FadeIn(b), FadeIn(a)) for p, b, a, _ in self.cards], lag_ratio=0.25), run_time=1.3)

    def _recap_text(self, i, txt, col):
        panel, bd, arw, y = self.cards[i]
        t = T(txt, 28, C_TXT)
        if t.width > 8.0: t.scale_to_fit_width(8.0)
        t.move_to([-2.0 + t.width / 2, y, 0])
        self.play_sfx("sounds/pop.wav")
        self.play(Write(t), run_time=1.0)
        self.play(Indicate(bd, color=col, scale_factor=1.15), run_time=0.7)

    def cue_sum_o1(self, d):
        self.at(0.3)
        self._recap_text(0, "input বাড়লেও কাজ প্রায় একই।", C_O1)

    def cue_sum_log(self, d):
        self.at(0.3)
        self._recap_text(1, "input বাড়ে, কিন্তু কাজ ধীরে বাড়ে।", C_LOG)

    def cue_sum_n(self, d):
        self.at(0.3)
        self._recap_text(2, "input যত বাড়ে, কাজও প্রায় ততটাই বাড়ে।", C_N)

    def cue_why_matters(self, d):
        self.clear_stage(0.5)
        t = T("Asymptotic Notation", 60, C_TXT, bold=True).move_to([0, 0.8, 0])
        t.set_color_by_gradient(C_LOG, C_O1)
        s = T("why it matters", 36, C_DIM).move_to([0, -0.4, 0])
        self.play(Write(t), run_time=1.2)
        self.play(FadeIn(s, shift=UP * 0.2), run_time=0.6)

    def cue_why_100(self, d):
        self.clear_stage(0.5)
        xs = [-4.5, -1.5, 1.5, 4.5]
        line = overlay(Arrow([-5.9, 0.2, 0], [5.9, 0.2, 0], buff=0, color=C_DIM, stroke_width=4))
        nodes = [Dot([x, 0.2, 0], radius=0.13, color=C_LOG) for x in xs]
        labs = [T(s, 30, C_TXT, bold=True).move_to([x, 1.0, 0]) for s, x in zip(["100", "10,000", "1,000,000", "100,000,000"], xs)]
        self.ladder = dict(xs=xs, nodes=nodes, labs=labs)
        self.play_sfx("sounds/slide.wav")
        self.play(Create(line), run_time=0.5)
        self.at(1.0)
        self.play_sfx("sounds/pop.wav")
        self.play(FadeIn(nodes[0]), FadeIn(labs[0]), run_time=0.5)
        ok = VGroup(icon_check(C_O1), T("fast", 30, C_O1)).arrange(RIGHT, buff=0.2).move_to([xs[0], -0.7, 0])
        self.play_sfx("sounds/success.wav")
        self.play(FadeIn(ok, scale=0.6), run_time=0.5)
        self.at(3.0)
        no = T("not enough!", 40, C_BAD, bold=True).move_to([0, -1.8, 0])
        self.no_enough = no
        self.play_sfx("sounds/error.wav")
        self.play(FadeIn(no, scale=0.7), run_time=0.5)
        self.play(Indicate(no, color=C_BAD, scale_factor=1.12), run_time=0.7)

    def cue_why_big(self, d):
        self.play(FadeOut(self.no_enough), run_time=0.3)
        L = self.ladder
        self.qs = []
        for t_at, i in ((2.0, 1), (3.5, 2), (5.0, 3)):
            self.at(t_at)
            q = T("?", 60, C_BAD, bold=True).move_to([L["xs"][i], -0.7, 0])
            self.qs.append(q)
            self.play_sfx("sounds/pop.wav")
            self.play(FadeIn(L["nodes"][i]), FadeIn(L["labs"][i]), run_time=0.45)
            self.play_sfx("sounds/error.wav")
            self.play(FadeIn(q, scale=0.5), run_time=0.45)

    def cue_why_what(self, d):
        self.at(0.2)
        self.play(LaggedStart(*[Indicate(q, color=C_BAD, scale_factor=1.5) for q in self.qs], lag_ratio=0.3), run_time=1.6)

    def make_bubble(self, txt, x, y, w, h, col, size=30):
        r = RoundedRectangle(width=w, height=h, corner_radius=0.3, stroke_color=col, stroke_width=4, fill_color=C_PANEL, fill_opacity=1).move_to([x, y, 0])
        t = T(txt, size, C_TXT)
        if t.width > w - 0.6: t.scale_to_fit_width(w - 0.6)
        t.move_to(r)
        return VGroup(r, t)

    def cue_prog_now(self, d):
        self.clear_stage(0.5)
        win = RoundedRectangle(width=3.2, height=2.6, corner_radius=0.2, stroke_color=C_DIM, stroke_width=4, fill_color=C_PANEL, fill_opacity=1).move_to([-4.4, 0.4, 0])
        dots = VGroup(*[Dot(radius=0.06, color=c) for c in (C_BAD, C_HI, C_O1)]).arrange(RIGHT, buff=0.12).move_to(win.get_corner(UL) + RIGHT * 0.5 + DOWN * 0.28)
        lens, cols = [1.8, 1.2, 2.0, 0.9, 1.5], [C_LOG, C_O1, C_N, C_LOG, C_HI]
        lines = VGroup(*[Line(ORIGIN, RIGHT * l, color=c, stroke_width=6) for l, c in zip(lens, cols)]).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to(win.get_center() + DOWN * 0.25)
        self.win = VGroup(win, dots, lines)
        self.play_sfx("sounds/whoosh.wav")
        self.play(FadeIn(self.win, shift=RIGHT * 0.3), run_time=0.7)
        self.at(2.2)
        self.b1 = self.make_bubble("How fast is my code\nright now?", 1.8, 1.4, 6.2, 1.5, C_LOG, 32)
        self.arw1 = Arrow([-2.6, 1.4, 0], [-1.4, 1.4, 0], buff=0, color=C_DIM, stroke_width=4)
        self.play_sfx("sounds/pop.wav")
        self.play(Create(self.arw1), FadeIn(self.b1, scale=0.85), run_time=0.8)
        self.at(5.2)
        self.play(self.b1.animate.set_opacity(0.35), run_time=0.6)

    def cue_prog_big(self, d):
        self.at(1.8)
        self.b2 = self.make_bubble("How will it hold up when\nthe data is huge?", 1.8, -0.6, 6.2, 1.7, C_O1, 32)
        self.arw2 = Arrow([-2.6, -0.6, 0], [-1.4, -0.6, 0], buff=0, color=C_DIM, stroke_width=4)
        self.play_sfx("sounds/pop.wav")
        self.play(Create(self.arw2), FadeIn(self.b2, scale=0.85), run_time=0.8)
        self.at(4.2)
        nb = T("n = 100,000,000+", 30, C_HI, bold=True).move_to([1.8, -1.95, 0])
        self.play(FadeIn(nb, shift=UP * 0.2), run_time=0.6)
        self.play(Indicate(nb, color=C_HI, scale_factor=1.12), run_time=0.7)

    def cue_language(self, d):
        self.clear_stage(0.5)
        g = T("Growth", 56, C_LOG, bold=True).move_to([0, 1.8, 0])
        ar = Arrow([0, 1.15, 0], [0, 0.25, 0], buff=0, color=C_HI, stroke_width=6)
        n = T("Asymptotic Notation", 56, C_TXT, bold=True).move_to([0, -0.35, 0])
        n.set_color_by_gradient(C_LOG, C_O1)
        sub = T("the language of growth", 30, C_DIM).move_to([0, -1.4, 0])
        self.at(0.5)
        self.play_sfx("sounds/pop.wav")
        self.play(FadeIn(g, shift=DOWN * 0.2), run_time=0.6)
        self.at(2.4)
        self.play(Create(ar), run_time=0.5)
        self.at(3.3)
        self.play_sfx("sounds/success.wav")
        self.play(Write(n), run_time=1.2)
        self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.5)

    def cue_symbols(self, d):
        self.clear_stage(0.5)
        toks = [T("O(1)", 58, C_O1, bold=True).move_to([-4.4, 0.9, 0]),
                T("O(log n)", 58, C_LOG, bold=True).move_to([0, 0.9, 0]),
                T("O(n)", 58, C_N, bold=True).move_to([4.4, 0.9, 0])]
        for t_at, tk in zip((0.5, 1.2, 1.9), toks):
            self.at(t_at)
            self.play_sfx("sounds/pop.wav")
            self.play(FadeIn(tk, scale=0.7), run_time=0.5)
        self.at(2.7)
        js = T("just symbols", 42, C_DIM).move_to([0, -0.6, 0])
        self.play(FadeIn(js, shift=UP * 0.15), run_time=0.5)
        self.at(3.5)
        strike = overlay(Line(js.get_left() + LEFT * 0.15, js.get_right() + RIGHT * 0.15, color=C_BAD, stroke_width=6))
        self.play_sfx("sounds/slash.wav")
        self.play(Create(strike), run_time=0.4)
        self.play(Indicate(js, color=C_BAD, scale_factor=1.05), run_time=0.5)

    def cue_final(self, d):
        self.clear_stage(0.5)
        ax, xl, yl = self.make_chart([-0.8, 0.3, 0], 8.4, 4.0, "n (input size)", "work / time")
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.9)
        specs = [(1.9, f_one, C_O1, "O(1)"), (3.1, f_log, C_LOG, "O(log n)"), (4.3, f_lin, C_N, "O(n)")]
        labels = []
        for t_at, fn, col, name in specs:
            self.at(t_at)
            crv = self.curve(ax, fn, col)
            lab = T(name, 32, col, bold=True).move_to(ax.c2p(10, fn(10)) + RIGHT * (0.55 + T(name, 32, col, bold=True).width / 2))
            self.play_sfx("sounds/slide.wav")
            self.play(Create(crv), run_time=0.8)
            self.play(FadeIn(lab, shift=LEFT * 0.2), run_time=0.3)
            labels.append(lab)
        self.at(5.6)
        self.play(LaggedStart(*[Indicate(l, scale_factor=1.25) for l in labels], lag_ratio=0.3), run_time=1.3)