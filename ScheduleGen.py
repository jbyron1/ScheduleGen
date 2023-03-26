import drawsvg as draw
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from Constants import *
import draw_functions as drawfunc
import colors

with open('example.json', 'r', encoding='utf-8') as jsonfile:
    event = json.load(jsonfile)

color_ids = []
time_zone_name = event['event']['time zone']
time_zone = ZoneInfo(time_zone_name)
for day in event['event']['days']:
    date = day['date']
    earliest_block = None
    latest_block = None
    num_streams = len(day['streams'])
    blocks_start_times = []
    for stream in day['streams']:
        stream_earliest = None
        stream_latest = None
        for block in stream['blocks']:
            color = block['color']
            if type(color) == int:
                color_ids.append(color)
            
            start_str = (date + ' ' + block['start'])
            start_dt = datetime.strptime(start_str, "%m-%d-%Y %H:%M:%S")
            start_dt = start_dt.replace(tzinfo = time_zone)
            blocks_start_times.append(start_dt)

            end_str = (date + ' ' + block['end'])
            end_dt = datetime.strptime(end_str, "%m-%d-%Y %H:%M:%S")
            end_dt = end_dt.replace(tzinfo = time_zone)

            if stream_earliest == None or start_dt < stream_earliest:
                stream_earliest = start_dt

            if stream_latest == None or end_dt > stream_latest:
                stream_latest = end_dt

        if earliest_block == None or stream_earliest < earliest_block:
            earliest_block = stream_earliest
        
        if latest_block == None or stream_latest > latest_block:
            latest_block = stream_latest

    blocks_start_times.sort()

    offset = None
    if latest_block.utcoffset() < timedelta(0):
        offset = -int((-latest_block.utcoffset().seconds + 86400) / 3600)
    else:
        offset = int(latest_block.utcoffset().seconds / 3600)

    offset = drawfunc.calc_offset(latest_block)

    color_ids = (list(set(color_ids)))
    color_palette = colors.gen_color_palette(event["event"]["color_palette"], len(color_ids))
    c_map = {}
    for c in color_ids:
        c_map[c] = color_palette[len(c_map)]


    diff = latest_block - earliest_block
    diff_s = diff.total_seconds()
    time_blocks = int(divmod(diff_s, 900)[0]) # + 1
    width_cells = STREAM_LOGO_BOX_WIDTH + STREAM_LINK_BOX_WIDTH + time_blocks*STREAM_15_MINUTE_WIDTH
    width_pixels = width_cells * CELL_WIDTH
    height_cells = STREAM_TIME_ZONE_BOX_HEIGHT + STREAM_LINK_BOX_HEIGHT * num_streams
    height_pixels = height_cells * CELL_HEIGHT

    thing = draw.Drawing(width_pixels, height_pixels + 1000)
    r = draw.Rectangle(0,0, width_pixels, height_pixels + 1000, stroke = 'black', stroke_width = 0, fill = "grey")
    thing.append(r)

    dayOut = drawfunc.draw_dayStreams(day, earliest_block, date, time_zone, c_map, event["event"]["time format"], time_blocks, blocks_start_times,
                                day, time_zone_name, offset)

    cv_tz =  ZoneInfo(event['event']['zones'][4]['identifier'])

    CV_box = drawfunc.draw_conversion_box(day, event['event']['zones'], time_blocks, blocks_start_times, transform=f"translate({0},{dayOut[1] + TIME_BOX_GAP_HEIGHT * CELL_HEIGHT}) ")

    thing.append(dayOut[2])
    thing.append(CV_box[2])
   

    thing.save_svg('best.svg')

    drawfunc.draw_day(day, event['event']['time zone'], event['event']['time format'], event['event']['zones'], c_map)
   

