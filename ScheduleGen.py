import drawsvg as draw
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from Constants import *
import draw_functions as drawfunc

with open('example.json', 'r', encoding='utf-8') as jsonfile:
    event = json.load(jsonfile)

print(event)



d = draw.Drawing(500, 500)

r = draw.Rectangle(10, 10, 40, 50, fill='#1248ff')
r.append_title("recty")
d.append(r)



im = drawfunc.Image(10, 10, 60, 60, "./AELogo.png", "xMidYMid")
d.append(im)
d.save_svg('test.svg')



time_zone_name = event['event']['time zone']
time_zone = ZoneInfo(time_zone_name)
print(time_zone)
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
    dt = datetime(2022, 8, 4, 15, 15, tzinfo=time_zone) + timedelta(minutes=45)
    if dt in blocks_start_times:
        print("yeah boy")
    print(blocks_start_times)
    print(latest_block.utcoffset() > timedelta(0))
    offset = None
    if latest_block.utcoffset() < timedelta(0):
        offset = -int((-latest_block.utcoffset().seconds + 86400) / 3600)
    else:
        offset = int(latest_block.utcoffset().seconds / 3600)
    print(str(offset))


    diff = latest_block - earliest_block
    diff_s = diff.total_seconds()
    time_blocks = int(divmod(diff_s, 900)[0]) + 1
    width_cells = STREAM_LOGO_BOX_WIDTH + STREAM_LINK_BOX_WIDTH + time_blocks*STREAM_15_MINUTE_WIDTH
    width_pixels = width_cells * CELL_WIDTH
    height_cells = STREAM_TIME_ZONE_BOX_HEIGHT + STREAM_LINK_BOX_HEIGHT * num_streams
    height_pixels = height_cells * CELL_HEIGHT

    d = draw.Drawing(width_pixels, height_pixels)
    r = draw.Rectangle(0,0, width_pixels, height_pixels, stroke = 'black', stroke_width = 0, fill = "grey")
    
    d.append(r)
    #d.append(draw.Text('Basic text', 8, 10, 10, fill='blue'))
    #d.append(stream_day)
    #d.append(stream_zone_name)
    top_bar = drawfunc.draw_top_row(event["event"]["time format"],time_blocks, blocks_start_times, day, time_zone_name, offset)
    stream_logo = drawfunc.draw_stream_logo(".\EVO1.png", transform=f"translate({0}, {top_bar[1] - .5})")
    stream_link = drawfunc.draw_stream_link("twitch.tv/", "teamSp00ky", transform=f"translate( {stream_logo[0] - .5}, {top_bar[1] - .5})")
    for stream in day["streams"]:
        starts = []
        ends = []
        for block in stream["blocks"]:
            start_str = (date + ' ' + block['start'])
            start_dt = datetime.strptime(start_str, "%m-%d-%Y %H:%M:%S")
            start_dt = start_dt.replace(tzinfo = time_zone)

            end_str = (date + ' ' + block['end'])
            end_dt = datetime.strptime(end_str, "%m-%d-%Y %H:%M:%S")
            end_dt = end_dt.replace(tzinfo = time_zone)

            

        

    d.append(top_bar[2])
    d.append(stream_logo[2])
    d.append(stream_link[2])
    #d.append(blank)
    d.save_svg('test2.svg')

        