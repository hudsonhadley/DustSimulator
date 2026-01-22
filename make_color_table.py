def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    h %= 360

    chroma: float = v * s

    X: float = chroma * (1 - abs((h / 60) % 2 - 1))
    m: float = v - chroma

    if h < 60:
        r, g, b = (chroma, X, 0)
    elif h < 120:
        r, g, b = (X, chroma, 0)
    elif h < 180:
        r, g, b = (0, chroma, X)
    elif h < 240:
        r, g, b = (0, X, chroma)
    elif h < 300:
        r, g, b = (X, 0, chroma)
    else:
        r, g, b = (chroma, 0, X)

    return (int((r+m)*255), int((g+m)*255), int((b+m)*255))

def read_table(file: str) -> list[tuple[int, int, int]]:
    colors: list[tuple[int, int, int]] = []

    with open(file, 'rt', encoding='utf-8') as colors_in:
        for line in colors_in:
            if len(line) == 0:
                break
            r, g, b = line.strip().split(',')
            
            colors.append((int(r), int(g), int(b)))

    return colors


COLOR_COUNT = 1024
SATURATION = 1
VALUE = 1

delta = 360.0 / COLOR_COUNT

with open("color_table.csv", 'wt', encoding='utf-8') as table_out:
    for i in range(COLOR_COUNT):
        hue = i * delta

        r, g, b = hsv_to_rgb(hue, SATURATION, VALUE)
        table_out.write(f"{r},{g},{b}\n")
