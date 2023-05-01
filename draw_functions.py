from Constants import *
import drawsvg as draw
from datetime import datetime, timedelta
import colors as colr
import colorsys
from zoneinfo import ZoneInfo

def calc_offset(dt : datetime):
    offset = None
    if dt.utcoffset() < timedelta(0):
        offset = -int((-dt.utcoffset().seconds + 86400) / 3600)
    else:
        offset = int(dt.utcoffset().seconds / 3600)

    return offset


#CHECK THE Elements.py file in drawsvg before you reimplement any tags YOU FUCKING DUMBASS
class Image(draw.DrawingBasicElement):
    TAG_NAME = 'image'
    def __init__(self, x, y, width, height, href, preserveAspectRatio, target=None, **kwargs):
        super().__init__(x=x, y=y, width=width, href=href, preserveAspectRatio=preserveAspectRatio, target=target, **kwargs)

#draw the Day name in the top left corner of the graphic
def draw_day_box(day, transform=f"translate({0}, {0})"):
    stream_day = draw.Group(transform=transform, class_="Day")
    obj_height = STREAM_DAY_BOX_HEIGHT * CELL_HEIGHT
    obj_width =  STREAM_DAY_BOX_WIDTH * CELL_WIDTH
    stream_day.append(draw.Rectangle(0, 0, obj_width, obj_height, stroke = "yellow", stroke_width = 1, fill = 'yellow', shape_rendering="crispEdges"))
    stream_day.append(draw.Text(day , 18, obj_width/2, obj_height/2, center=True, fill="black", font_weight="bold", font_family="Arial"))
    stream_day.append_title("Stream Day")
    return obj_width, obj_height, stream_day

#draws the name of the time zone the event is taking place in
def draw_zone_name_box(zone_text,  transform=f"translate({0}, {0})"):
    stream_zone_text = draw.Group(transform=transform, class_="Zone Text")
    obj_height = STREAM_ZONE_NAME_HEIGHT * CELL_HEIGHT
    obj_width = STREAM_ZONE_NAME_WIDTH * CELL_WIDTH
    stream_zone_text.append(draw.Rectangle(0,0,obj_width, obj_height, stroke = "yellow", stroke_width = 1, fill = 'yellow',  shape_rendering="crispEdges"))
    stream_zone_text.append(draw.Text(zone_text, 12, obj_width/2, obj_height/2, center=True, fill="black", font_weight="bold", font_family="Arial"))
    stream_zone_text.append_title("Zone Text")
    return obj_width, obj_height, stream_zone_text

#combine the Day and the time zone name into one box
def draw_dayzone_box(day, zone_text, transform=f"translate({0}, {0})"):
    dayzone = draw.Group(transform=transform, class_="Day and Zone Text")
    
    stream_day = draw_day_box(day)
    zone_text = draw_zone_name_box(zone_text,transform=f"translate({0}, {stream_day[1]})")
    
    obj_width = stream_day[0]
    obj_height = stream_day[1] + zone_text[1]

    bg = draw.Rectangle(0,0, obj_width, obj_height, stroke = 'black', stroke_width = '0', shape_rendering="crispEdges")
    border = draw.Rectangle(0,0, obj_width, obj_height, stroke = 'black', stroke_width = 1, fill="none", shape_rendering="crispEdges")
    dayzone.append(bg)
    
    dayzone.append(stream_day[2])
    dayzone.append(zone_text[2])
    dayzone.append(border)
    dayzone.append_title("Day and Zone box")
    return obj_width, obj_height, dayzone

#draws the offset value from UTC that the event is taking place in
def draw_offset_box(offset,  transform=f"translate({0}, {0})"):
    offset_box = draw.Group(transform=transform, class_ = "UTC offset box")

    obj_height = STREAM_TIME_ZONE_BOX_HEIGHT * CELL_HEIGHT
    obj_width = STREAM_TIME_ZONE_BOX_WIDTH * CELL_WIDTH

    string = ""
    if offset >= 0:
        string = "UTC+" + str(offset)
    else:
        string = "UTC" + str(offset)
    
    offset_box.append(draw.Rectangle(0,0, obj_width, obj_height, stroke = "yellow", stroke_width = .5, fill = 'yellow', shape_rendering="crispEdges"))
    offset_box.append(draw.Rectangle(0,0, obj_width , obj_height, stroke = 'black', stroke_width = 1, fill="none", shape_rendering="crispEdges"))
    offset_box.append(draw.Text(string, 14, obj_width/2, obj_height/2, center=True, fill="black", font_weight="bold", font_family="Arial"))
    offset_box.append_title("Offset From UTC box")
    return obj_width, obj_height, offset_box

#combine the day and time zone name box with the utc offset box
def draw_dtz_box(day, zone_text, offset,transform=f"translate({0}, {0})"):
    dtz = draw.Group(transform=transform, class_ = "Day, Zone, Offset Box")
    dayzone = draw_dayzone_box(day['day'], zone_text)
    offset_box = draw_offset_box(offset, transform=f"translate({dayzone[0] - 0}, {0})")
    dtz.append(dayzone[2])
    dtz.append(offset_box[2])
    obj_width = dayzone[0] + offset_box[0]
    obj_height = dayzone[1]
    dtz.append_title("Day/Zone/Offset box")
    return obj_width, obj_height, dtz

#draw empty time cells 
def draw_blank_time_cell(num_cells, transform=f"translate({0}, {0})"):
    obj_width = STREAM_15_MINUTE_WIDTH * CELL_WIDTH * num_cells
    obj_height = STREAM_TIME_ZONE_BOX_HEIGHT * CELL_HEIGHT
    blank_cell = draw.Rectangle(0,0, obj_width, obj_height, fill ="black",  stroke_width = 1, stroke = 'black', transform=transform,  shape_rendering="crispEdges")
    return obj_width, obj_height, blank_cell

#draw time cell with a time in it
def draw_pop_time_cell(time, transform=f"translate({0}, {0})"):
    obj_width = 2 * STREAM_15_MINUTE_WIDTH * CELL_WIDTH
    obj_height = STREAM_TIME_ZONE_BOX_HEIGHT * CELL_HEIGHT
    filled_cell = draw.Group(transform=transform)
    text = draw.Text(time, 16,  obj_width/10, obj_height - (obj_height/3), center=False, fill= "white", font_weight="bold", font_family="Arial",  shape_rendering="crispEdges")
    block = draw.Rectangle(0,0, obj_width, obj_height, fill ="black")
    filled_cell.append(block)
    filled_cell.append(text)
    return obj_width, obj_height, filled_cell

#convert the time to the format specified in the json
def time_convert(format, datetime):
    time_str = ''
    if format == '12h':
        time_str = datetime.strftime("%I:%M %p")
        if time_str[3] == '0':
            time_str = time_str[:2] + time_str[6:]
        else: 
            time_str = time_str[:5] + time_str[6:]
        if time_str[0] == '0':
            time_str = time_str[1:]
    else:
        time_str = datetime.strftime("%H:%M")

    return time_str

#draw the entire row of time cells, first the blanks, and then the populated on top of it
def draw_time_cells(time_format, cell_count, block_list,  transform=f"translate({0}, {0})"):
    times = draw.Group(transform=transform, class_="time cells")
    cell = draw_blank_time_cell(cell_count)
    obj_width = cell[0]
    obj_height = cell[1]
    times.append(cell[2])
    start_time = block_list[0]
    prev_start = None
    for block in block_list:    
        if(prev_start and (block - prev_start).total_seconds() <= 1200):
            continue
        diff = (block - start_time)
        diff_s = diff.total_seconds()
        time_blocks = int(divmod(diff_s, 900)[0])
        time_str = time_convert(time_format, block)
        time_block = draw_pop_time_cell(time_str, transform=f"translate({(time_blocks * CELL_WIDTH * STREAM_15_MINUTE_WIDTH) - 0}, {0})")
        times.append(time_block[2])
        prev_start = block
    times.append_title("time row")
    return obj_width, obj_height, times

#draw the entire top row with date and time zone location, as well as the times of each block start
def draw_top_row(time_format, cell_count, block_list, day, zone_text, offset, transform = f"translate({0}, {0})"):
    dtz = draw_dtz_box(day, zone_text, offset)
    time_bar = draw_time_cells(time_format, cell_count, block_list, transform=f"translate({dtz[0] - 0}, {0})")

    top_bar = draw.Group(transform= transform, class_ = "Top Row")
    top_bar.append(dtz[2])
    top_bar.append(time_bar[2])

    obj_width = dtz[0] + time_bar[0]
    obj_height = time_bar[1]
    top_bar.append_title("Top Bar info")

    return obj_width, obj_height, top_bar

#draws the logo of a stream
def draw_stream_logo(file_location, transform=f"translate({0}, {0})"):
    obj_width = STREAM_LOGO_BOX_WIDTH * CELL_WIDTH
    obj_height = STREAM_LOGO_BOX_HEIGHT * CELL_HEIGHT

    img_height = 2*CELL_HEIGHT
    img_width = CELL_WIDTH

    img_x = (obj_width - img_width)/2
    img_y = (obj_height - img_height)/2

    logobox = draw.Group(transform = transform, class_="stream logo")
    bg = draw.Rectangle(0,0, obj_width, obj_height, fill="white", stroke = 'black', stroke_width = '0',  shape_rendering="crispEdges")
    border = draw.Rectangle(0,0, obj_width , obj_height, stroke = 'black', stroke_width = 1, fill="none",  shape_rendering="crispEdges")
    image = draw.Image(img_x, img_y, img_width, img_height, file_location)
    logobox.append(bg)
    logobox.append(image)
    logobox.append(border)

    return obj_width, obj_height, logobox

#displays a link to the stream
#TODO make the background different colors for twitch/youtube/etc
def draw_stream_link(platform, streamer, transform=f"translate({0}, {0})"):
    obj_width = STREAM_LINK_BOX_WIDTH * CELL_WIDTH
    obj_height = STREAM_LINK_BOX_HEIGHT * CELL_HEIGHT

    linkbox = draw.Group(transform = transform, class_="stream link")
    bg = draw.Rectangle(0,0, obj_width, obj_height, fill="pink", stroke = 'black', stroke_width = '0',  shape_rendering="crispEdges")
    border = draw.Rectangle(0,0, obj_width, obj_height, stroke = 'black', stroke_width = 1, fill="none",  shape_rendering="crispEdges")
    plat = draw.Text(platform, 10, obj_width/2, obj_height/4, center=True, font_weight="bold", font_family="Arial")
    link = draw.Text(streamer, 14, obj_width/2, 5*obj_height/8, center=True, font_weight="bold", font_family="Arial")

    linkbox.append(bg)
    linkbox.append(plat)
    linkbox.append(link)
    linkbox.append(border)

    return obj_width, obj_height, linkbox

#draw a stream block for a single block
def draw_block(length, game_image, game_name, round, color, text_color, transform=f"translate({0}, {0})"):
    obj_width = length * STREAM_15_MINUTE_WIDTH * CELL_WIDTH
    obj_height = STREAM_HOUR_BOX_HEIGHT * CELL_HEIGHT

    img_height = 1.9 * CELL_HEIGHT
    img_width = 1.9 * CELL_WIDTH

    img_x = ((2 * STREAM_15_MINUTE_WIDTH * CELL_WIDTH) - img_width )/ 2
    img_y = (obj_height - img_height)/2
    
    round_text = draw.Text(round, 14, 2 * STREAM_15_MINUTE_WIDTH * CELL_WIDTH, 3*obj_height/4, font_weight="bold", font_family="Arial", fill=text_color)
    border = draw.Rectangle(0,0, obj_width, obj_height, stroke = 'black', stroke_width = 1, fill=color, shape_rendering="crispEdges")
    block = draw.Group(transform = transform, class_ = game_name + " " + round)
    block.append_title(game_name + round)
    block.append(border)
    if game_image != None and game_image != "":
        game_logo = draw.Image(img_x + 2, img_y, img_width - 4, img_height - 4, game_image)
        block.append(game_logo)

    game_name_text = draw.Text(game_name, 14, 2*STREAM_15_MINUTE_WIDTH*CELL_WIDTH, obj_height/3, font_weight="bold", font_family="Arial", fill=text_color)
    block.append(game_name_text)
    block.append(round_text)
    

    return obj_width, obj_height, block


#draw all blocks for a stream on a day
def draw_stream_blocks(stream, blocks, start_time, time_blocks, date, time_zone, color_map, transform=f"translate({0}, {0})"):
    stream_blocks = draw.Group(transform=transform, class_ = stream)
    stream_blocks.append_title(stream + " Blocks")
    for block in blocks:
            start_str = (date + ' ' + block['start'])
            start_dt = datetime.strptime(start_str, "%m-%d-%Y %H:%M:%S")
            start_dt = start_dt.replace(tzinfo = time_zone)

            end_str = (date + ' ' + block['end'])
            end_dt = datetime.strptime(end_str, "%m-%d-%Y %H:%M:%S")
            end_dt = end_dt.replace(tzinfo = time_zone)

            #look into the cast to int if things are being weird

            game = block["game"]
            round = block["round"]
            path = block["game_logo"]
            shift = block["shifted"]
            
            diff = end_dt - start_dt
            diff_s = diff.total_seconds()
            duration =  int(divmod(diff_s, 900)[0])

            offset = start_dt-start_time
            offset_s = offset.total_seconds()
            offset_cells = int(divmod(offset_s, 900)[0])

            colors=["red", "orange", "green", "tan"]
            if type(block["color"]) == int:
                color = color_map[block["color"]]
            else:
                color = colr.hex_to_rgb(block["color"])
            if shift:
                hsv = colorsys.rgb_to_hsv(color[0]/255.0, color[1]/255.0, color[2]/255.0)
                color = colorsys.hsv_to_rgb(hsv[0], hsv[1] - .2, hsv[2])
                r = int(color[0] * 255)
                g = int(color[1] * 255)
                b = int(color[2] * 255)
                color = (r,g,b)
            text_color = colr.choose_textcolor(color)
            color = colr.rgb_to_hex(color)
            block = draw_block(duration, path,game, round, color, text_color, transform=f"translate({(offset_cells*CELL_WIDTH*STREAM_15_MINUTE_WIDTH)}, {0})")
            stream_blocks.append(block[2])
    
    obj_height = STREAM_HOUR_BOX_HEIGHT * CELL_HEIGHT
    obj_width = STREAM_15_MINUTE_WIDTH * time_blocks * CELL_WIDTH

    border = draw.Rectangle(0,0, obj_width, obj_height, stroke = 'black', stroke_width = 1, fill="none", shape_rendering="crispEdges")

    stream_blocks.append(border)


    return obj_width, obj_height, stream_blocks

#draw all information for a single stream for a day
def draw_stream(stream, start_time, time_blocks, date, time_zone, color_map, transform=f"translate({0}, {0})"):
    stream_row = draw.Group(transform=transform, class_=stream["stream"])
    stream_name = stream["stream"]
    stream_logo = draw_stream_logo(stream['stream_logo'])
    stream_logo[2]
    stream_link = draw_stream_link(stream["platform"], stream_name, transform=f"translate( {stream_logo[0] - 0}, {0})")
    stream_link[2]
    #drawfunc.draw_stream_blocks(", stream["blocks"], earliest_block, time_blocks, date, time_zone, transform=f"translate({stream_logo[0] + stream_link[0] - .5}, {top_bar[1] - .5})")
    stream_blocks = draw_stream_blocks(stream_name, stream["blocks"], start_time, time_blocks, date, time_zone, color_map,
                                       transform=f"translate({stream_logo[0] + stream_link[0] - 0}, {0})")
    
    obj_height = STREAM_HOUR_BOX_HEIGHT * CELL_HEIGHT
    obj_width = stream_logo[0] + stream_link[0] + stream_blocks[0]

    stream_row.append(stream_logo[2])
    stream_row.append(stream_link[2])
    stream_row.append(stream_blocks[2])

    stream_row.append_title(stream_name + " Row")

    return obj_width, obj_height, stream_row

#draw all the streams for a day
def draw_dayStreams(day, start_time, date, time_zone, color_map, time_format,
             cell_count, block_list, dayName, zone_text, offset, transform=f"translate({0}, {0})"):

    dayGroup = draw.Group(transform=transform, class_="Days streams")
    top_bar = draw_top_row(time_format, cell_count, block_list, dayName, zone_text, offset)
    obj_width = top_bar[0]
    obj_height = top_bar[1]
    dayGroup.append(top_bar[2])
    ready_blocks = []
    for stream in day["streams"]:
        vertical_offset = (top_bar[1] - 0) + (len(ready_blocks) * ((STREAM_HOUR_BOX_HEIGHT * CELL_HEIGHT)))
        obj_height += STREAM_HOUR_BOX_HEIGHT * CELL_HEIGHT
        stream_row = draw_stream(stream,start_time, cell_count, date, time_zone, color_map, transform=f"translate({0}, {vertical_offset})")
        ready_blocks.append(stream_row)
        dayGroup.append(stream_row[2])

    return obj_width, obj_height, dayGroup

#draw the box that says what day the time zones are
def draw_conversion_header(day, num_cells, transform=f"translate({0}, {0})"):
    obj_width = (STREAM_TIME_ZONE_BOX_WIDTH + STREAM_DAY_BOX_WIDTH + (STREAM_15_MINUTE_WIDTH * num_cells)) * CELL_WIDTH
    obj_height = CONVERSION_HEADER_HEIGHT * CELL_HEIGHT
    rectangle = draw.Rectangle(0,0,obj_width,obj_height, fill ="black", stroke="black", stroke_width = 1, shape_rendering="crispEdges")
    days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
    next_day = (days.index(day['day'].upper()) + 1) % 7
    prev_day = (days.index(day['day'].upper()) - 1) % 7
    text = draw.Text("ADDITIONAL TIME ZONES - " + day['day'].upper() , 18, obj_width/2, obj_height/2, center=True, fill="white", font_weight="bold", font_family="Arial")
    text.append(draw.TSpan("(" + days[prev_day].lower().capitalize() +" in gold, ", font_size="18",  fill="white", font_weight="bold", font_family="Arial"))
    text.append(draw.TSpan( "" + days[next_day].lower().capitalize() +" in blue)", font_size="18",  fill="white", font_weight="bold", font_family="Arial"))
    header = draw.Group(transform=transform)
    header.append(rectangle)
    header.append(text)
    return obj_width, obj_height, header

#draw the time zone name
def draw_conversion_row_text(text, transform=f"translate({0}, {0})"):
    obj_width = TIME_ZONE_TEXT_WIDTH * CELL_WIDTH
    obj_height = TIME_ZONE_ROW_HEIGHT * CELL_HEIGHT
    rectangle = draw.Rectangle(0,0, obj_width, obj_height, stroke= "black", stroke_width = 1, fill = "white", shape_rendering="crispEdges" )
    rowText = draw.Text(text, 16, obj_width/2, obj_height/2, center=True, font_family="Arial", fill="black", font_weight="bold")
    row_text_box = draw.Group(transform=transform)
    row_text_box.append(rectangle)
    row_text_box.append(rowText)
    return obj_width, obj_height, row_text_box

#draws the offset value from UTC for the zone being converted to
def draw_conversion_offset_box(offset,  transform=f"translate({0}, {0})"):
    offset_box = draw.Group(transform=transform)

    obj_height = TIME_ZONE_ROW_HEIGHT * CELL_HEIGHT
    obj_width = TIME_ZONE_OFFSET_WIDTH * CELL_WIDTH

    string = ""
    if offset >= 0:
        string = "UTC+" + str(offset)
    else:
        string = "UTC" + str(offset)
    offset_box.append(draw.Rectangle(0,0, obj_width, obj_height, stroke = "black", stroke_width = 0, fill = 'white', shape_rendering="crispEdges"))
    offset_box.append(draw.Rectangle(0,0, obj_width , obj_height, stroke = 'black', stroke_width = 1, fill="none", shape_rendering="crispEdges"))
    offset_box.append(draw.Text(string, 14, obj_width/2, obj_height/2, center=True, fill="black", font_weight="bold", font_family="Arial"))
    return obj_width, obj_height, offset_box

#draws the blank cells in the correct colors corresponding to the days
def draw_timezone_cells(day0_count, day1_count, day2_count, transform=f"translate({0}, {0})"):
    conversion_data_row = draw.Group(transform=transform)

    obj_height = TIME_ZONE_ROW_HEIGHT * CELL_HEIGHT
    obj_width = (day0_count + day1_count + day2_count) * STREAM_15_MINUTE_WIDTH * CELL_WIDTH

    conversion_data_row.append(draw.Rectangle(0,0, day0_count * STREAM_15_MINUTE_WIDTH * CELL_WIDTH, obj_height, stroke = "black", stroke_width = 0, fill= " #FFD700", shape_rendering="crispEdges"))
    conversion_data_row.append(draw.Rectangle((day0_count * STREAM_15_MINUTE_WIDTH * CELL_WIDTH), 0, (day1_count * STREAM_15_MINUTE_WIDTH * CELL_WIDTH), obj_height, stroke="black", stroke_width = 0, fill = "white", shape_rendering="crispEdges"))
    conversion_data_row.append(draw.Rectangle(((day1_count + day0_count) * STREAM_15_MINUTE_WIDTH * CELL_WIDTH), 0, (day2_count * STREAM_15_MINUTE_WIDTH * CELL_WIDTH), obj_height, stroke="black", stroke_width = 0, fill = " #6699cc", shape_rendering="crispEdges"))
    conversion_data_row.append(draw.Rectangle(0,0, obj_width, obj_height, fill = "none", stroke = "black", stroke_width = 1, shape_rendering="crispEdges"))

    return obj_width, obj_height, conversion_data_row

#draw time cell with a time in it
def draw_cv_time_cell(time, transform=f"translate({0}, {0})"):
    obj_width = 2 * STREAM_15_MINUTE_WIDTH * CELL_WIDTH
    obj_height = TIME_ZONE_ROW_HEIGHT * CELL_HEIGHT
    filled_cell = draw.Group(transform=transform)
    text = draw.Text(time, 16,  obj_width/10, obj_height - (obj_height/3), center=False, fill= "black", font_family="Arial",  shape_rendering="crispEdges")
    block = draw.Rectangle(0,0, obj_width, obj_height, fill ="none")
    filled_cell.append(block)
    filled_cell.append(text)
    return obj_width, obj_height, filled_cell

#draws the converted times
def draw_conversion_row_blocks(cell_count, block_start_times, conversion_zone, format, transform=f"translate({0}, {0})"):
    times = draw.Group(transform=transform)

    start_time = block_start_times[0]
    start_day = start_time.day
    cur_step = start_time.astimezone(conversion_zone)
    day1_blocks = 0
    day0_blocks = 0
    total_blocks = 0
    while total_blocks < cell_count and (cur_step.day < start_day or (cur_step.month < start_time.month)):
        day0_blocks += 1
        cur_step = cur_step + timedelta(minutes=15)
        total_blocks = day0_blocks
    while total_blocks < cell_count and (cur_step.day == start_day):
        day1_blocks +=1
        cur_step = cur_step + timedelta(minutes=15)
        total_blocks = day0_blocks + day1_blocks

    day2_blocks = cell_count - day1_blocks - day0_blocks
    tz_blanks = draw_timezone_cells(day0_blocks, day1_blocks, day2_blocks)

    start_time = start_time.astimezone(conversion_zone)
    times.append(tz_blanks[2])
    obj_width = tz_blanks[0]
    obj_height = tz_blanks[1]
    prev_block = None
    for block in block_start_times: 
        cv_block = block.astimezone(conversion_zone)   
        if(prev_block and (block - prev_block).total_seconds() <= 900):
            continue
        diff = (cv_block - start_time)
        diff_s = diff.total_seconds()
        time_blocks = int(divmod(diff_s, 900)[0])
        time_str = time_convert(format, cv_block)
        time_block = draw_cv_time_cell(time_str, transform=f"translate({(time_blocks * CELL_WIDTH * STREAM_15_MINUTE_WIDTH) - 0}, {0})")
        times.append(time_block[2])
        prev_block = block

    return obj_width, obj_height, times

#draw a complete converted row for a time zone
def draw_conversion_row(tz_text, tz_name, time_blocks, block_times, format,  transform=f"translate({0}, {0})"):
    CV_Row = draw.Group(transform=transform)

    tz = ZoneInfo(tz_name)
    offset = calc_offset(block_times[0].astimezone(tz))

    CV_Text = draw_conversion_row_text(tz_text)
    CV_Offset = draw_conversion_offset_box(offset, transform=f'translate({CV_Text[0]}, {0})')
    CV_Times = draw_conversion_row_blocks(time_blocks, block_times, tz, format, transform=f'translate({CV_Text[0] + CV_Offset[0]}, {0})')

    CV_Row.append(CV_Text[2])
    CV_Row.append(CV_Offset[2])
    CV_Row.append(CV_Times[2])

    obj_height = TIME_ZONE_ROW_HEIGHT
    obj_width = CV_Text[0] + CV_Offset[0] + CV_Times[0]

    return obj_width, obj_height, CV_Row

#draw all converted time zones
def draw_conversion_box(day, zones, time_blocks, block_times,  transform=f"translate({0}, {0})"):
    CV_Box = draw.Group(transform=transform)

    CV_Header = draw_conversion_header(day, time_blocks)

    obj_width = CV_Header[0]
    obj_height = CV_Header[1]

    CV_Box.append(CV_Header[2])
    drawn_zones = 0
    for zone in zones:
        vertical_offset = CV_Header[1] + (drawn_zones * TIME_ZONE_ROW_HEIGHT * CELL_HEIGHT)
        obj_height += TIME_ZONE_ROW_HEIGHT * CELL_HEIGHT
        CV_Row = draw_conversion_row(zone['text'],zone['identifier'], time_blocks, block_times, zone['format'], transform=f"translate({0}, {vertical_offset})")
        CV_Box.append(CV_Row[2])
        drawn_zones += 1

    return obj_width, obj_height, CV_Box

#draw the entirety of a stream day
def draw_day(event_name, day, time_zone_name, zone_text, format, cv_zones, c_map):
    
    earliest = None
    latest = None
    host_zone = ZoneInfo(time_zone_name)
    date = day['date']
    start_times = []
    for stream in day['streams']:
        for block in stream['blocks']:
            start_str = date + ' ' + block['start']
            start_dt = datetime.strptime(start_str, "%m-%d-%Y %H:%M:%S")
            start_dt = start_dt.replace(tzinfo=host_zone)
            start_times.append(start_dt)

            end_str = date + ' ' + block['end']
            end_dt = datetime.strptime(end_str, "%m-%d-%Y %H:%M:%S")
            end_dt = end_dt.replace(tzinfo=host_zone)

            if earliest == None or start_dt < earliest:
                earliest = start_dt

            if latest == None or latest < end_dt:
                latest = end_dt

    start_times.sort()
    
    offset = calc_offset(earliest)

    diff = latest - earliest
    diff_s = diff.total_seconds()
    num_time_blocks = int(divmod(diff_s, 900)[0])

    streams = draw_dayStreams(day, earliest, date, host_zone, c_map, format, num_time_blocks, start_times, day, zone_text, offset, transform=f"translate({BLEED_WIDTH * CELL_WIDTH}, {BLEED_HEIGHT * CELL_HEIGHT})")
    cv_box = draw_conversion_box(day, cv_zones, num_time_blocks, start_times, transform=f"translate({BLEED_WIDTH * CELL_WIDTH}, {streams[1] + (TIME_BOX_GAP_HEIGHT * CELL_HEIGHT) + (BLEED_HEIGHT * CELL_HEIGHT)})")

    width = streams[0] + (2*BLEED_WIDTH * CELL_WIDTH)
    height = streams[1] + cv_box[1] + (TIME_BOX_GAP_HEIGHT * CELL_HEIGHT) + (2 * BLEED_HEIGHT * CELL_HEIGHT)
    day_canvas = draw.Drawing(width, height)
    day_canvas.append(draw.Rectangle(0,0,width, height, fill="grey"))
    day_canvas.append(streams[2])
    day_canvas.append(cv_box[2])

    filename = event_name + day['day'] + '.svg'
    day_canvas.save_svg(filename)
    #day_canvas.rasterize(filename)


def draw_tourney_logo(file_location, transform=f"translate({0}, {0})"):
    obj_width = TOURNAMENT_LOGO_WIDTH * CELL_WIDTH
    obj_height = TOURNAMENT_LOGO_HEIGHT * CELL_HEIGHT

    img_height = .95 * obj_height
    img_width = .95 * obj_width

    img_x = (obj_width - img_width)/2
    img_y = (obj_height - img_height)/2

    logobox = draw.Group(transform = transform, class_="tournament logo")
    bg = draw.Rectangle(0,0, obj_width, obj_height, fill="black", stroke = 'black', stroke_width = '1',  shape_rendering="crispEdges")
    border = draw.Rectangle(0,0, obj_width , obj_height, stroke = 'black', stroke_width = 1, fill="none",  shape_rendering="crispEdges")
    image = draw.Image(img_x, img_y, img_width, img_height, file_location)
    logobox.append(bg)
    logobox.append(image)
    logobox.append(border)

    return obj_width, obj_height, logobox

def draw_tourney_name(event,  transform=f"translate({0}, {0})"):
    obj_width = TOURNAMENT_TITLE_WIDTH * CELL_WIDTH
    obj_height = TOURNAMENT_TITLE_HEIGHT * CELL_HEIGHT

    namebox = draw.Group(transform=transform, class_="tournament name")
    bg = draw.Rectangle(0,0, obj_width, obj_height, fill="black", stroke = 'black', stroke_width = '1', shape_rendering="crispEdges")
    text1 = draw.Text(event['event']['title_line1'], 24, obj_width/2, obj_height * .4 , center = True, fill="white", font_weight="bold", font_family="Arial")
    text2 = draw.Text(event['event']['title_line2'], 24, obj_width/2, obj_height * .6, center = True, fill="white", font_weight="bold", font_family="Arial")

    namebox.append(bg)
    namebox.append(text1)
    namebox.append(text2)
    return obj_width, obj_height, namebox

def draw_tourney_infobox(event, transform=f"translate({0}, {0})"):
    obj_height = TOURNAMENT_INFO_BOX_HEIGHT * CELL_HEIGHT
    obj_width = TOURNAMENT_INFO_BOX_WIDTH * CELL_WIDTH

    line_height = obj_height/3

    infobox = draw.Group(transform=transform, class_="tournament infobox")

    line1_bg = draw.Rectangle(0,0, obj_width, line_height, fill= 'white', stroke = 'white', stroke_width = '1', shape_rendering="crispEdges")
    line2_bg = draw.Rectangle(0,line_height, obj_width, line_height, fill= 'white', stroke = 'white', stroke_width = '1', shape_rendering="crispEdges")
    line3_bg = draw.Rectangle(0,2 * line_height, obj_width, line_height, fill= 'white', stroke = 'white', stroke_width = '1', shape_rendering="crispEdges")
    line1_text = draw.Text(event['event']['dates'], 18, obj_width/2, line_height/2 , center = True, fill="black", font_weight="bold", font_family="Calibri")
    line2_text = draw.Text(event['event']['location'], 18, obj_width/2, (line_height/2) + line_height , center = True, fill="black", font_weight="bold", font_family="Calibri")
    line3_str = event['event']['twitter'] + " | " + event['event']['hashtag']
    line3_text = draw.Text(line3_str, 18, obj_width/2, (line_height/2) + (2*line_height) , center = True, fill="black", font_weight="bold", font_family="Calibri")
    border = draw.Rectangle(0,0,obj_width, obj_height, fill="none", stroke = "black", stroke_width = 1, shape_rendering="crispEdges")

    
    infobox.append(line1_bg)
    infobox.append(line2_bg)
    infobox.append(line3_bg)
    infobox.append(line1_text)
    infobox.append(line2_text)
    infobox.append(line3_text)
    infobox.append(border)

    return obj_width, obj_height, infobox

def draw_disclaimer(event, transform=f"translate({0}, {0})"):
    disclaimerbox = draw.Group(transform=transform, class_='disclaimerbox')

    obj_width = DISCLAIMER_WIDTH * CELL_WIDTH
    disc_height = DISCLAIMER_HEADER_HEIGHT * CELL_HEIGHT
    obj_height = DISCLAIMER_HEIGHT * CELL_HEIGHT + disc_height
    line_height = (DISCLAIMER_HEIGHT * CELL_HEIGHT) / 3


    warningBox = draw.Rectangle(0,0, obj_width, disc_height, fill = "yellow", stroke = 'black', stroke_width = '1', shape_rendering="crispEdges")
    warningText = draw.Text("ALL TIMES SUBJECT TO CHANGE", 22, obj_width/2, disc_height/2, center = True, fill="black", font_weight="bold", font_family="Calibri")
    line1_bg = draw.Rectangle(0, disc_height, obj_width, line_height, fill = "white", stroke = "white", stroke_width = 1, shape_rendering="crispEdges")
    line2_bg = draw.Rectangle(0, disc_height + line_height, obj_width, line_height, fill = "white", stroke = "white", stroke_width = 1, shape_rendering="crispEdges")
    line3_bg = draw.Rectangle(0, disc_height + 2 * line_height, obj_width, line_height, fill = "white", stroke = "white", stroke_width = 1, shape_rendering="crispEdges")
    border = draw.Rectangle(0,0, obj_width, obj_height, fill="none", stroke = "black", stroke_width = 1, shape_rendering="crispEdges")
    line1_str = "This is an unofficial schedule by " + event['event']['scheduler']
    line2_str = "The most recent official schedule can be found at:"
    line3_str = event['event']['official_schedule']
    line1 = draw.Text(line1_str, 15, obj_width/2, disc_height + .5*line_height, center = True, fill="black", font_family="Calibri")
    line2 = draw.Text(line2_str, 15, obj_width/2, disc_height + 1.5 * line_height, center = True, fill="black", font_family="Calibri")
    line3 = draw.Text(line3_str, 22, obj_width/2, disc_height + 2.5*line_height, center = True, fill="black", font_family="Calibri",  font_weight="bold")
    
    
    disclaimerbox.append(line1_bg)
    disclaimerbox.append(line2_bg)
    disclaimerbox.append(line3_bg)
    disclaimerbox.append(warningBox)
    disclaimerbox.append(warningText)
    disclaimerbox.append(border)
    disclaimerbox.append(line1)
    disclaimerbox.append(line2)
    disclaimerbox.append(line3)

    return obj_width, obj_height, disclaimerbox

def draw_time_desc(event, transform=f"translate({0}, {0})"):
    timedesc = draw.Group(transform=transform, class_='time description box')

    obj_width = DISCLAIMER_WIDTH * CELL_WIDTH
    disc_height = DISCLAIMER_HEADER_HEIGHT * CELL_HEIGHT
    obj_height = DISCLAIMER_HEIGHT * CELL_HEIGHT + disc_height
    line_height = (DISCLAIMER_HEIGHT * CELL_HEIGHT) / 3

    offset = calc_offset(datetime.now().astimezone(ZoneInfo(event['event']['time zone'])))

    off_string = ""
    if offset >= 0:
        off_string = "UTC+" + str(offset)
    else:
        off_string = "UTC" + str(offset)

    warningBox = draw.Rectangle(0,0, obj_width, disc_height, fill = "yellow", stroke = 'black', stroke_width = '1', shape_rendering="crispEdges")
    warning_str = "Times in the black bars are " + event['event']['zone_text'] + '(' + off_string + ')'
    warningText = draw.Text(warning_str, 22, obj_width/2, disc_height/2, center = True, fill="black", font_weight="bold", font_family="Calibri")
    line1_bg = draw.Rectangle(0, disc_height, obj_width, line_height, fill = "white", stroke = "white", stroke_width = 1, shape_rendering="crispEdges")
    line2_bg = draw.Rectangle(0, disc_height + line_height, obj_width, line_height, fill = "white", stroke = "white", stroke_width = 1, shape_rendering="crispEdges")
    line3_bg = draw.Rectangle(0, disc_height + 2 * line_height, obj_width, line_height, fill = "white", stroke = "white", stroke_width = 1, shape_rendering="crispEdges")
    border = draw.Rectangle(0,0, obj_width, obj_height, fill="none", stroke = "black", stroke_width = 1, shape_rendering="crispEdges")
    line1_str = "For additional time zones,"
    line2_str = "please use the conversion charts"
    line3_str = "at the bottom of each days schedule."
    line1 = draw.Text(line1_str, 18, obj_width/2, disc_height + .5*line_height, center = True, fill="black", font_family="Calibri")
    line2 = draw.Text(line2_str, 18, obj_width/2, disc_height + 1.5 * line_height, center = True, fill="black", font_family="Calibri")
    line3 = draw.Text(line3_str, 18, obj_width/2, disc_height + 2.5*line_height, center = True, fill="black", font_family="Calibri",  font_weight="bold")
    
    
    timedesc.append(line1_bg)
    timedesc.append(line2_bg)
    timedesc.append(line3_bg)
    timedesc.append(warningBox)
    timedesc.append(warningText)
    timedesc.append(border)
    timedesc.append(line1)
    timedesc.append(line2)
    timedesc.append(line3)

    return obj_width, obj_height, timedesc

def draw_tournament_box(event, transform=f"translate({0}, {0})" ):
    

    logo = draw_tourney_logo("E:\\Acekingoffsuit clone\\Tourney Logos\\the-mixup-2018-2.png",transform=f"translate({BLEED_WIDTH * CELL_WIDTH}, {BLEED_HEIGHT * CELL_HEIGHT})")
    namebox = draw_tourney_name(event, transform=f"translate({logo[0] + (BLEED_WIDTH * CELL_WIDTH)}, {BLEED_HEIGHT * CELL_HEIGHT})")
    infobox = draw_tourney_infobox(event, transform=f"translate({BLEED_WIDTH * CELL_WIDTH}, {namebox[1] + (BLEED_HEIGHT * CELL_HEIGHT)})")
    disclaimerbox = draw_disclaimer(event, transform=f"translate({BLEED_WIDTH * CELL_WIDTH}, {namebox[1] + infobox[1] + DISCLAIMER_GAP * CELL_HEIGHT + (BLEED_HEIGHT * CELL_HEIGHT)})")
    timedesc = draw_time_desc(event, transform=f"translate({BLEED_WIDTH * CELL_WIDTH}, {logo[1] + (DISCLAIMER_GAP + TIME_EXPLANATION_GAP) * CELL_HEIGHT + infobox[1] + disclaimerbox[1] + (BLEED_HEIGHT * CELL_HEIGHT)})")
    width = infobox[0] + (BLEED_WIDTH * 2 * CELL_WIDTH)
    height = (DISCLAIMER_GAP + TIME_EXPLANATION_GAP) * CELL_HEIGHT + infobox[1] + disclaimerbox[1] + timedesc[1] + logo[1] + (2*BLEED_HEIGHT *CELL_HEIGHT) 

    canvas = draw.Drawing(width, height)
    canvas.append(draw.Rectangle(0,0,width, height, fill="grey"))
    canvas.append(logo[2])
    canvas.append(namebox[2])
    canvas.append(infobox[2])
    canvas.append(disclaimerbox[2])
    canvas.append(timedesc[2])

    canvas.save_svg(event['event']['name'] + "TBox.svg")







