# [h] hTools2.modules.anchors

'''Tools to create, move, delete and transfer anchors.'''

from hTools2.modules.color import clear_colors, random_color

# font-level tools

def get_anchors(font, glyph_names=None):
    '''Get anchors from a font as a dictionary.

    **glyph_names** A list of glyphs to restrict selection.

    Returns a dictionary with anchor names and positions for each glyph.

    '''
    anchors_dict = {}
    if glyph_names == None:
        _glyph_names = font.keys()
    else:
        _glyph_names = glyph_names
    for glyph_name in _glyph_names:
        g = font[glyph_name]
        if len(g.anchors) > 0:
            anchors = []
            for a in g.anchors:
                anchors.append((a.name, (a.x, a.y)))
            anchors_dict[g.name] = anchors
    return anchors_dict

def clear_anchors(font, glyph_names=None):
    '''Delete all anchors in the font.

    **glyph_names** A list of glyphs to restrict selection.

    '''
    if glyph_names is None:
        glyph_names = font.keys()
    for glyph_name in glyph_names:
        if font.has_key(glyph_name) and len(font[glyph_name].anchors) > 0:
            font[glyph_name].prepareUndo('clear anchors')
            font[glyph_name].clearAnchors()
            font[glyph_name].changed()
            font[glyph_name].performUndo()
    font.changed()

def find_lost_anchors(font):
    '''Find anchors which are lost outside of the glyph box.'''
    clear_colors(font)
    c = random_color()
    lost_anchors = []
    for g in font:
        if len(g.anchors) > 0:
            for a in g.anchors:
                if a.y > f.info.unitsPerEm:
                    lost_anchors.append((g.name, a.name, (a.x, a.y) ))
                    g.mark = c
    return lost_anchors


def remove_duplicate_anchors(font):
    '''Delete duplicate anchors with same name and position.'''
    pass

def get_anchors_dict(accents_dict):
    '''Get an anchors dict from a glyph construction dict (accents).

    Returns a dictionary with anchor names and positions for each glyph.

    '''
    # get anchors
    anchors_dict = {}
    for accented_glyph in accents_dict.keys():
        # get base glyph and accents
        base, accents = accents_dict[accented_glyph]
        # create entry
        if not anchors_dict.has_key(base):
            anchors_dict[base] = []
        # add anchor to lib
        for accent in accents:
            anchor_name = accent[1]
            if anchor_name not in anchors_dict[base]:
                anchors_dict[base].append(anchor_name)
    # done
    return anchors_dict

def get_accents_anchors_dict(accents_dict):
    # get anchors
    anchors_dict = {}
    for accented_glyph in accents_dict.keys():
        # get base glyph and accents
        base, accents = accents_dict[accented_glyph]
        for accent_name, accent_anchor in accents:
            if not anchors_dict.has_key(accent_name):
                anchors_dict[accent_name] = []
            if accent_anchor not in anchors_dict[accent_name]:
                anchors_dict[accent_name].append(accent_anchor)
    # done
    return anchors_dict

# glyph-level tools

def rename_anchor(glyph, old_name, new_name):
    '''Rename named anchor in the given glyph.

    **old_name** Old anchor name to be replace.
    **new_name** New anchor name.

    Returns a boolean indicating if the glyph has any anchor with the given *old_name*.

    '''
    has_name = False
    if len(glyph.anchors) > 0:
        for a in glyph.anchors:
            if a.name == old_name:
                has_name = True
                a.name = new_name
                glyph.changed()
    return has_name

def transfer_anchors(source_glyph, dest_glyph, clear=True, proportional=False):
    '''Transfer all anchors from one glyph to another.

    **source_glyph** The source glyph for the anchors.
    **dest_glyph** The destination glyph.

    Returns a boolean indicating if the source glyph has any anchor.

    '''
    has_anchor = False
    if len(source_glyph.anchors) > 0 :
        # collect anchors in source glyph
        has_anchor = True
        anchorsDict = {}
        for a in source_glyph.anchors:
            anchorsDict[a.name] = a.x, a.y
        # clear anchors in dest glyph
        if clear:
            dest_glyph.clearAnchors()
        # place anchors in dest glyph
        for anchor in anchorsDict:
            x, y = anchorsDict[anchor]
            if proportional:
                factor = dest_glyph.width / float(source_glyph.width)
                x *= factor
            dest_glyph.appendAnchor(anchor, (x, y))
            dest_glyph.changed()
    # done
    return has_anchor

def move_anchors(glyph, anchor_names, (delta_x, delta_y)):
    '''Move named anchors in the given glyph.

    **anchor_names** A list of anchor names to move.
    **delta_x** The horizontal move distance.
    **delta_y** The vertical move distance.

    '''
    for anchor in glyph.anchors:
        if anchor.name in anchor_names:
            anchor.moveBy((delta_x, delta_y))
            glyph.changed()

def create_anchors(glyph, top=True, bottom=True, accent=False, top_pos=20, bottom_pos=20):
    '''Create anchors in glyph.

    **top** Create or not *top* anchors.
    **bottom** Create or not *bottom* anchors.
    **accent** Create ot not accent anchors with underscore prefix.
    **top_pos** Position of the *top* anchors.
    **bottom_pos** Position of the *bottom* anchors.

    '''
    # make anchors list
    anchor_names = []
    if top:
        anchor_names.append('top')
    if bottom:
        anchor_names.append('bottom')
    # run
    font = glyph.getParent()
    has_anchor = False
    anchors = []
    # get existing anchors
    if len(glyph.anchors) > 0 :
        has_anchor = True
        for a in glyph.anchors:
            anchors.append(a.name)
    # add only new anchors
    x = glyph.width / 2
    for anchor_name in anchor_names:
        # add underscore if accent
        if accent:
            anchor_name = '_' + anchor_name
        if anchor_name not in anchors:
            # make anchor y-position
            if anchor_name in [ 'top', '_top' ]:
                y = top_pos
            else:
                y = bottom_pos
            # place anchor
            glyph.appendAnchor(anchor_name, (x, y))
    # done glyph
    glyph.update()

def clear_duplicate_anchors(glyph):
    '''Delete duplicate anchors with same name and position.'''
    anchors = []
    glyph.prepareUndo('delete duplicate anchors')
    for anchor in glyph.anchors:
        a = anchor.name, anchor.position
        if a in anchors:
            glyph.removeAnchor(anchor)
        else:
            anchors.append(a)
    glyph.performUndo()
