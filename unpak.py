#!/bin/python

import sys
import struct
import os

def ensure_dir(f):
  d = os.path.dirname(f)
  if not os.path.exists(d):
    os.makedirs(d)

def unpak(pak_filename):
  pakfile = open(pak_filename)
  if pakfile.read(4) != "PACK":
    raise Exception("Not a PAK")
  dir_offset = struct.unpack("I", pakfile.read(4))[0]
  dir_length = struct.unpack("I", pakfile.read(4))[0]
  pakfile.seek(dir_offset, 0)

  files = []

  while pakfile.tell() < dir_offset + dir_length:
    filepath = pakfile.read(56).split('\x00', 2)[0]
    if filepath == "":
      break
    file_offset = struct.unpack("I", pakfile.read(4))[0]
    file_length = struct.unpack("I", pakfile.read(4))[0]
    files.append({
      'path': filepath,
      'offset': file_offset,
      'length': file_length
      })

  outdir = pak_filename.rsplit('.', 1)[0]
  os.system("mkdir -p %s" % (outdir,))

  for f in files:
    print 'Extracting %s...' % (f['path'],)
    pakfile.seek(f['offset'], 0)
    outfile_contents = pakfile.read(f['length'])
    outpath = os.path.join(outdir, f['path'])
    ensure_dir(outpath)
    outfile = open(outpath, 'w')
    outfile.write(outfile_contents)
    outfile.close()

if __name__ == "__main__":
  print 'unpacking %s' % (sys.argv[1],)
  unpak(sys.argv[1])