# lampshow-generator
Python code to generate .lampshow files for pinball machines based on P-ROC and pyprocgame/skeletongame

I was taking a Python class and needed a project, so I created this program to generate lampshow files.  The files use the .lampshow
format as described in http://pyprocgame.pindev.org/ref/lamps.html

Input files follow the machine description YAML files described in http://pyprocgame.pindev.org/manual.html?highlight=yaml#machine-config with
some additional attributes for each lamp - xpos, ypos, and group.  The xpos and ypos values (integers) are the x-position and y-position of each lamp, and
group is an optional attribute that groups lamps together in logical groups.  I measured x and y in millimeters from the lower left corner
of the playfield, but any consistent way to measure should work.

To use the program, put your modified yaml file in the same directory as the program and edit the program to include the name of the yaml
file - I used a WCS playfield for developing the program, so "WCS.yaml" is used for the CONFIG_FILENAME variable.

The program uses distinct subroutines to create each lampshow file.  These subroutines are called from the main section of the program.  The
user can (and should) edit the main section to create whichever files are desired, along with the names for the output files and any
optionsl parameters (such as the length in seconds of the lampshow).

A few notes on the program:

- There's not a lot of error checking in the code.  It is assumed that if the input file is found, it is created correctly.
- Some of the code is clunky and inefficient.  Some of the code, and the data structures used, are unwieldy and not smart.  The reason for
this is that this was a class project, and the project requirements specified that certain elements of the Python language needed to be used.
Making the program more efficient would have removed a number of the language elements, so there are some loops and structures that could be 
optimized and/or removed entirely.  The program runs quickly enough to create the lampshows, so it wasn't worth the effort to go back and
improve it once the class had ended.
