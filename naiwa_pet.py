from __future__ import annotations

import math
import sys
import time
from pathlib import Path
import tkinter as tk

from PIL import Image, ImageTk


APP_DIR = Path(__file__).resolve().parent
ASSET_PATH = APP_DIR / "assets" / "naiwa.png"
TRANSPARENT_KEY = "#ff00ff"
BASE_HEIGHT = 430
ANIMATION_MS = 520


class NaiwaPet:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("奶娃桌宠")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        try:
            self.root.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError:
            pass

        self.source = Image.open(ASSET_PATH).convert("RGBA")
        ratio = BASE_HEIGHT / self.source.height
        self.base_image = self.source.resize(
            (round(self.source.width * ratio), BASE_HEIGHT), Image.Resampling.LANCZOS
        )
        self.photo = None
        self.canvas = tk.Canvas(
            root,
            bg=TRANSPARENT_KEY,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.canvas.pack()

        self.drag_origin: tuple[int, int, int, int] | None = None
        self.dragged = False
        self.animating = False
        self.animation_started = 0.0
        self.render(1.0, center=None)
        self.place_initially()

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.show_menu)

        self.menu = tk.Menu(root, tearoff=False)
        self.menu.add_command(label="退出奶娃", command=self.close)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def place_initially(self) -> None:
        # Tk reports 1x1 until the canvas geometry has been flushed.
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - self.root.winfo_width() - 36
        y = screen_h - self.root.winfo_height() - 52
        self.root.geometry(f"+{max(0, x)}+{max(0, y)}")

    def render(self, inflate: float, center: tuple[float, float] | None) -> None:
        width = max(1, round(self.base_image.width * inflate))
        height = max(1, round(self.base_image.height * (1.0 + (inflate - 1.0) * 0.16)))
        frame = self.base_image.resize((width, height), Image.Resampling.LANCZOS)
        # Re-quantize after resizing; Tk color-key transparency turns blended
        # edge pixels into a visible halo otherwise.
        alpha = frame.getchannel("A").point(lambda value: 255 if value >= 128 else 0)
        frame.putalpha(alpha)
        self.photo = ImageTk.PhotoImage(frame)
        self.canvas.configure(width=width, height=height)
        self.canvas.delete("pet")
        self.canvas.create_image(width // 2, height // 2, image=self.photo, tags="pet")
        if center is None:
            return
        x = round(center[0] - width / 2)
        y = round(center[1] - height / 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def on_press(self, event: tk.Event) -> None:
        self.drag_origin = (
            event.x_root,
            event.y_root,
            self.root.winfo_x(),
            self.root.winfo_y(),
        )
        self.dragged = False

    def on_drag(self, event: tk.Event) -> None:
        if not self.drag_origin:
            return
        start_x, start_y, window_x, window_y = self.drag_origin
        dx = event.x_root - start_x
        dy = event.y_root - start_y
        if abs(dx) > 3 or abs(dy) > 3:
            self.dragged = True
        self.root.geometry(f"+{window_x + dx}+{window_y + dy}")

    def on_release(self, _event: tk.Event) -> None:
        if not self.dragged:
            self.inflate()
        self.drag_origin = None

    def inflate(self) -> None:
        if self.animating:
            return
        self.animating = True
        self.animation_started = time.perf_counter()
        self.animate_frame()

    def animate_frame(self) -> None:
        elapsed = (time.perf_counter() - self.animation_started) * 1000
        progress = min(1.0, elapsed / ANIMATION_MS)
        # A smooth pulse: grow quickly, then settle back to the original shape.
        pulse = math.sin(progress * math.pi)
        inflate = 1.0 + 0.085 * pulse
        center = (
            self.root.winfo_x() + self.root.winfo_width() / 2,
            self.root.winfo_y() + self.root.winfo_height() / 2,
        )
        self.render(inflate, center)
        if progress < 1.0:
            self.root.after(16, self.animate_frame)
        else:
            self.animating = False

    def show_menu(self, event: tk.Event) -> None:
        self.menu.tk_popup(event.x_root, event.y_root)

    def close(self) -> None:
        self.menu.grab_release()
        self.root.destroy()


def main() -> None:
    if not ASSET_PATH.exists():
        raise FileNotFoundError(f"Missing character asset: {ASSET_PATH}")
    root = tk.Tk()
    NaiwaPet(root)
    root.mainloop()


if __name__ == "__main__":
    main()
