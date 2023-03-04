from Constants import *
import drawsvg as draw


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
    zone_name = draw_zone_name_box(zone_name)

    