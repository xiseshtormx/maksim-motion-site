"""Generate the original KAIROS motion assets used by the site.

Requires Pillow and imageio-ffmpeg. The generated videos are silent and contain
only procedural graphics, so the site does not depend on third-party footage.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "media"
OUT.mkdir(parents=True, exist_ok=True)

INK = (11, 13, 15)
INK_SOFT = (20, 24, 28)
PAPER = (243, 239, 229)
BLUE = (11, 62, 114)
BLUE_BRIGHT = (14, 103, 184)
WHITE = (248, 246, 239)

FONT = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_CONDENSED = r"C:\Windows\Fonts\bahnschrift.ttf"


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease_out(value: float) -> float:
    value = clamp(value)
    return 1 - (1 - value) ** 3


def ease_in_out(value: float) -> float:
    value = clamp(value)
    return value * value * (3 - 2 * value)


def mix(a: float, b: float, progress: float) -> float:
    return a + (b - a) * progress


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def text_spaced(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    face: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int] | tuple[int, int, int, int],
    spacing: float,
    anchor: str = "la",
) -> None:
    widths = [draw.textlength(char, font=face) for char in text]
    total = sum(widths) + spacing * max(0, len(text) - 1)
    x, y = position
    if anchor.startswith("m"):
        x -= total / 2
    elif anchor.startswith("r"):
        x -= total
    for char, width in zip(text, widths):
        draw.text((x, y), char, font=face, fill=fill, anchor="la")
        x += width + spacing


def draw_mark(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    scale: float,
    color: tuple[int, int, int] | tuple[int, int, int, int],
    opposite: tuple[int, int, int] | tuple[int, int, int, int],
    tick_progress: float = 1.0,
) -> None:
    s = scale
    draw.rectangle((x + 25.5*s, y + 5.5*s, x + 41*s, y + 58.5*s), fill=color)
    draw.polygon(
        [(x+36*s,y+33*s),(x+49*s,y+33*s),(x+79*s,y+5.5*s),(x+64*s,y+5.5*s)],
        fill=color,
    )
    draw.polygon(
        [(x+36*s,y+31*s),(x+49*s,y+31*s),(x+80*s,y+58.5*s),(x+65*s,y+58.5*s)],
        fill=color,
    )
    tick_heights = [2.8,3.2,3.8,4.3,5.0,5.6,6.1,6.8,6.1,5.3,4.6,3.9,3.3,2.8,2.3]
    for index, height in enumerate(tick_heights):
        local = clamp(tick_progress * 1.45 - index * 0.035)
        if local <= 0:
            continue
        tx = x + index * 6.15*s
        width = (4.4 if index < 4 else 2.2 if index < 9 else 1.4) * s
        visible_height = height * s * local
        center = y + 32*s
        draw.rectangle((tx, center-visible_height/2, tx+width, center+visible_height/2), fill=color)
    draw.polygon(
        [(x+31*s,y+27.5*s),(x+45*s,y+32*s),(x+31*s,y+36.5*s)],
        fill=opposite,
    )


def draw_full_logo(
    image: Image.Image,
    center: tuple[float, float],
    scale: float,
    color: tuple[int, int, int],
    opposite: tuple[int, int, int],
    progress: float = 1.0,
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = center
    mark_w = 92 * scale
    total_w = 710 * scale
    start_x = cx - total_w / 2
    mark_x = start_x + mix(-95*scale, 0, ease_out(progress))
    word_x = start_x + 160*scale + mix(130*scale, 0, ease_out(progress))
    rgba = (*color, int(255 * clamp(progress * 1.8)))
    draw_mark(draw, mark_x, cy - 32*scale, scale, rgba, (*opposite, rgba[3]), progress)
    divider_x = start_x + 126*scale
    draw.line((divider_x, cy-38*scale, divider_x, cy+38*scale), fill=(*color, int(110*progress)), width=max(1, int(scale)))
    face = font(FONT, max(16, int(48*scale)))
    sub = font(FONT_BOLD, max(8, int(10*scale)))
    text_spaced(draw, (word_x, cy-32*scale), "KAIROS", face, rgba, 12*scale)
    text_spaced(draw, (word_x, cy+30*scale), "MOTION DESIGN / VIDEO EDITING", sub, (*color, int(205*progress)), 5.1*scale)
    reveal = Image.new("L", image.size, 0)
    reveal_draw = ImageDraw.Draw(reveal)
    reveal_half = total_w * ease_out(progress) / 2
    reveal_draw.rectangle((cx-reveal_half, 0, cx+reveal_half, image.height), fill=255)
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", image.size, 0), reveal))
    image.alpha_composite(layer)


def add_grid(draw: ImageDraw.ImageDraw, size: tuple[int, int], color: tuple[int, int, int, int], step: int) -> None:
    width, height = size
    for x in range(0, width + 1, step):
        draw.line((x, 0, x, height), fill=color, width=1)
    for y in range(0, height + 1, step):
        draw.line((0, y, width, y), fill=color, width=1)


def identity_frame(frame_index: int, fps: int, size: tuple[int, int]) -> Image.Image:
    width, height = size
    seconds = frame_index / fps
    progress = ease_out(seconds / 1.45)
    image = Image.new("RGBA", size, (*PAPER, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    add_grid(draw, size, (*INK, int(18 * progress)), 120)
    cx, cy = width/2, height/2
    for index, radius in enumerate((115, 220, 330)):
        radius_now = mix(radius * .72, radius, progress)
        alpha = int((35 - index * 6) * progress)
        draw.ellipse((cx-radius_now, cy-radius_now, cx+radius_now, cy+radius_now), outline=(*INK, alpha), width=2)
    axis_alpha = int(34 * progress)
    draw.line((0, cy, width, cy), fill=(*INK, axis_alpha), width=1)
    draw.line((cx, 0, cx, height), fill=(*INK, axis_alpha), width=1)
    pulse = 1 + math.sin(seconds * math.pi * 1.25) * .012 * progress
    draw_full_logo(image, (cx, cy), .98 * pulse, BLUE, PAPER, progress)
    time_face = font(FONT_BOLD, 12)
    text_spaced(draw, (34, 34), "KAIROS / PRIMARY MOTION", time_face, (*INK, int(105*progress)), 2.6)
    text_spaced(draw, (width-34, height-45), f"00:00:{int(seconds):02d}:{frame_index%fps:02d}", time_face, (*INK, int(105*progress)), 2.0, "ra")
    return Image.alpha_composite(Image.new("RGBA", size, (*PAPER, 255)), image).convert("RGB")


def hero_frame(frame_index: int, fps: int, size: tuple[int, int]) -> Image.Image:
    width, height = size
    seconds = frame_index / fps
    segment_duration = 2.5
    segment = min(3, int(seconds // segment_duration))
    local = (seconds % segment_duration) / segment_duration
    fade = clamp(min(local / .12, (1-local) / .12))
    image = Image.new("RGBA", size, (*INK, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    add_grid(draw, size, (255, 255, 255, 13), 80)
    draw.rectangle((0, 0, width, 9), fill=(*BLUE_BRIGHT, 170))
    small = font(FONT_BOLD, 13)
    label = font(FONT_BOLD, 18)
    big = font(FONT_CONDENSED, 162)
    huge = font(FONT_CONDENSED, 260)

    if segment == 0:
        p = ease_out(local)
        frame_x = mix(-width*.5, width*.07, p)
        draw.rounded_rectangle((frame_x, height*.13, frame_x+width*.58, height*.83), radius=28, fill=(*BLUE, int(210*fade)))
        draw.rounded_rectangle((frame_x+width*.035, height*.18, frame_x+width*.545, height*.78), radius=20, fill=(*INK_SOFT, int(245*fade)))
        for index in range(7):
            y = height*.24 + index*height*.072
            line_w = width*(.16 + .24*abs(math.sin(index*.82 + seconds*2.8)))
            draw.rounded_rectangle((frame_x+width*.085, y, frame_x+width*.085+line_w, y+8), radius=4, fill=(*PAPER, int((65+index*14)*fade)))
        title_x = mix(width*1.06, width*.47, p)
        draw.text((title_x, height*.18), "EDIT", font=huge, fill=(*PAPER, int(240*fade)))
        draw.line((title_x+8, height*.64, width*.92, height*.64), fill=(*BLUE_BRIGHT, int(230*fade)), width=8)
        text_spaced(draw, (title_x+8, height*.7), "RHYTHM / FRAME / IMPACT", label, (*PAPER, int(165*fade)), 5.5)
    elif segment == 1:
        p = ease_in_out(local)
        drift = math.sin(local * math.pi) * width*.08
        for index in range(6):
            band_y = height*(.14 + index*.125)
            direction = -1 if index % 2 else 1
            band_x = width*.08 + direction*drift + index*width*.018
            band_w = width*(.34 + .08*math.sin(index*.9 + seconds))
            tone = BLUE if index in (1,4) else PAPER
            alpha = int((52 + index*18) * fade)
            draw.rounded_rectangle((band_x,band_y,band_x+band_w,band_y+13+index*2),radius=9,fill=(*tone,alpha))
        word_x = mix(width*.9, width*.42, ease_out(local))
        draw.text((word_x, height*.18), "FLOW", font=huge, fill=(*PAPER, int(225*fade)), anchor="ma", stroke_width=2, stroke_fill=(*INK, int(80*fade)))
        radius = mix(width*.09,width*.24,ease_out(local))
        draw.ellipse((width*.73-radius,height*.53-radius,width*.73+radius,height*.53+radius),outline=(*BLUE_BRIGHT,int(100*fade)),width=3)
        draw.ellipse((width*.73-radius*.58,height*.53-radius*.58,width*.73+radius*.58,height*.53+radius*.58),outline=(*PAPER,int(54*fade)),width=2)
        text_spaced(draw, (width*.91, height*.8), "PACE / DIRECTION / CONTINUITY", label, (*PAPER, int(150*fade)), 5.2, "ra")
    elif segment == 2:
        p = ease_out(local)
        bars = 38
        for index in range(bars):
            x = width*.09 + index * width*.82/(bars-1)
            envelope = math.sin((index/(bars-1))*math.pi)
            wave = .35 + .65 * abs(math.sin(index*.72 + seconds*5.4))
            bar_h = (28 + 185*envelope*wave) * p
            draw.rounded_rectangle((x-3, height/2-bar_h/2, x+3, height/2+bar_h/2), radius=3, fill=(*PAPER, int((90+150*envelope)*fade)))
        draw.text((width*.08, height*.12), "SOUND", font=big, fill=(*PAPER, int(225*fade)))
        text_spaced(draw, (width*.91, height*.82), "RHYTHM / 24 FPS", label, (*BLUE_BRIGHT, int(230*fade)), 5, "ra")
    else:
        p = ease_out(local/.68)
        sweep = mix(-width*.45, width*1.05, ease_in_out(local))
        draw.polygon([(sweep-width*.18,0),(sweep+width*.04,0),(sweep-width*.18,height),(sweep-width*.4,height)], fill=(*BLUE, int(185*fade)))
        word_x = mix(width*1.08, width*.08, p)
        draw.text((word_x, height*.18), "MOTION", font=huge, fill=(*PAPER, int(245*fade)))
        draw.text((word_x+width*.006, height*.49), "DESIGN", font=big, fill=(*BLUE_BRIGHT, int(230*fade)))
        for index in range(5):
            y = height*(.68 + index*.027)
            length = width*(.18 + index*.11)
            draw.line((word_x+8, y, min(width*.93,word_x+8+length), y), fill=(*PAPER, int((95-index*12)*fade)), width=2)
        text_spaced(draw, (width*.92, height*.8), "EDIT / TYPE / SOUND / 24 FPS", label, (*PAPER, int(155*fade)), 5.5, "ra")

    text_spaced(draw, (32, 29), f"MAXIM / REEL–{segment+1:02d}", small, (*PAPER, int(125*fade)), 2.5)
    text_spaced(draw, (width-32, 29), f"00:00:{int(seconds):02d}:{frame_index%fps:02d}", small, (*PAPER, int(125*fade)), 2.0, "ra")
    return Image.alpha_composite(Image.new("RGBA", size, (*INK, 255)), image).convert("RGB")


def encode_pair(name: str, frame_factory, duration: float, size: tuple[int, int], fps: int = 24) -> None:
    frame_count = int(duration * fps)
    webm = imageio_ffmpeg.write_frames(
        str(OUT / f"{name}.webm"), size, fps=fps, codec="libvpx-vp9", pix_fmt_in="rgb24",
        output_params=["-crf", "35", "-b:v", "0", "-row-mt", "1", "-an"],
    )
    mp4 = imageio_ffmpeg.write_frames(
        str(OUT / f"{name}.mp4"), size, fps=fps, codec="libx264", pix_fmt_in="rgb24",
        output_params=["-crf", "25", "-preset", "medium", "-movflags", "+faststart", "-pix_fmt", "yuv420p", "-an"],
    )
    webm.send(None)
    mp4.send(None)
    poster = None
    poster_index = int((frame_count - 1) * .92)
    for index in range(frame_count):
        frame = frame_factory(index, fps, size)
        payload = frame.tobytes()
        webm.send(payload)
        mp4.send(payload)
        if index == poster_index:
            poster = frame.copy()
    webm.close()
    mp4.close()
    assert poster is not None
    poster.save(OUT / f"{name}-poster.webp", "WEBP", quality=90, method=6)


if __name__ == "__main__":
    encode_pair("kairos-hero-reel", hero_frame, duration=10.0, size=(1280, 720))
    encode_pair("kairos-logo-motion", identity_frame, duration=4.8, size=(1280, 720))
    for path in sorted(OUT.glob("kairos-*")):
        print(f"{path.name}: {path.stat().st_size / 1024:.1f} KB")
