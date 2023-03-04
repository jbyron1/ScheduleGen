from Constants import *
import drawsvg as draw
from datetime import datetime, timedelta

class Image(draw.DrawingBasicElement):
    TAG_NAME = 'image'
    def __init__(self, x, y, width, height, href, preserveAspectRatio, target=None, **kwargs):
        super().__init__(x=x, y=y, width=width, href=href, preserveAspectRatio=preserveAspectRatio, target=target, **kwargs)


def draw_day_box(day, transform=f"translate({0}, {0})"):
    stream_day = draw.Group(transform=transform)
    obj_height = STREAM_DAY_BOX_HEIGHT * CELL_HEIGHT
    obj_width =  STREAM_DAY_BOX_WIDTH * CELL_WIDTH
    stream_day.append(draw.Rectangle(0, 0, obj_width, obj_height, stroke = "black", stroke_width = 0, fill = 'yellow'))
    stream_day.append(draw.Text(day , 18, obj_width/2, obj_height/2, center=True, fill="black", font_weight="bold", font_family="Arial"))
    return obj_width, obj_height, stream_day

def draw_zone_name_box(zone_name,  transform=f"translate({0}, {0})"):
    stream_zone_name = draw.Group(transform=transform)
    obj_height = STREAM_ZONE_NAME_HEIGHT * CELL_HEIGHT
    obj_width = STREAM_ZONE_NAME_WIDTH * CELL_WIDTH
    stream_zone_name.append(draw.Rectangle(0,0,obj_width, obj_height, stroke = "black", stroke_width = 0, fill = 'yellow'))
    stream_zone_name.append(draw.Text(zone_name, 12, obj_width/2, obj_height/2, center=True, fill="black", font_weight="bold", font_family="Arial"))
    return obj_width, obj_height, stream_zone_name

def draw_dayzone_box(day, zone_name, transform=f"translate({0}, {0})"):
    dayzone = draw.Group(transform=transform)
    
    stream_day = draw_day_box(day)
    zone_name = draw_zone_name_box(zone_name,transform=f"translate({0}, {stream_day[1]})")
    
    obj_width = stream_day[0]
    obj_height = stream_day[1] + zone_name[1]

    bg = draw.Rectangle(0,0, obj_width, obj_height, stroke = 'black', stroke_width = '0')
    border = draw.Rectangle(.5,.5, obj_width - 1, obj_height -1, stroke = 'black', stroke_width = 1, fill="none")
    dayzone.append(bg)
    
    dayzone.append(stream_day[2])
    dayzone.append(zone_name[2])
    dayzone.append(border)
    return obj_width, obj_height, dayzone

def draw_offset_box(offset,  transform=f"translate({0}, {0})"):
    offset_box = draw.Group(transform=transform)

    obj_height = STREAM_TIME_ZONE_BOX_HEIGHT * CELL_HEIGHT
    obj_width = STREAM_TIME_ZONE_BOX_WIDTH * CELL_WIDTH
    
    offset_box.append(draw.Rectangle(0,0, obj_width, obj_height, stroke = "black", stroke_width = 0, fill = 'yellow'))
    offset_box.append(draw.Rectangle(.5,.5, obj_width - 1, obj_height -1, stroke = 'black', stroke_width = 1, fill="none"))
    offset_box.append(draw.Text("UTC" + str(offset), 14, obj_width/2, obj_height/2, center=True, fill="black", font_weight="bold", font_family="Arial"))
    return obj_width, obj_height, offset_box

def draw_dtz_box(day, zone_name, offset,transform=f"translate({0}, {0})"):
    dtz = draw.Group(transform=transform)
    dayzone = draw_dayzone_box(day['day'], zone_name)
    offset_box = draw_offset_box(offset, transform=f"translate({dayzone[0] - .5}, {0})")
    dtz.append(dayzone[2])
    dtz.append(offset_box[2])
    obj_width = dayzone[0] + offset_box[0]
    obj_height = dayzone[1]
    return obj_width, obj_height, dtz

def draw_blank_time_cell(num_cells, transform=f"translate({0}, {0})"):
    obj_width = STREAM_15_MINUTE_WIDTH * CELL_WIDTH * num_cells
    obj_height = STREAM_TIME_ZONE_BOX_HEIGHT * CELL_HEIGHT
    blank_cell = draw.Rectangle(0,0, obj_width, obj_height, fill ="black",  transform=transform)
    return obj_width, obj_height, blank_cell

def draw_pop_time_cell(time, transform=f"translate({0}, {0})"):
    obj_width = 2 * STREAM_15_MINUTE_WIDTH * CELL_WIDTH
    obj_height = STREAM_TIME_ZONE_BOX_HEIGHT * CELL_HEIGHT
    filled_cell = draw.Group(transform=transform)
    text = draw.Text(time, 16,  obj_width/10, obj_height - (obj_height/3), center=False, fill= "white", font_weight="bold", font_family="Arial")
    block = draw.Rectangle(0,0, obj_width, obj_height, fill ="black")
    filled_cell.append(block)
    filled_cell.append(text)
    return obj_width, obj_height, filled_cell

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

    
def draw_time_cells(time_format, cell_count, block_list,  transform=f"translate({0}, {0})"):
    times = draw.Group(transform=transform)
    cell = draw_blank_time_cell(cell_count)
    obj_width = cell[0]
    obj_height = cell[1]
    times.append(cell[2])
    start_time = block_list[0]
    for block in block_list:    
        diff = (block - start_time)
        diff_s = diff.total_seconds()
        time_blocks = int(divmod(diff_s, 900)[0])
        print(time_blocks)
        time_str = time_convert(time_format, block)
        time_block = draw_pop_time_cell(time_str, transform=f"translate({time_blocks * CELL_WIDTH * STREAM_15_MINUTE_WIDTH}, {0})")
        times.append(time_block[2])
        

   
    return obj_width, obj_height, times

def draw_top_row(time_format, cell_count, block_list, day, zone_name, offset, transform = f"translate({0}, {0})"):
    dtz = draw_dtz_box(day, zone_name, offset)
    time_bar = draw_time_cells(time_format, cell_count, block_list, transform=f"translate({dtz[0] -.5}, {0})")

    top_bar = draw.Group(transform= transform)
    top_bar.append(dtz[2])
    top_bar.append(time_bar[2])

    obj_width = dtz[0] + time_bar[0]
    obj_height = time_bar[1]

    return obj_width, obj_height, top_bar

def draw_stream_logo(file_location, transform=f"translate({0}, {0})"):
    obj_width = STREAM_LOGO_BOX_WIDTH * CELL_WIDTH
    obj_height = STREAM_LOGO_BOX_HEIGHT * CELL_HEIGHT

    logobox = draw.Group(transform = transform)
    bg = draw.Rectangle(0,0, obj_width, obj_height, fill="white", stroke = 'black', stroke_width = '0')
    border = draw.Rectangle(.5,.5, obj_width - 1, obj_height -1, stroke = 'black', stroke_width = 1, fill="none")
    image = Image(obj_width/4, 3*obj_height/16, obj_width/2, obj_height/2, file_location, True)
    logobox.append(bg)
    logobox.append(image)
    logobox.append(border)

    return obj_width, obj_height, logobox

def draw_stream_link(platform, streamer, transform=f"translate({0}, {0})"):
    obj_width = STREAM_LINK_BOX_WIDTH * CELL_WIDTH
    obj_height = STREAM_LINK_BOX_HEIGHT * CELL_HEIGHT

    linkbox = draw.Group(transform = transform)
    bg = draw.Rectangle(0,0, obj_width, obj_height, fill="pink", stroke = 'black', stroke_width = '0')
    border = draw.Rectangle(.5,.5, obj_width - 1, obj_height -1, stroke = 'black', stroke_width = 1, fill="none")
    plat = draw.Text(platform, 10, obj_width/2, obj_height/4, center=True, font_weight="bold", font_family="Arial")
    link = draw.Text(streamer, 14, obj_width/2, 5*obj_height/8, center=True, font_weight="bold", font_family="Arial")

    linkbox.append(bg)
    linkbox.append(plat)
    linkbox.append(link)
    linkbox.append(border)

    return obj_width, obj_height, linkbox



