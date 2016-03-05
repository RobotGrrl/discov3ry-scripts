# *experimental* gcode post-processor v2 
# for use with the Discov3ry on an Ultimaker 2+ Go!
#
# adds in commands to the original gcode to reset 
# the extruded distance. then adjusts the extruded
# distance to be a certain percentage of the original;
# if it is after a threshold of total distance
# extruded.
#
# essentially toggling back and forth between actual
# flow rate, and a reduced flow rate.
#
# the idea is for there to not be as much pressure
# building up in the system. by setting a low number
# of steps/mm, it serves as a way to let the existing
# material flow out —  rather than adding to the 
# built up pressure by a constant application of 
# steps/mm
#
# this is experimental, make sure you check out the
# generated gcode and see that it will not hurt
# your printer. not responsible if there is an
# icing explosion caused by this code (or anything
# else bad). 
# 
# the parameters will depend on the material you
# use - it might take a few test prints to get it
# just right
#
# -------------------------------------------------
# written while on Quest a part of Studio Y at MaRS,
# during Maker in Residence at Structur3d!
#
# Weds. March 2, 2016
# Erin RobotGrrl
# erin@robotgrrl.com
# -------------------------------------------------

import os

f = open('test_rings4.gcode', 'r')
out = open('test_rings4_post.gcode', 'w')

ADJ_PERCENT = 0.2
ADJ_THRESH = 250.0

i = 0
begin_counting = False
the_end = False
copying_mode = True
adj_mode = False
extrude_mm_counter = 0.0
num_adjs = 0
cur_extr_amount = 0.0
last_extr_amount = 0.0


for line in f:

  #if i > 50: break
  i+=1

  # assumes start of design gcode is after a M117 cmd
  if line.startswith("M117"):
    if begin_counting == False:
      begin_counting = True
      print("so it begins at ", i)

  # assumes end of design gcode is after M104 cmd
  if line.startswith("M104"):
    print("so it ends at ", i)
    the_end = True

  if begin_counting == True and the_end == False:
    if line.startswith("G1"):
      #print("line ", i)
      copying_mode = False

      # finding the E in the G1 cmd
      n = 0
      for c in line:
        if c == 'E':
          start_ind = n
          break
        n+=1
      stop_ind = len(line) # this assumes E is the last parameter in the command (could be bad)
      s = line[start_ind+1:stop_ind]
      f = float(s)
      
      # adding extruded amount to counter

      last_extr_amount = cur_extr_amount
      cur_extr_amount = f
      extrude_mm_counter += (cur_extr_amount-last_extr_amount)
      #print("extrude amount for ", line, " is ", (cur_extr_amount-last_extr_amount))
      #print("extrude counter: ", extrude_mm_counter)


      # finding when to switch adjustments

      if extrude_mm_counter >= ADJ_THRESH:
        num_adjs += 1
        extrude_mm_counter = 0.0
        
        if num_adjs%2 == 0:
          out.write("; adjustment ON\n")
          adj_mode = True
        else:
          out.write("; adjustment OFF\n")
          adj_mode = False
          
      out.write("G92 E0\n")
      new_cmd = line[0:start_ind]


      # writing the new cmd based on adjustment mode

      if adj_mode == True:
        num = ADJ_PERCENT*(cur_extr_amount-last_extr_amount)
        new_cmd += str(" E%f\n" %  num)
        print("*ADJ* new cmd: ", new_cmd)
      else:
        new_cmd += str(" E%f\n" % (cur_extr_amount-last_extr_amount) )
        print("new cmd: ", new_cmd)
        
      out.write(new_cmd)

    else: # for any line that is not G1
      copying_mode = True


  # copy everything else

  if copying_mode == True:
    out.write(line)
  #else:
    #print("not printing ", line)

      
print("number of adjustments: ", num_adjs)
out.close()
