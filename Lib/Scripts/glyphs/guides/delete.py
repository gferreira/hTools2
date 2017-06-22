# [h] clear guides

'''Remove all guides in selected glyphs.'''

from mojo.roboFont import CurrentFont
from hTools2.modules.fontutils import get_glyphs
from hTools2.modules.glyphutils import clear_guides
from hTools2.modules.messages import no_font_open, no_glyph_selected

f = CurrentFont()

if f is not None:

    glyph_names = get_glyphs(f)

    if len(glyph_names) > 0:
        for glyph_name in glyph_names:
            clear_guides(f[glyph_name])

    # no glyph selected
    else:
        print no_glyph_selected

# no font open
else:
    print no_font_open
