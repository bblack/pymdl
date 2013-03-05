#!/bin/python

import struct
import sys
from PIL import Image, ImageDraw

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
    def read_b(f):
      return struct.unpack("b", f.read(struct.calcsize("b")))[0]
    def read_vertex(f):
      return {
        0: read_b(f),
        1: read_b(f),
        2: read_b(f),
        'normal_index': read_b(f)
      }
    def read_frame(f, num_verts):
      frame = {
        'bboxmin': read_vertex(f),
        'bboxmax': read_vertex(f),
        'name': f.read(16).split('\x00', 1)[0],
        'verts': []
      }
      for j in range(0, num_verts):
        frame['verts'].append(read_vertex(f))
      return frame

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
    m.num_anims = read_I(f)
    m.synctype = read_I(f)
    m.flags = read_I(f)
    m.size = read_f(f)

    m.skin = { 'animated': read_I(f) } # like a bool
    if (m.skin['animated'] == 0):
      m.skin['data'] = f.read(m.skinwidth * m.skinheight)
    else:
      raise Exception("multiskins NYI")

    m.tex_coords = []
    for i in range(0, m.num_verts):
      # coords are on a plane of skinwidth * skinheight. 0,0 is top left (?)
      tex_coord = {
        'onseam': read_I(f), # like a bool
        's': read_I(f),
        't': read_I(f)
      }
      m.tex_coords.append(tex_coord)

    m.tris = []
    for i in range(0, m.num_tris):
      tri = {
        'facesfront': read_I(f), # like bool
        'vert_indices': [read_I(f), read_I(f), read_I(f)] # todo: point to actual verts?
      }
      m.tris.append(tri)

    print hex(f.tell())
    m.animations = []
    for i in range(0, m.num_anims):
      print "on anim %i" % i
      animation = {
        'type': read_I(f)
      }
      if animation['type'] == 0:
        # Simple (one-frame) animation
        animation['frame'] = read_frame(f, m.num_verts)
      else:
        # Multi-frame (1 or more frames) animation
        raise Exception("encountered anim_type = %i" % animation['type'])
        animation['bboxmin'] = read_vertex(f)
        animation['bboxmax'] = read_vertex(f)
        animation['frame_times'] = []
        animation['frames'] = []
        for j in range(0, animation['type']):
          animation['frame_times'].append(read_f(f))
        for j in range(0, animation['type']):
          animation['frames'].append(read_frame(f, m.num_verts))
    print "Bytes left: %s" % len(f.read())

    f.close()
    return m

if __name__ == "__main__":
  print 'reading %s' % (sys.argv[1],)
  m = Model.open(sys.argv[1], sys.argv[2])
  img = Image.fromstring("P", (m.skinwidth, m.skinheight), m.skin['data'],
        'raw', 'P', 0, 1)
  img.putpalette(m.pal)
  draw = ImageDraw.Draw(img)

  for tri in m.tris:
    e_sts = [] # effective st's (backface offsets added)
    for i in range(0, 3):
      st = m.tex_coords[tri['vert_indices'][i]]
      e_st = {'s': st['s'], 't': st['t']}
      if not tri['facesfront'] and st['onseam']:
        e_st['s'] += m.skinwidth / 2
      e_sts.append(e_st)
    fill = 256
    draw.line([e_sts[0]['s'], e_sts[0]['t'], e_sts[1]['s'], e_sts[1]['t']], fill=fill)
    draw.line([e_sts[1]['s'], e_sts[1]['t'], e_sts[2]['s'], e_sts[2]['t']], fill=fill)
    draw.line([e_sts[2]['s'], e_sts[2]['t'], e_sts[0]['s'], e_sts[0]['t']], fill=fill)

  img.save('skin.png', 'png')
  # print vars(m)