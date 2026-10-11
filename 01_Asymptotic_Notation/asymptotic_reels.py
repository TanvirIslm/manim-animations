"""
tanFlux - Asymptotic Notation Growth Reel (9:16, English text + growth sound)

RENDER   manim -pqh asymptotic_growth_reel_v2_english.py AsymptoticGrowthReel
PREVIEW  REEL_PREVIEW=1 manim -pql asymptotic_growth_reel_v2_english.py AsymptoticGrowthReel

The graph, curve order, scaling, layout, and animation timings are preserved.
All on-screen Bengali text has been changed to English. Rising sound effects are
synthesized automatically and synchronized with each curve's growth animation.
Optional extra sounds: ./sounds/{bass,whoosh,tick,impact,chime}.wav
"""
from manim import *
import numpy as np
import os
import wave

PREVIEW = bool(os.environ.get("REEL_PREVIEW"))
config.pixel_width = 540 if PREVIEW else 1080
config.pixel_height = 960 if PREVIEW else 1920
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30 if PREVIEW else 60
config.background_color = "#05070B"

# ------------------------------------------------------------ palette
PANEL = "#0A111B"
PANEL_EDGE = "#2A3A52"
GRIDC = "#1B2738"
WHITE = "#F3F6FC"
MUTED = "#8C99AD"
CYAN = "#38D9E8"
GREEN = "#64D99C"
GOLD = "#F5C451"
ORANGE = "#F49A56"
RED = "#FF647A"
VIOLET = "#B49AFF"
UI_FONT = "DejaVu Sans"
BN_FONT = "Noto Sans Bengali"  # retained for compatibility; no Bengali text is used

# ------------------------------------------------------------ plot geometry
X0, X1 = -3.50, 3.20
Y0, Y1 = -3.75, 3.75
N_MIN, N_MAX = 1.0, 6.0
PANEL_W, PANEL_H = 8.5, 9.5
TITLE_Y = 6.05
LEGEND_TOP, LEGEND_STEP = 3.20, 0.72

# name, colour, function, y-scale while drawing, grow seconds, meaning, example
FUNCS = [
    dict(name="O(1)", col=CYAN, fn=lambda n: 1.0, ymax=7, grow=2.2,
         bn="Work stays constant as input grows", ex="Array index access"),
    dict(name="O(log n)", col=GREEN, fn=lambda n: np.log2(n), ymax=7, grow=2.8,
         bn="Work grows slowly as input grows", ex="Binary Search"),
    dict(name="O(n)", col=GOLD, fn=lambda n: n, ymax=7, grow=3.0,
         bn="Work grows with input size", ex="Linear Search"),
    dict(name="O(n log n)", col=ORANGE, fn=lambda n: n * np.log2(n), ymax=16, grow=3.2,
         bn="Grows faster than linear", ex="Merge Sort"),
    dict(name="O(n²)", col=RED, fn=lambda n: n ** 2, ymax=38, grow=3.4,
         bn="Double input, four times the work", ex="Nested loops"),
    dict(name="O(2ⁿ)", col=VIOLET, fn=lambda n: 2.0 ** n, ymax=66, grow=3.8,
         bn="One more input can double the work", ex="Brute-force subsets"),
]


def indian(n: int) -> str:
    """1000000 -> '10,00,000' (original Bangladesh/Indian grouping)."""
    s = str(int(n))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts + [tail])


def make_growth_audio(path, duration, index, sample_rate=44100):
    """Create a rising synth + airy noise swell; later curves sound more intense."""
    count = max(1, int(sample_rate * duration))
    t = np.arange(count, dtype=np.float64) / sample_rate
    progress = np.linspace(0.0, 1.0, count, endpoint=False)

    # Gentle attack/release envelope; exponential curve gets a stronger crescendo.
    attack = np.clip(progress / 0.10, 0.0, 1.0)
    release = np.clip((1.0 - progress) / 0.09, 0.0, 1.0)
    envelope = (attack * release) ** 0.7
    intensity = 0.22 + 0.115 * index

    # Rising layered oscillator with a smooth upward pitch sweep.
    f0 = 95 + 18 * index
    f1 = 360 + 115 * index
    phase = 2 * np.pi * (f0 * t + (f1 - f0) * t * t / (2 * duration))
    tone = np.sin(phase) + 0.34 * np.sin(phase * 2.01 + 0.3)
    sub = np.sin(2 * np.pi * (48 + 14 * index) * t) * (0.28 + 0.30 * progress)

    # Soft noise becomes brighter/louder over time, like a controlled whoosh.
    rng = np.random.default_rng(2000 + index)
    noise = rng.normal(0.0, 1.0, count)
    # Lightweight moving-average smoothing gives the noise an airy, less harsh quality.
    kernel_size = 90
    kernel = np.ones(kernel_size, dtype=np.float64) / kernel_size
    airy = np.convolve(noise, kernel, mode="same") * 7.0
    whoosh = airy * (progress ** 1.7) * (0.5 + 0.15 * index)

    signal = envelope * intensity * (0.46 * tone + 0.22 * sub + 0.60 * whoosh)
    # Small final swell; strongest on O(2^n), but not clipped.
    signal += envelope * (0.025 + index * 0.009) * np.sin(2 * np.pi * (f1 * 1.3) * t) * progress
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / max(1.0, peak / 0.78)
    pcm = (np.clip(signal, -1.0, 1.0) * 32767).astype(np.int16)

    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())


class AsymptoticGrowthReel(Scene):
    # =========================================================== main flow
    def construct(self):
        self.ymax = ValueTracker(7)
        self.panel_vis = ValueTracker(0)
        self.make_background()
        self.make_brand()
        self.play_sound("bass", -10)
        self.show_hook()
        self.build_panel()
        self.panel_in()
        self.curves, self.opac, self.wid, self.labels = [], [], [], []
        for i, d in enumerate(FUNCS):
            self.grow_function(i, d)
        self.finale()

    def play_sound(self, name, gain=-12):
        path = os.path.join("sounds", f"{name}.wav")
        if os.path.isfile(path):
            self.add_sound(path, gain=gain)

    def play_growth_sound(self, index, duration):
        """Generate a curve-specific rising sound and start it at the growth cue."""
        folder = "generated_growth_audio"
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"growth_{index}_{duration:.2f}.wav")
        if not os.path.isfile(path):
            make_growth_audio(path, duration, index)
        self.add_sound(path, gain=-3 if index < 4 else 0)

    # =========================================================== coordinates
    def c2p(self, n, v):
        return np.array([X0 + (n - N_MIN) / (N_MAX - N_MIN) * (X1 - X0),
                         Y0 + v / self.ymax.get_value() * (Y1 - Y0), 0.0])

    # =========================================================== background
    def make_background(self):
        n = 40
        top, bot = ManimColor("#0C1626"), ManimColor("#04060A")
        strips = VGroup()
        for k in range(n):
            col = interpolate_color(top, bot, k / (n - 1))
            r = Rectangle(width=9.2, height=16 / n + 0.03, fill_color=col,
                          fill_opacity=1, stroke_width=0)
            r.move_to([0, 8 - (k + 0.5) * 16 / n, 0])
            strips.add(r)

        def glow(center, color, rmax, steps, op):
            g = VGroup()
            for k in range(steps):
                g.add(Circle(radius=rmax * (1 - k / steps), stroke_width=0,
                             fill_color=color, fill_opacity=op).move_to(center))
            return g

        glows = VGroup(glow([-2.2, 6.4, 0], CYAN, 5.2, 16, 0.010),
                       glow([3.0, -5.6, 0], GOLD, 5.0, 16, 0.009),
                       glow([0, 0.2, 0], "#2B4C9B", 6.0, 14, 0.006))

        dots = VGroup()
        for x in np.arange(-4.2, 4.21, 0.6):
            for y in np.arange(-7.8, 7.81, 0.6):
                d = np.hypot(x / 4.5, y / 8.0)
                op = max(0.0, 0.30 * (1 - d * 0.85))
                if op > 0.02:
                    dots.add(Dot([x, y, 0], radius=0.017, color="#6C86AD", fill_opacity=op))

        rules = VGroup(Line([-4.05, 7.62, 0], [-3.35, 7.62, 0], color=GOLD, stroke_width=3),
                       Line([3.35, -7.62, 0], [4.05, -7.62, 0], color=CYAN, stroke_width=3))
        bg = VGroup(strips, glows, dots, rules)
        cam = Camera(pixel_width=config.pixel_width, pixel_height=config.pixel_height,
                     frame_width=9, frame_height=16, background_color="#05070B")
        cam.capture_mobjects([bg])
        img = ImageMobject(np.array(cam.pixel_array)).set_height(16).move_to(ORIGIN)
        self.add(img)

    def make_brand(self):
        brand = VGroup(Text("tan", font=UI_FONT, font_size=20, weight=BOLD, color=WHITE),
                       Text("Flux", font=UI_FONT, font_size=20, weight=BOLD, color=GOLD)
                       ).arrange(RIGHT, buff=0.02).move_to([-3.45, 7.3, 0])
        self.add(brand)

    # =========================================================== text helpers
    def fade_swap(self, old, new, t_out=0.25, t_in=0.4):
        self.play(FadeOut(old), run_time=t_out)
        self.play(FadeIn(new, shift=UP * 0.12), run_time=t_in)

    def title_block(self, d):
        name = Text(d["name"], font=UI_FONT, font_size=62, weight=BOLD, color=d["col"])
        bn = Text(d["bn"], font=UI_FONT, font_size=34, weight=BOLD, color=WHITE)
        ex = Text("e.g.  " + d["ex"], font=UI_FONT, font_size=22, color=MUTED)
        for t in (bn, ex):
            if t.width > 8.0:
                t.scale_to_fit_width(8.0)
        return VGroup(name, bn, ex).arrange(DOWN, buff=0.13).move_to([0, TITLE_Y, 0])

    # =========================================================== HOOK
    def show_hook(self):
        q1 = Text("1 MILLION DATA POINTS?", font=UI_FONT, font_size=42, weight=BOLD, color=WHITE)
        q2 = Text("WHICH GROWS FASTER?", font=UI_FONT, font_size=34, weight=BOLD, color=GOLD)
        self.hook_q = VGroup(q1, q2).arrange(DOWN, buff=0.16).move_to([0, TITLE_Y, 0])

        card = RoundedRectangle(width=7.6, height=3.4, corner_radius=0.3, stroke_color=PANEL_EDGE,
                                stroke_width=2, fill_color=PANEL, fill_opacity=0.92).move_to([0, 0.6, 0])
        cap = Text("DATA SIZE (n)", font=UI_FONT, font_size=22, weight=BOLD, color=MUTED
                   ).move_to([0, 1.75, 0])
        u = ValueTracker(0.0)

        def big_number():
            v = 10 ** (2 + 4 * u.get_value())
            col = interpolate_color(ManimColor(CYAN), ManimColor(GOLD), u.get_value())
            return Text(indian(round(v)), font=UI_FONT, font_size=96, weight=BOLD, color=col
                        ).move_to([0, 0.35, 0])
        num = always_redraw(big_number)
        self.hook_card = VGroup(card, cap)
        self.hook_num = num
        self.add(self.hook_q, self.hook_card, num)
        self.play(u.animate.set_value(1.0), run_time=1.6, rate_func=rate_functions.ease_in_out_cubic)
        self.play(Indicate(num, color=GOLD, scale_factor=1.07), run_time=0.5)
        self.wait(0.7)
        num.clear_updaters()

    # =========================================================== panel
    def build_panel(self):
        panel = RoundedRectangle(width=PANEL_W, height=PANEL_H, corner_radius=0.28,
                                 stroke_color=PANEL_EDGE, stroke_width=2,
                                 fill_color=PANEL, fill_opacity=0.88)

        def corner(sx, sy, col):
            px, py = sx * PANEL_W / 2, sy * PANEL_H / 2
            v = VMobject(stroke_color=col, stroke_width=4)
            v.set_points_as_corners([[px - sx * 0.7, py, 0], [px, py, 0], [px, py - sy * 0.7, 0]])
            return v
        accents = VGroup(corner(-1, 1, GOLD), corner(1, -1, CYAN))

        grid = VGroup()
        for f in (0.25, 0.5, 0.75, 1.0):
            y = Y0 + f * (Y1 - Y0)
            grid.add(Line([X0, y, 0], [X1, y, 0], stroke_color=GRIDC, stroke_width=1.4))
        ticks = VGroup()
        for k in range(1, 7):
            x = self.c2p(k, 0)[0]
            grid.add(Line([x, Y0, 0], [x, Y1, 0], stroke_color=GRIDC, stroke_width=1.0, stroke_opacity=0.7))
            ticks.add(Text(str(k), font=UI_FONT, font_size=20, weight=BOLD, color=MUTED).move_to([x, Y0 - 0.3, 0]))

        axes = VGroup(Arrow([X0, Y0, 0], [X1 + 0.28, Y0, 0], buff=0, color="#5C6C84", stroke_width=3,
                            tip_length=0.2, max_tip_length_to_length_ratio=1),
                      Arrow([X0, Y0, 0], [X0, Y1 + 0.28, 0], buff=0, color="#5C6C84", stroke_width=3,
                            tip_length=0.2, max_tip_length_to_length_ratio=1))
        xt = Text("INPUT SIZE (n) · ILLUSTRATIVE GROWTH", font=UI_FONT, font_size=16, weight=BOLD, color=MUTED
                  ).move_to([(X0 + X1) / 2, Y0 - 0.72, 0])

        def readout():
            t = Text(f"SCALE  0 – {int(round(self.ymax.get_value()))} steps", font=UI_FONT, font_size=20,
                     weight=BOLD, color=GOLD)
            t.move_to([X0 + t.width / 2, Y1 + 0.45, 0]).set_opacity(self.panel_vis.get_value())
            return t
        self.readout = always_redraw(readout).set_z_index(5)
        foot = Text("ASYMPTOTIC NOTATION · BIG-O", font=UI_FONT, font_size=19, weight=BOLD, color=MUTED
                    ).move_to([0, -5.45, 0])
        self.panel_static = VGroup(panel, accents, grid, axes, ticks, xt, foot)

    def panel_in(self):
        self.play(FadeOut(self.hook_card), FadeOut(self.hook_num), FadeOut(self.hook_q), run_time=0.45)
        first = self.title_block(FUNCS[0])
        self.title = first
        self.add(self.readout)
        self.play(FadeIn(self.panel_static), self.panel_vis.animate.set_value(1.0), run_time=0.9)
        self.play(FadeIn(first, shift=UP * 0.12), run_time=0.4)

    # =========================================================== one function
    def grow_function(self, i, d):
        col, fn = d["col"], d["fn"]
        if i > 0:
            new = self.title_block(d)
            self.fade_swap(self.title, new)
            self.title = new

        if abs(self.ymax.get_value() - d["ymax"]) > 0.01:
            self.play_sound("whoosh", -13)
            self.play(self.ymax.animate.set_value(d["ymax"]), run_time=1.0,
                      rate_func=rate_functions.ease_in_out_sine)

        prog = ValueTracker(N_MIN)
        op = ValueTracker(1.0)
        wd = ValueTracker(5.5)
        self.opac.append(op)
        self.wid.append(wd)

        def build_curve():
            ne = max(prog.get_value(), N_MIN + 0.004)
            ns = np.linspace(N_MIN, ne, max(3, int(170 * (ne - N_MIN) / (N_MAX - N_MIN)) + 3))
            pts = [self.c2p(n, fn(n)) for n in ns]
            main = VMobject(stroke_color=col, stroke_width=wd.get_value(), stroke_opacity=op.get_value(),
                            cap_style=CapStyleType.ROUND)
            main.set_points_as_corners(pts)
            halo = VMobject(stroke_color=col, stroke_width=wd.get_value() * 2.8,
                            stroke_opacity=0.15 * op.get_value(), cap_style=CapStyleType.ROUND)
            halo.set_points_as_corners(pts)
            end = Dot(pts[-1], radius=0.09, color=col).set_opacity(op.get_value())
            return VGroup(halo, main, end)
        curve = always_redraw(build_curve)

        def build_tipfx():
            ne = max(prog.get_value(), N_MIN + 0.004)
            tip = self.c2p(ne, fn(ne))
            base = self.c2p(ne, 0)
            halo = Circle(radius=0.26, stroke_width=0, fill_color=col, fill_opacity=0.22).move_to(tip)
            drop = DashedLine(base, tip, dash_length=0.12, color=col, stroke_width=2.2, stroke_opacity=0.65)
            mark = Dot(base, radius=0.075, color=col)
            return VGroup(drop, halo, mark)
        tipfx = always_redraw(build_tipfx)

        txt = Text(d["name"], font=UI_FONT, font_size=26, weight=BOLD, color=col)
        pill = RoundedRectangle(width=txt.width + 0.42, height=txt.height + 0.30, corner_radius=0.15,
                                stroke_color=col, stroke_width=2.5, fill_color="#080D15", fill_opacity=0.94)
        txt.move_to(pill)
        label = VGroup(pill, txt).set_z_index(10)
        self.labels.append(label)

        def follow(m):
            ne = max(prog.get_value(), N_MIN + 0.004)
            tip = self.c2p(ne, fn(ne))
            cx = max(tip[0] - m.width / 2 - 0.10, X0 + m.width / 2 + 0.06)
            cy = min(tip[1] + 0.55, Y1 + 0.55)
            m.move_to([cx, cy, 0])
        follow(label)
        label.add_updater(follow)

        self.curves.append(curve)
        self.add(curve, tipfx, label)
        self.play_sound("impact" if i == len(FUNCS) - 1 else "tick", -12 if i == len(FUNCS) - 1 else -16)
        # New synchronized rising sound: pitch and intensity increase with curve order.
        self.play_growth_sound(i, d["grow"])
        self.play(prog.animate.set_value(N_MAX), run_time=d["grow"],
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.35)

        tipfx.clear_updaters()
        label.clear_updaters()
        slot_y = LEGEND_TOP - LEGEND_STEP * i
        self.play(FadeOut(tipfx),
                  label.animate.move_to([X0 + 0.06 + label.width / 2, slot_y, 0]),
                  run_time=0.6, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.45 if i < len(FUNCS) - 1 else 0.2)

    # =========================================================== finale
    def finale(self):
        self.play_sound("bass", -12)
        anims = [self.opac[k].animate.set_value(0.28) for k in range(len(FUNCS) - 1)]
        anims += [self.wid[-1].animate.set_value(8.5), Indicate(self.labels[-1], color=VIOLET, scale_factor=1.15)]
        self.play(*anims, run_time=0.8)
        final = Text("FASTEST GROWTH", font=UI_FONT, font_size=38, weight=BOLD, color=WHITE)
        name = Text("O(2ⁿ)", font=UI_FONT, font_size=62, weight=BOLD, color=VIOLET)
        fin = VGroup(name, final).arrange(DOWN, buff=0.2).move_to([0, TITLE_Y, 0])
        self.fade_swap(self.title, fin)
        self.play_sound("chime", -13)
        self.wait(1.8)
