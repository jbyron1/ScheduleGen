import drawsvg as draw
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from Constants import *
import draw_functions as drawfunc
import colors

with open('Mixup2023.json', 'r', encoding='utf-8') as jsonfile:
    event = json.load(jsonfile)

color_ids = []
for day in event['event']['days']:
    for stream in day['streams']:
        for block in stream['blocks']:
            color = block['color']
            if type(color) == int:
                color_ids.append(color)
            


    color_ids = (list(set(color_ids)))
    color_palette = colors.gen_color_palette(event["event"]["color_palette"], len(color_ids))
    c_map = {}
    for c in color_ids:
        c_map[c] = color_palette[len(c_map)]



for day in event['event']['days']:
    drawfunc.draw_day(event['event']['name'], day, event['event']['time zone'], event['event']['zone_text'], event['event']['time format'], event['event']['zones'], c_map)
   
canvas = draw.Drawing(1000, 1000)

drawfunc.draw_tournament_box(event)


logo = drawfunc.draw_tourney_logo("E:\\Acekingoffsuit clone\\Tourney Logos\\DHSanDiego.png")
namebox = drawfunc.draw_tourney_name(event, transform=f"translate({logo[0]}, {0})")
infobox = drawfunc.draw_tourney_infobox(event, transform=f"translate({0}, {namebox[1]})")
disclaimerbox = drawfunc.draw_disclaimer(event, transform=f"translate({0}, {namebox[1] + infobox[1] + DISCLAIMER_GAP * CELL_HEIGHT})")
timedesc = drawfunc.draw_time_desc(event, transform=f"translate({0}, {logo[1] + (DISCLAIMER_GAP + TIME_EXPLANATION_GAP) * CELL_HEIGHT + infobox[1] + disclaimerbox[1]})")
canvas.append(logo[2])
canvas.append(namebox[2])
canvas.append(infobox[2])
canvas.append(disclaimerbox[2])
canvas.append(timedesc[2])

canvas.save_svg("tourneybox.svg")