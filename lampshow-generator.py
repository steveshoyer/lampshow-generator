# Steve Shoyer
# 2018-12-12
# MET CS 521 Class project- Pinball light show generator

# This program generates light show (.lampshow) files  The format of these files
# is documented at http://pyprocgame.pindev.org/ref/lamps.html?highlight=lampshow#lampshow

# Light show files are used by a pinball programming framework called PyProcGameHD/SkeletonGame,
# which is documented at http://skeletongame.com/  The hardware platform is called P-ROC,
# produced by Multimorphic, Inc (https://www.multimorphic.com/store/circuit-boards/p-roc/).

CYCLES_PER_SECOND = 32  # There are 32 lamp show cycles per second

CONFIG_FILENAME = "WCS.yaml"

import yaml

class LampGroup:
    """ Lamp Group object: used to hold a list of grouped lamps, their orientation
    (horizontal or vertical) and an index into the list for sequencing """
    
    def __init__(self, name):
        self.lamp_index = 0  # start the index at the first lamp
        self.lamp_list = list()
        self.group_name = name
        self.orientation = 'TBD'  # the group's oroientation isn't set yet
        self.direction = 'Forward'
        
    def __str__(self):  # Human-readable representation of Lamp
        return(self.group_name + ', lamp index=' + str(self.lamp_index) + '  ' + str(self.lamp_list))
        
    def add(self, lamp, xpos, ypos):
        """ add a lamp to the list along with its x,y position """
        self.lamp_list.append((lamp, xpos, ypos))
        return()
        
    def set_orientation(self):
        """ determine if this group is horizontal or vertical """
        min_height = min(int(lamp[2]) for lamp in self.lamp_list)
        max_height = max(int(lamp[2]) for lamp in self.lamp_list)
        min_width = min(int(lamp[1]) for lamp in self.lamp_list)
        max_width = max(int(lamp[1]) for lamp in self.lamp_list)
        group_height = max_height - min_height
        group_width = max_width - min_width
        if group_height > group_width:
            self.orientation = 'Vertical'
        else:
            self.orientation = 'Horizontal'
    
    def sort_group(self):
        """ sort the list of lamps for this group """
        if self.orientation == 'Horizontal':
            self.lamp_list.sort(key=lambda x: x[1])
        else:
            self.lamp_list.sort(key=lambda x: x[2])

    def next_lamp(self):
        """ return the next lamp in the sequence, increment/decrement the index """
        next_lamp_name = self.lamp_list[self.lamp_index][0] # return the next lamp name
        if self.orientation == 'Vertical':
            self.lamp_index += 1
            if len(self.lamp_list) == self.lamp_index:
                self.lamp_index = 0
        elif self.direction == 'Forward':  # horizontal, moving right
            if (len(self.lamp_list) - 1) == self.lamp_index:
                self.direction = 'Reverse'
            else:
                self.lamp_index += 1
        else:  # horizontal, moving left
            if self.lamp_index ==  0:
                self.direction = 'Forward'
            else:
                self.lamp_index -= 1
        return(next_lamp_name)    

    def getGroupName(self):
        return self.group_name


def group_search(lamp_group_list, group_name):
    """ return index of a group name in a list of group objects """
    """ return None if the group name is not found """
    index = 0
    while lamp_group_list[index].getGroupName() != group_name:
        index += 1
        if index == len(lamp_group_list):
            return(None)
    return(index)
    
 
def header_string(key_length=0, number_of_seconds=2):
    """ return a header string for the output file """    
    header_string = '#'
    header_string += ' ' * (key_length+8)
    header_string += '         1         2         3  ' * number_of_seconds + '\n'
    header_string += '#'
    header_string += ' ' * (key_length+8)
    header_string += '1234567890123456789012345678901-' * number_of_seconds + '\n'
    return(header_string)
    

def print_lightshow(lamp_dictionary, filename='attract.lampshow', number_of_seconds=2):
    """ Print out a lamp show file of duration "number_of_seconds" """
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND
    # determine the size of the lamp names and set up a pattern for formatting
    max_key_length = max([len(k) for k in lamp_dictionary.keys()])
    format_pattern = '<'+str(max_key_length+7)+'s'
    
    try:
        outfile = open(filename, 'w')  # open the output file for writing
    
        outfile.write(header_string(max_key_length, number_of_seconds))
        for lamp in lamp_dictionary:
            # set up the lamp name as the row header
            output_str = format('lamp:' + lamp, format_pattern) + '| '
            cycle_list = [' '] * (number_of_cycles)  # create a list of spaces for each cycle
            # next, turn the lamp on for any cycles in the list
            if (len(lamp_dictionary[lamp]['step map']) > 0):  # make sure this lamp is on at least once
                while (len(lamp_dictionary[lamp]['step map']) > 0):
                    this_cycle = lamp_dictionary[lamp]['step map'].pop()
                    cycle_list[this_cycle] = '.'
            # finally, convert the list into a string and write it to the file
            output_str += "".join(cycle_list)
            outfile.write(output_str + '\n')
        outfile.close()
    except:
        print("An error occurred writing to the file " + filename)
    return()


def create_lightshow_wipe_right(lamp_dictionary, filename='attract.lampshow', number_of_seconds=2):
# create a light show that wipes horizontally left to right
# starting from the left, all lamps turn on in half the time, then they turn off
# in half the time
    
    # determine the number of cycles
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND
    first_pass_cycles = (number_of_cycles // 2) + 1
    
    # the minimum and maximum lamp X position (i.e., determine playfield width) 
    min_width = min(int(l['xpos']) for l in lamp_dictionary.values())
    max_width = max(int(l['xpos']) for l in lamp_dictionary.values())
    window_width = max_width - min_width
    window_jump_per_cycle = window_width // first_pass_cycles
    
    # check each lamp to see if it should be on
    for lamp in lamp_dictionary.keys():
        x_pos = lamp_dictionary[lamp]['xpos']
        lamp_dictionary[lamp]['step map'] = list()
        window_edge = min_width - window_width  # start at the left side
     
        for i in range(0, number_of_cycles):
            if (x_pos >= window_edge) and (x_pos <= (window_edge + window_width)):
                lamp_dictionary[lamp]['step map'].append(i)  # add this cycle to the lamp's step map list
            else:
                pass
            window_edge += window_jump_per_cycle  # move the window to the right

    print_lightshow(lamp_dictionary, filename, number_of_seconds)
    return()


def create_lightshow_wipe_left(lamp_dictionary, filename='attract.lampshow', number_of_seconds=2):
# create a light show that wipes horizontally right to left
# starting from the left, all lamps turn on in half the time, then they turn off
# in half the time
    
    # determine the number of cycles
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND
    first_pass_cycles = (number_of_cycles // 2) + 1
    
    # the minimum and maximum lamp X position (i.e., determine playfield width) 
    min_width = min(int(l['xpos']) for l in lamp_dictionary.values())
    max_width = max(int(l['xpos']) for l in lamp_dictionary.values())
    window_width = max_width - min_width
    window_jump_per_cycle = window_width // first_pass_cycles
    
    # check each lamp to see if it should be on
    for lamp in lamp_dictionary.keys():
        x_pos = lamp_dictionary[lamp]['xpos']
        lamp_dictionary[lamp]['step map'] = list()  # clear out this lamp's step map
        window_edge = max_width  # start at the right side
     
        for i in range(0, number_of_cycles):
            if (x_pos >= window_edge) and (x_pos <= (window_edge + window_width)):
                lamp_dictionary[lamp]['step map'].append(i)  # add this cycle to the lamp's step map list
            else:
                pass
            window_edge -= window_jump_per_cycle  # move the window to the left

    print_lightshow(lamp_dictionary, filename, number_of_seconds)
    return()


def create_lightshow_wipe_up(lamp_dictionary, filename='attract.lampshow', number_of_seconds=2):
# create a light show that wipes vertically from bottom to top
# starting from the bottom, all lamps turn on in half the time, then they turn off
# in half the time
    
    # determine the number of cycles
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND
    first_pass_cycles = (number_of_cycles // 2) + 1
    
    # the minimum and maximum lamp Y position (i.e., determine playfield height) 
    min_height = min(int(l['ypos']) for l in lamp_dictionary.values())
    max_height = max(int(l['ypos']) for l in lamp_dictionary.values())
    window_height = max_height - min_height
    window_jump_per_cycle = window_height // first_pass_cycles
    
    # check each lamp to see if it should be on
    for lamp in lamp_dictionary.keys():
        y_pos = lamp_dictionary[lamp]['ypos']
        lamp_dictionary[lamp]['step map'] = list()  # clear out this lamp's step map
        window_edge = min_height - window_height  # start at the right side
     
        for i in range(0, number_of_cycles):
            if (y_pos >= window_edge) and (y_pos <= (window_edge + window_height)):
                lamp_dictionary[lamp]['step map'].append(i)  # add this cycle to the lamp's step map list
            else:
                pass
            window_edge += window_jump_per_cycle  # move the window up

    print_lightshow(lamp_dictionary, filename, number_of_seconds)
    return()


def create_lightshow_wipe_down(lamp_dictionary, filename='attract.lampshow', number_of_seconds=2):
# create a light show that wipes vertically from top to bottom
# starting from the bottom, all lamps turn on in half the time, then they turn off
# in half the time
    
    # determine the number of cycles
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND
    first_pass_cycles = (number_of_cycles // 2) + 1
    
    # the minimum and maximum lamp Y position (i.e., determine playfield height) 
    min_height = min(int(l['ypos']) for l in lamp_dictionary.values())
    max_height = max(int(l['ypos']) for l in lamp_dictionary.values())
    window_height = max_height - min_height
    window_jump_per_cycle = window_height // first_pass_cycles
    
    # check each lamp to see if it should be on
    for lamp in lamp_dictionary.keys():
        y_pos = lamp_dictionary[lamp]['ypos']
        lamp_dictionary[lamp]['step map'] = list()  # clear out this lamp's step map
        window_edge = max_height  # start at the top
     
        for i in range(0, number_of_cycles):
            if (y_pos >= window_edge) and (y_pos <= (window_edge + window_height)):
                lamp_dictionary[lamp]['step map'].append(i)  # add this cycle to the lamp's step map list
            else:
                pass
            window_edge -= window_jump_per_cycle  # move the window down

    print_lightshow(lamp_dictionary, filename, number_of_seconds)
    return()


def create_lightshow_circle_out(lamp_dictionary, filename='attract.lampshow', number_of_seconds=2, center=(-1,-1)):
# create a light show that radiates outward from a center point.   If no center is given,
# the center of the playfield is used.  All lamps turn on in half the time, then they turn off
# in half the time
    
    # determine the number of cycles
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND
    first_pass_cycles = (number_of_cycles // 2) + 1
    
    # figure out the size of the space 
    min_height = min(int(l['ypos']) for l in lamp_dictionary.values())
    max_height = max(int(l['ypos']) for l in lamp_dictionary.values())
    min_width = min(int(l['xpos']) for l in lamp_dictionary.values())
    max_width = max(int(l['xpos']) for l in lamp_dictionary.values())
    window_height = max_height - min_height
    window_width = max_width - min_width
    window_jump_per_cycle = max(window_height, window_width) // first_pass_cycles
    if center == (-1,-1): # default, so find the center of the lamps
        center = (((window_width // 2)  +  min_width),((window_height // 2) + min_height)) 
    
    # clear out the step maps
    for lamp in lamp_dictionary.keys():
        lamp_dictionary[lamp]['step map'] = list()  # clear out this lamp's step map

    # start in the center of the circle and move outwards
    circle_radius = window_jump_per_cycle
    x_center = center[0]  # pick up the x and y of the circle's center
    y_center = center[1]
    
    for i in range(0, first_pass_cycles):
        radius_sq = pow(circle_radius, 2)  # save this for later comparison

        # check each lamp to see if it should be on
        for lamp in lamp_dictionary.keys():
            x_pos = lamp_dictionary[lamp]['xpos']
            y_pos = lamp_dictionary[lamp]['ypos']
            # use the Pythagorean theorem to see if the point is inside the circle
            if (pow((x_pos - x_center),2) + pow((y_pos - y_center),2)) <= radius_sq:
                lamp_dictionary[lamp]['step map'].append(i)  # add this cycle to the lamp's step map list
            else:
                pass
            
        circle_radius += window_jump_per_cycle
        
    # now that the lights are on, repeat with the inverse to turn them off
    # start in the center of the circle and move outwards
    circle_radius = window_jump_per_cycle
    
    for i in range(first_pass_cycles, number_of_cycles):
        radius_sq = pow(circle_radius, 2)  # save this for later comparison
        # check each lamp to see if it should be on
        for lamp in lamp_dictionary.keys():
            x_pos = lamp_dictionary[lamp]['xpos']
            y_pos = lamp_dictionary[lamp]['ypos']
            # use the Pythagorean theorem to see if the point is inside the circle
            if (pow((x_pos - x_center),2) + pow((y_pos - y_center),2)) <= radius_sq:
                pass
            else:
                lamp_dictionary[lamp]['step map'].append(i)  # add this cycle to the lamp's step map list
            
        circle_radius += window_jump_per_cycle

    print_lightshow(lamp_dictionary, filename, number_of_seconds)
    return()


def create_lightshow_circle_out_in(lamp_dictionary, filename='attract.lampshow', number_of_seconds=2, center=(-1,-1)):
# create a light show that radiates outward from a center point and then comes back in.   If no center is given,
# the center of the playfield is used.  All lamps turn on in half the time, then they turn off
# in half the time
    
    # determine the number of cycles
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND
    first_pass_cycles = (number_of_cycles // 2) + 1
    
    # figure out the size of the space 
    min_height = min(int(l['ypos']) for l in lamp_dictionary.values())
    max_height = max(int(l['ypos']) for l in lamp_dictionary.values())
    min_width = min(int(l['xpos']) for l in lamp_dictionary.values())
    max_width = max(int(l['xpos']) for l in lamp_dictionary.values())
    window_height = max_height - min_height
    window_width = max_width - min_width
    window_jump_per_cycle = max(window_height, window_width) // first_pass_cycles
    if center == (-1,-1): # default, so find the center of the lamps
        center = (((window_width // 2)  +  min_width),((window_height // 2) + min_height)) 
    
    # clear out the step maps
    for lamp in lamp_dictionary.keys():
        lamp_dictionary[lamp]['step map'] = list()  # clear out this lamp's step map

    # start in the center of the circle and move outwards
    circle_radius = window_jump_per_cycle
    x_center = center[0]  # pick up the x and y of the circle's center
    y_center = center[1]
    
    for i in range(0, first_pass_cycles):
        radius_sq = pow(circle_radius, 2)  # save this for later comparison

        # check each lamp to see if it should be on
        for lamp in lamp_dictionary.keys():
            x_pos = lamp_dictionary[lamp]['xpos']
            y_pos = lamp_dictionary[lamp]['ypos']
            # use the Pythagorean theorem to see if the point is inside the circle
            if (pow((x_pos - x_center),2) + pow((y_pos - y_center),2)) <= radius_sq:
                lamp_dictionary[lamp]['step map'].append(i)  # add this cycle to the lamp's step map list
                lamp_dictionary[lamp]['step map'].append(number_of_cycles - i - 1)  # add the reflective cycle to the lamp's step map list too
            else:
                pass
            
        circle_radius += window_jump_per_cycle
        
    print_lightshow(lamp_dictionary, filename, number_of_seconds)
    return()


def create_lightshow_flash_groups(lamp_dictionary, filename='attract.lampshow', number_of_seconds=2):
# create a light show that flashes all lamps in a group, from left to right
    
    # determine the number of cycles
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND

    # clear out the step maps
    for lamp in lamp_dictionary.keys():
        lamp_dictionary[lamp]['step map'] = list()  # clear out this lamp's step map

    # get a set of groups (they need to be unique values)
    group_set = set()
    for lamp in lamp_dictionary:
        if 'group' in lamp_dictionary[lamp].keys():
            group_set.add(lamp_dictionary[lamp]['group'])

    # figure out how many groups there are and how long each one should be flashing
    number_of_groups = len(group_set)
    cycles_per_group = number_of_cycles // number_of_groups
    
    # look at each lamp and find the minimum x value, to sort the groups left to right
    group_dict = dict.fromkeys(group_set)  # set up a dictionary for the groups
    for lamp in lamp_dictionary:
        if 'group' in lamp_dictionary[lamp].keys():
            if group_dict[lamp_dictionary[lamp]['group']] == None:
                group_dict[lamp_dictionary[lamp]['group']] = lamp_dictionary[lamp]['xpos']
            elif lamp_dictionary[lamp]['xpos'] < group_dict[lamp_dictionary[lamp]['group']]:
                group_dict[lamp_dictionary[lamp]['group']] = lamp_dictionary[lamp]['xpos']
    group_list = sorted(group_dict, key=group_dict.__getitem__)
    # start going through the groups and adding cycles to each lamp in the group
    group_start_cycle = 0
    for group_to_flash in group_list:
        group_lamp_list = [lamp for lamp in lamp_dictionary if ('group' in lamp_dictionary[lamp].keys() and lamp_dictionary[lamp]['group'] == group_to_flash)]
        for lamp in group_lamp_list:
            for cycle in range(group_start_cycle, group_start_cycle + cycles_per_group):
                lamp_dictionary[lamp]['step map'].append(cycle)
        group_start_cycle += cycles_per_group

    print_lightshow(lamp_dictionary, filename, number_of_seconds)
    return()

def create_lightshow_sequence_groups(lamp_dictionary, filename='attract.lampshow', number_of_seconds=4):
    """ create a light show that sequences lamps from each group """
    
    CYCLE_SPAN = 3  # number of contiguous time cycles for each lamp to be on 
    
    # determine the number of cycles
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND

    # clear out the step maps
    for lamp in lamp_dictionary.keys():
        lamp_dictionary[lamp]['step map'] = list()  # clear out this lamp's step map

    # get a set of groups (they need to be unique values)
    group_set = set()
    for lamp in lamp_dictionary:
        if 'group' in lamp_dictionary[lamp].keys():
            group_set.add(lamp_dictionary[lamp]['group'])

    # set up the list of lamp group objects
    lamp_group_list = []
    for lamp_group in group_set:
        lamp_group_list.append(LampGroup(lamp_group))

    # go through the lamps and add them to the LampGroup objects
    for lamp in lamp_dictionary:
        if 'group' in lamp_dictionary[lamp].keys():
            group_index = group_search(lamp_group_list, lamp_dictionary[lamp]['group'])
            if group_index != None:
                lamp_group_list[group_index].add(lamp, lamp_dictionary[lamp]['xpos'], lamp_dictionary[lamp]['ypos'])
    
    # look at all of the LampGroup objects, determine their orientation, then sort them
    for lamp_group in lamp_group_list:
        lamp_group.set_orientation()
        lamp_group.sort_group()
        
    # finally, go through the groups and adding cycles to the next lamp in each group
    for cycle in range(0,number_of_cycles,2):
        for lamp_group in lamp_group_list:
            this_lamp = lamp_group.next_lamp()
            for bump in range(CYCLE_SPAN):
                if (cycle+bump) < number_of_cycles:
                    lamp_dictionary[this_lamp]['step map'].append(cycle+bump)

    print_lightshow(lamp_dictionary, filename, number_of_seconds)
    return()


def create_lightshow_random(lamp_dictionary, filename='attract.lampshow', concurrent_lamps=5, number_of_seconds=2):
# create a light show that randomly flashes lamps
    import random
    
    # determine the number of cycles
    number_of_cycles = number_of_seconds * CYCLES_PER_SECOND
    
    # clear out the step maps and set up the list of lamps
    for lamp in lamp_dictionary.keys():
        lamp_dictionary[lamp]['step map'] = list()  # clear out this lamp's step map
    lamp_names = list(lamp_dictionary.keys())

    for i in range(0, number_of_cycles):
        random.shuffle(lamp_names)  # randomly shuffle the lamps for this cycle
        lamps_this_cycle = tuple(lamp_names[:concurrent_lamps]) # save the lamp names for this cycle in a tuple 
        for this_lamp in lamps_this_cycle:
            lamp_dictionary[this_lamp]['step map'].append(i)  # add this cycle to the lamp's step map list

    print_lightshow(lamp_dictionary, filename, number_of_seconds)
    return()


if __name__ == "__main__":

    filename = CONFIG_FILENAME  # configuration file
    try:    
        with open(filename, 'r') as stream:  # load the playfield description file
            data_loaded = yaml.load(stream)
            
        # create a dictionary of the lamps that have coordinates given in the config file
        lamp_dict = {lamp : data_loaded['PRLamps'][lamp] for lamp in data_loaded['PRLamps'] if 'xpos' in data_loaded['PRLamps'][lamp] }
        
        create_lightshow_wipe_right(lamp_dict, 'right.lampshow')
        create_lightshow_wipe_left(lamp_dict, 'left.lampshow')
        create_lightshow_wipe_up(lamp_dict, 'up.lampshow')
        create_lightshow_wipe_down(lamp_dict, 'down.lampshow')
        create_lightshow_circle_out(lamp_dict, 'circle_out.lampshow')
        create_lightshow_circle_out_in(lamp_dict, 'circle_out_in_LA.lampshow', 2, (130,572))
        create_lightshow_flash_groups(lamp_dict, 'flash_groups.lampshow', 2)
        create_lightshow_sequence_groups(lamp_dict, 'sequence_groups.lampshow', 5)
        create_lightshow_random(lamp_dict, 'random.lampshow', 5, 2)

    except FileNotFoundError as err:
        print("The configuration file " + filename + " was not found.")
    else:
        print("The light show files have been created.")
