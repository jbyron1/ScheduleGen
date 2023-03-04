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

class Image(draw.DrawingBasicElement):
    TAG_NAME = 'image'
    def __init__(self, x, y, width, height, href, preserveAspectRatio, target=None, **kwargs):
        super().__init__(x=x, y=y, width=width, href=href, preserveAspectRatio=preserveAspectRatio, target=target, **kwargs)


im = Image(10, 10, 60, 60, "./AELogo.png", "xMidYMid")
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
    for stream in day['streams']:
        stream_earliest = None
        stream_latest = None
        for block in stream['blocks']:
            start_str = (date + ' ' + block['start'])
            start_dt = datetime.strptime(start_str, "%m-%d-%Y %H:%M:%S")
            start_dt = start_dt.replace(tzinfo = time_zone)

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



    print(latest_block)
    diff = latest_block - earliest_block
    diff_s = diff.total_seconds()
    time_blocks = divmod(diff_s, 900)[0]
    width_cells = STREAM_LOGO_BOX_WIDTH + STREAM_LINK_BOX_WIDTH + time_blocks*STREAM_15_MINUTE_WIDTH
    width_pixels = width_cells * CELL_WIDTH
    height_cells = STREAM_TIME_ZONE_BOX_HEIGHT + STREAM_LINK_BOX_HEIGHT * num_streams
    height_pixels = height_cells * CELL_HEIGHT

    d = draw.Drawing(width_pixels + 10, height_pixels + 10)
    r = draw.Rectangle(0,0, width_pixels, height_pixels, stroke = 'black', stroke_width = 1, fill = "grey")
    cur_coords = (1,1)
    
    time_zone_group = draw.Group()
   
   
    stream_day = drawfunc.draw_day_box(day['day'])

    cur_coords = (cur_coords[0] + 0, cur_coords[1] + stream_day[1])
    stream_zone_name = drawfunc.draw_zone_name_box(time_zone_name)

    time_zone_group.append(stream_day[2])
    time_zone_group.append(stream_zone_name[2])

    obj_height = (STREAM_DAY_BOX_HEIGHT + STREAM_ZONE_NAME_HEIGHT) * CELL_HEIGHT
    obj_width = (STREAM_ZONE_NAME_WIDTH + STREAM_TIME_ZONE_BOX_WIDTH) * CELL_WIDTH
    time_zone_group.append(draw.Rectangle(0,0, obj_width, obj_height, stroke = "black", stroke_width = 1, fill='None'))

    

    d.append(r)
    #d.append(draw.Text('Basic text', 8, 10, 10, fill='blue'))
    #d.append(stream_day)
    #d.append(stream_zone_name)
    d.append(time_zone_group)
    d.save_svg('test2.svg')

        