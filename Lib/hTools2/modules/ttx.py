# [h] hTools2.modules.ttx

import os
import time
from fontTools.ttLib import TTFont
from hTools2.modules.sysutils import SuppressPrint
from hTools2.extras.ElementTree import parse

# functions

def ttx2otf(ttx_path, otf_path=None):
    '''Generate an .otf font from a .ttx file.

    **ttx_path** Path of the .ttx font source.
    **otf_path** Path of the target .otf font.

    '''
    # make otf path
    if not otf_path:
        otf_path = '%s.otf' % os.path.splitext(ttx_path)[0]
    # save otf font
    with SuppressPrint():
        tt = TTFont()
        tt.verbose = False
        tt.importXML(ttx_path)
        tt.save(otf_path)

def otf2ttx(otf_path, ttx_path=None):
    '''Generate a .ttx font from an .otf file.

    **otf_path** Path of the .otf font source.
    **ttx_path** Path of the target .ttx font.

    '''
    # make ttx path
    if not ttx_path:
        ttx_path = '%s.ttx' % os.path.splitext(otf_path)[0]
    # save ttx font
    with SuppressPrint():
        tt = TTFont(otf_path)
        tt.verbose = False
        tt.saveXML(ttx_path)

def strip_names(ttx_path):
    '''Clear several nameIDs to prevent the font from being installable on desktop OSs.

    **ttx_path** Path of the .ttx font to be modified.

    '''
    # nameIDs which will be erased
    nameIDs = [1, 2, 4, 16, 17, 18]
    tree = parse(ttx_path)
    root = tree.getroot()
    for child in root.find('name'):
        if int(child.attrib['nameID']) in nameIDs:
            child.text = ' '
    tree.write(ttx_path)

def set_version_string(ttx_path, string_text):
    tree = parse(ttx_path)
    root = tree.getroot()
    for child in root.find('name'):
        if child.attrib['nameID'] == '5':
            child.text = string_text
    tree.write(ttx_path)

def set_unique_name(ttx_path, unique_name):
    tree = parse(ttx_path)
    root = tree.getroot()
    for child in root.find('name'):
        if child.attrib['nameID'] == '3':
            child.text = unique_name
    tree.write(ttx_path)

def fix_font_info(otf_path, family_name, style_name, version_major, version_minor, clear_ttx=True):
    ttx_path = '%s.ttx' % os.path.splitext(otf_path)[0]
    timestamp = time.strftime("%Y%m%d.%H%M%S", time.localtime())
    version_string = 'Version %s.%s' % (version_major, version_minor)
    unique_name = '%s %s: %s' % (family_name, style_name, timestamp)
    otf2ttx(otf_path, ttx_path)
    set_version_string(ttx_path, version_string)
    set_unique_name(ttx_path, unique_name)
    ttx2otf(ttx_path, otf_path)
    if clear_ttx:
        os.remove(ttx_path)

def makeDSIG(tt_font):
    '''
    Add a dummy DSIG table to an OpenType-TTF font, so positioning features work in Office applications on Windows.

    thanks to Ben Kiel on TypeDrawers:
    http://typedrawers.com/discussion/192/making-ot-ttf-layout-features-work-in-ms-word-2010

    '''
    from fontTools import ttLib
    from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord
    newDSIG = ttLib.newTable("DSIG")
    newDSIG.ulVersion = 1
    newDSIG.usFlag = 1
    newDSIG.usNumSigs = 1
    sig = SignatureRecord()
    sig.ulLength = 20
    sig.cbSignature = 12
    sig.usReserved2 = 0
    sig.usReserved1 = 0
    sig.pkcs7 = '\xd3M4\xd3M5\xd3M4\xd3M4'
    sig.ulFormat = 1
    sig.ulOffset = 20
    newDSIG.signatureRecords = [sig]
    tt_font["DSIG"] = newDSIG
    # ugly but necessary -> so all tables are added to ttfont
    # tt_font.lazy = False
    for key in tt_font.keys():
        print tt_font[key]

def add_DSIG_table(otf_path):
    with SuppressPrint():
        tt_font = TTFont(otf_path)
        makeDSIG(tt_font)
        tt_font.save(otf_path)

def extract_tables(otf_path, dest_folder, table_names=['name'], split=True):
    '''Extract font tables from an OpenType font as .ttx.'''
    ttfont = TTFont(otf_path)
    info_file = os.path.splitext(os.path.split(otf_path)[1])[0]
    info_path = os.path.join(dest_folder, '%s.ttx' % info_file)
    ttfont.saveXML(info_path, tables=table_names, splitTables=split)

def find_and_replace_otf(otf_path, dest_path, find_string, replace_string, tables=['name']):
    ttx_path = '%s.ttx' % os.path.splitext(otf_path)[0]
    otf2ttx(otf_path, ttx_path)
    find_and_replace_ttx(ttx_path, find_string, replace_string, tables)
    ttx2otf(ttx_path, dest_path)
    os.remove(ttx_path)

def find_and_replace_ttx(ttx_path, find_string, replace_string, tables=['name']):
    count = 0
    # 1. modify 'name' table
    if 'name' in tables:
        tree  = parse(ttx_path)
        root  = tree.getroot()
        for child in root.find('name'):
            if child.text.find(find_string) != -1:
                new_text = child.text.replace(find_string, replace_string)
                child.text = new_text
                count += 1
        tree.write(ttx_path)
    # 2. modify 'CFF ' table
    if 'CFF ' in tables:
        CFF_elements = ['version', 'Notice', 'Copyright', 'FullName', 'FamilyName', 'Weight']
        tt_font = TTFont()
        tt_font.importXML(ttx_path)
        font_dict = tt_font['CFF '].cff.topDictIndex.items[0]
        for element in CFF_elements:
            text = getattr(font_dict, element)
            if text.find(find_string) != -1:
                new_text = text.replace(find_string, replace_string)
                setattr(font_dict, element, new_text)
                count += 1
        tt_font.saveXML(ttx_path)
    # done
    return count
