import seaborn

def choose_textcolor(color):
    r = color[0] 
    g = color[1] 
    b = color[2] 
    yiq = ((r * 299) + (g*587) + (b* 114))/1000
    if yiq >= 128:
        return 'black'
    else:
        return 'white'

def gen_color_palette(palette, n):
    colors = seaborn.color_palette(palette, n)
    new_colors = []
    for color in colors:
        r = int(color[0] * 255)
        g = int(color[1] * 255)
        b = int(color[2] * 255)
        new_colors.append((r,g,b))
    return new_colors

def rgb_to_hex(color):
    return '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])

def hex_to_rgb(hex):
  rgb = []
  for i in (0, 2, 4):
    decimal = int(hex[i:i+2], 16)
    rgb.append(decimal)
  
  return tuple(rgb)