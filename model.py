#!/bin/python

import struct
import sys
from PIL import Image

class Model:
  def __init__(self):
    return

  @classmethod
  def open(cls, filepath, palettepath):
    def read_I(f):
      s = f.read(struct.calcsize("I"))
      if len(s) == struct.calcsize("I"):
        return struct.unpack("I", s)[0]
      else:
        return None
    def read_f(f):
      return struct.unpack("f", f.read(struct.calcsize("f")))[0]

    m = cls()

    pf = open(palettepath)
    m.pal = pf.read()
    pf.close()

    f = open(filepath)
    m.ident = f.read(4)
    m.version = read_I(f)
    m.scale = [read_f(f), read_f(f), read_f(f)]
    m.translate = [read_f(f), read_f(f), read_f(f)]
    m.boundingradius = read_f(f)
    m.eyeposition = [read_f(f), read_f(f), read_f(f)]
    m.num_skins = read_I(f)
    m.skinwidth = read_I(f)
    m.skinheight = read_I(f)
    m.num_verts = read_I(f)
    m.num_tris = read_I(f)
    m.num_frames = read_I(f)
    m.synctype = read_I(f)
    m.flags = read_I(f)
    m.size = read_f(f)

    m.skin = {
      'animated': read_I(f) # like a bool
    }
    if (m.skin['animated'] == 0):
      m.skin['data'] = f.read(m.skinwidth * m.skinheight)
    else:
      raise Exception("multiskins NYI")

    f.close()
    return m

if __name__ == "__main__":
  print 'reading %s' % (sys.argv[1],)
  m = Model.open(sys.argv[1], sys.argv[2])
  i = Image.fromstring("P", (m.skinwidth, m.skinheight), m.skin['data'],
        'raw', 'P', 0, 1)
  i.putpalette(m.pal)
  i.save('skin.png', 'png')
  # print vars(m)