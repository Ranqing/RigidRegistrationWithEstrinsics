import sys
import glob
import os

frm_dir = './frm_0054_downsample'
files = glob.glob(frm_dir + '/*.ply')

out_file_object = open('rename.sh', 'w')
for f in files:
	filename = os.path.basename(f)
	new_filename = filename[4:]
	command = 'mv ' + filename + ' ' + new_filename + '\n'
	out_file_object.write(command)

