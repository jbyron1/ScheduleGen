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

    d = draw.Drawing(width_pixels, height_pixels + 500)
    thing = draw.Drawing(width_pixels, height_pixels + 1000)
    r = draw.Rectangle(0,0, width_pixels, height_pixels + 1000, stroke = 'black', stroke_width = 0, fill = "grey")
    thing.append(r)
    d.append(r)
    #d.append(draw.Text('Basic text', 8, 10, 10, fill='blue'))
    #d.append(stream_day)
    #d.append(stream_zone_name)
    top_bar = drawfunc.draw_top_row(event["event"]["time format"],time_blocks, blocks_start_times, day, time_zone_name, offset)
    #stream_logo = drawfunc.draw_stream_logo(".\EVO1.png", transform=f"translate({0}, {top_bar[1] - .5})")
    #stream_link = drawfunc.draw_stream_link("twitch.tv/", "teamSp00ky", transform=f"translate( {stream_logo[0] - .5}, {top_bar[1] - .5})")
    #test_block = drawfunc.draw_block(8, "./Injustice2.png", "Street Fighter 4: AE", "Top 24 -> Top 8", "navy", transform=f"translate({stream_logo[0] + stream_link[0] - .5}, {top_bar[1] - .5})")
    ready_blocks = []
    for stream in day["streams"]:
        vertical_offset = (top_bar[1] - .5) + (len(ready_blocks) * ((STREAM_HOUR_BOX_HEIGHT * CELL_HEIGHT)))
        stream_row = drawfunc.draw_stream(stream, earliest_block, time_blocks, date, time_zone, c_map, transform=f"translate({0}, {vertical_offset})")
        #new_block = drawfunc.draw_stream_blocks("evo1", stream["blocks"], earliest_block, time_blocks, date, time_zone, transform=f"translate({stream_logo[0] + stream_link[0] - .5}, {top_bar[1] - .5})")
        ready_blocks.append(stream_row)
        

            
    dayOut = drawfunc.draw_dayStreams(day, earliest_block, time_blocks, date, time_zone, c_map, event["event"]["time format"], time_blocks, blocks_start_times,
                                day, time_zone_name, offset)

    conversion = drawfunc.draw_conversion_header(day, time_blocks, transform=f"translate({0}, {dayOut[1] + TIME_BOX_GAP_HEIGHT * CELL_HEIGHT})")
    zone_text = drawfunc.draw_conversion_row_text("US Pacific (CA)", transform=f"translate({0}, {dayOut[1] + conversion[1] + TIME_BOX_GAP_HEIGHT * CELL_HEIGHT})")
    offset_box = drawfunc.draw_conversion_offset_box(-8, transform=f"translate({zone_text[0]}, {dayOut[1] + conversion[1] + TIME_BOX_GAP_HEIGHT * CELL_HEIGHT})" )

    data_row = drawfunc.draw_timezone_cells(30, 18, transform=f"translate({offset_box[0] + zone_text[0]}, {dayOut[1] + conversion[1] + TIME_BOX_GAP_HEIGHT * CELL_HEIGHT})")

    cv_tz =  ZoneInfo(event['event']['zones'][4]['identifier'])
    #cv_row = drawfunc.draw_conversion_row_blocks(time_blocks, blocks_start_times,cv_tz, '24h', transform=f"translate({offset_box[0] + zone_text[0]}, {dayOut[1] + conversion[1] + TIME_BOX_GAP_HEIGHT * CELL_HEIGHT})")
    print(day)

    cv_row = drawfunc.draw_conversion_row(event['event']['zones'][4]['identifier'], time_blocks, blocks_start_times, event['event']['zones'][4]['format'], transform=f'translate({0}, {dayOut[1] + conversion[1] + TIME_BOX_GAP_HEIGHT * CELL_HEIGHT})')
    
    CV_box = drawfunc.draw_conversion_box(day, event['event']['zones'], time_blocks, blocks_start_times, transform=f"translate({0},{dayOut[1] + TIME_BOX_GAP_HEIGHT * CELL_HEIGHT}) ")

    item = drawfunc.draw_top_row(event["event"]["time format"],time_blocks, blocks_start_times, day, time_zone_name, offset, transform=f"translate({0}, {dayOut[1]})")
    thing.append(dayOut[2])
    thing.append(CV_box[2])
    #thing.append(conversion[2])
    #thing.append(zone_text[2])
    #thing.append(offset_box[2])
    #thing.append(cv_row[2])

    thing.save_svg('best.svg')
    d.append(top_bar[2])
    for stream in ready_blocks:
        d.append(stream[2])
    #d.append(test_block[2])
    #d.append(blank)
    d.save_svg('test2.svg')

