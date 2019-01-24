#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import io

import codecs
import json as js
import argparse
from libindic_.soundex import Soundex
import datetime
from ._utils import UrduNormalizer, WX
from .transliterator import Transliterator
from polyglot_tokenizer import Tokenizer
import regex
import re
#from itertools import filterfalse

import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')

__all__ = ['Transliterator', 'UrduNormalizer', 'WX']

__author__ = "Irshad Ahmad Bhat"
__version__ = "1.0"

UNICODE_NSM = ['\u0300', '\u0301', '\u0302', '\u0303', '\u0304', '\u0305', '\u0306', '\u0307', '\u0308', '\u0309', '\u030A', '\u030B', '\u030C', '\u030D', '\u030E', '\u030F', '\u0310', '\u0311', '\u0312', '\u0313', '\u0314', '\u0315', '\u0316', '\u0317', '\u0318', '\u0319', '\u031A', '\u031B', '\u031C', '\u031D', '\u031E', '\u031F', '\u0320', '\u0321', '\u0322', '\u0323', '\u0324', '\u0325', '\u0326', '\u0327', '\u0328', '\u0329', '\u032A', '\u032B', '\u032C', '\u032D', '\u032E', '\u032F', '\u0330', '\u0331', '\u0332', '\u0333', '\u0334', '\u0335', '\u0336', '\u0337', '\u0338', '\u0339', '\u033A', '\u033B', '\u033C', '\u033D', '\u033E', '\u033F', '\u0340', '\u0341', '\u0342', '\u0343', '\u0344', '\u0345', '\u0346', '\u0347', '\u0348', '\u0349', '\u034A', '\u034B', '\u034C', '\u034D', '\u034E', '\u034F', '\u0350', '\u0351', '\u0352', '\u0353', '\u0354', '\u0355', '\u0356', '\u0357', '\u0358', '\u0359', '\u035A', '\u035B', '\u035C', '\u035D', '\u035E', '\u035F', '\u0360', '\u0361', '\u0362', '\u0363', '\u0364', '\u0365', '\u0366', '\u0367', '\u0368', '\u0369', '\u036A', '\u036B', '\u036C', '\u036D', '\u036E', '\u036F', '\u0483', '\u0484', '\u0485', '\u0486', '\u0487', '\u0591', '\u0592', '\u0593', '\u0594', '\u0595', '\u0596', '\u0597', '\u0598', '\u0599', '\u059A', '\u059B', '\u059C', '\u059D', '\u059E', '\u059F', '\u05A0', '\u05A1', '\u05A2', '\u05A3', '\u05A4', '\u05A5', '\u05A6', '\u05A7', '\u05A8', '\u05A9', '\u05AA', '\u05AB', '\u05AC', '\u05AD', '\u05AE', '\u05AF', '\u05B0', '\u05B1', '\u05B2', '\u05B3', '\u05B4', '\u05B5', '\u05B6', '\u05B7', '\u05B8', '\u05B9', '\u05BA', '\u05BB', '\u05BC', '\u05BD', '\u05BF', '\u05C1', '\u05C2', '\u05C4', '\u05C5', '\u05C7', '\u0610', '\u0611', '\u0612', '\u0613', '\u0614', '\u0615', '\u0616', '\u0617', '\u0618', '\u0619', '\u061A', '\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652', '\u0653', '\u0654', '\u0655', '\u0656', '\u0657', '\u0658', '\u0659', '\u065A', '\u065B', '\u065C', '\u065D', '\u065E', '\u065F', '\u0670', '\u06D6', '\u06D7', '\u06D8', '\u06D9', '\u06DA', '\u06DB', '\u06DC', '\u06DF', '\u06E0', '\u06E1', '\u06E2', '\u06E3', '\u06E4', '\u06E7', '\u06E8', '\u06EA', '\u06EB', '\u06EC', '\u06ED', '\u0711', '\u0730', '\u0731', '\u0732', '\u0733', '\u0734', '\u0735', '\u0736', '\u0737', '\u0738', '\u0739', '\u073A', '\u073B', '\u073C', '\u073D', '\u073E', '\u073F', '\u0740', '\u0741', '\u0742', '\u0743', '\u0744', '\u0745', '\u0746', '\u0747', '\u0748', '\u0749', '\u074A', '\u07A6', '\u07A7', '\u07A8', '\u07A9', '\u07AA', '\u07AB', '\u07AC', '\u07AD', '\u07AE', '\u07AF', '\u07B0', '\u07EB', '\u07EC', '\u07ED', '\u07EE', '\u07EF', '\u07F0', '\u07F1', '\u07F2', '\u07F3', '\u0816', '\u0817', '\u0818', '\u0819', '\u081B', '\u081C', '\u081D', '\u081E', '\u081F', '\u0820', '\u0821', '\u0822', '\u0823', '\u0825', '\u0826', '\u0827', '\u0829', '\u082A', '\u082B', '\u082C', '\u082D', '\u0859', '\u085A', '\u085B', '\u08E4', '\u08E5', '\u08E6', '\u08E7', '\u08E8', '\u08E9', '\u08EA', '\u08EB', '\u08EC', '\u08ED', '\u08EE', '\u08EF', '\u08F0', '\u08F1', '\u08F2', '\u08F3', '\u08F4', '\u08F5', '\u08F6', '\u08F7', '\u08F8', '\u08F9', '\u08FA', '\u08FB', '\u08FC', '\u08FD', '\u08FE', '\u0900', '\u0901', '\u0902', '\u093A', '\u093C', '\u093E', '\u0941', '\u0942', '\u0943', '\u0944', '\u0945', '\u0946', '\u0947', '\u0948', '\u094D', '\u0951', '\u0952', '\u0953', '\u0954', '\u0955', '\u0956', '\u0957', '\u0962', '\u0963', '\u0981', '\u09BC', '\u09C1', '\u09C2', '\u09C3', '\u09C4', '\u09CD', '\u09E2', '\u09E3', '\u0A01', '\u0A02', '\u0A3C', '\u0A41', '\u0A42', '\u0A47', '\u0A48', '\u0A4B', '\u0A4C', '\u0A4D', '\u0A51', '\u0A70', '\u0A71', '\u0A75', '\u0A81', '\u0A82', '\u0ABC', '\u0AC1', '\u0AC2', '\u0AC3', '\u0AC4', '\u0AC5', '\u0AC7', '\u0AC8', '\u0ACD', '\u0AE2', '\u0AE3', '\u0B01', '\u0B3C', '\u0B3F', '\u0B41', '\u0B42', '\u0B43', '\u0B44', '\u0B4D', '\u0B56', '\u0B62', '\u0B63', '\u0B82', '\u0BC0', '\u0BCD', '\u0C3E', '\u0C3F', '\u0C40', '\u0C46', '\u0C47', '\u0C48', '\u0C4A', '\u0C4B', '\u0C4C', '\u0C4D', '\u0C55', '\u0C56', '\u0C62', '\u0C63', '\u0CBC', '\u0CBF', '\u0CC6', '\u0CCC', '\u0CCD', '\u0CE2', '\u0CE3', '\u0D41', '\u0D42', '\u0D43', '\u0D44', '\u0D4D', '\u0D62', '\u0D63', '\u0DCA', '\u0DD2', '\u0DD3', '\u0DD4', '\u0DD6', '\u0E31', '\u0E34', '\u0E35', '\u0E36', '\u0E37', '\u0E38', '\u0E39', '\u0E3A', '\u0E47', '\u0E48', '\u0E49', '\u0E4A', '\u0E4B', '\u0E4C', '\u0E4D', '\u0E4E', '\u0EB1', '\u0EB4', '\u0EB5', '\u0EB6', '\u0EB7', '\u0EB8', '\u0EB9', '\u0EBB', '\u0EBC', '\u0EC8', '\u0EC9', '\u0ECA', '\u0ECB', '\u0ECC', '\u0ECD', '\u0F18', '\u0F19', '\u0F35', '\u0F37', '\u0F39', '\u0F71', '\u0F72', '\u0F73', '\u0F74', '\u0F75', '\u0F76', '\u0F77', '\u0F78', '\u0F79', '\u0F7A', '\u0F7B', '\u0F7C', '\u0F7D', '\u0F7E', '\u0F80', '\u0F81', '\u0F82', '\u0F83', '\u0F84', '\u0F86', '\u0F87', '\u0F8D', '\u0F8E', '\u0F8F', '\u0F90', '\u0F91', '\u0F92', '\u0F93', '\u0F94', '\u0F95', '\u0F96', '\u0F97', '\u0F99', '\u0F9A', '\u0F9B', '\u0F9C', '\u0F9D', '\u0F9E', '\u0F9F', '\u0FA0', '\u0FA1', '\u0FA2', '\u0FA3', '\u0FA4', '\u0FA5', '\u0FA6', '\u0FA7', '\u0FA8', '\u0FA9', '\u0FAA', '\u0FAB', '\u0FAC', '\u0FAD', '\u0FAE', '\u0FAF', '\u0FB0', '\u0FB1', '\u0FB2', '\u0FB3', '\u0FB4', '\u0FB5', '\u0FB6', '\u0FB7', '\u0FB8', '\u0FB9', '\u0FBA', '\u0FBB', '\u0FBC', '\u0FC6', '\u102D', '\u102E', '\u102F', '\u1030', '\u1032', '\u1033', '\u1034', '\u1035', '\u1036', '\u1037', '\u1039', '\u103A', '\u103D', '\u103E', '\u1058', '\u1059', '\u105E', '\u105F', '\u1060', '\u1071', '\u1072', '\u1073', '\u1074', '\u1082', '\u1085', '\u1086', '\u108D', '\u109D', '\u135D', '\u135E', '\u135F', '\u1712', '\u1713', '\u1714', '\u1732', '\u1733', '\u1734', '\u1752', '\u1753', '\u1772', '\u1773', '\u17B4', '\u17B5', '\u17B7', '\u17B8', '\u17B9', '\u17BA', '\u17BB', '\u17BC', '\u17BD', '\u17C6', '\u17C9', '\u17CA', '\u17CB', '\u17CC', '\u17CD', '\u17CE', '\u17CF', '\u17D0', '\u17D1', '\u17D2', '\u17D3', '\u17DD', '\u180B', '\u180C', '\u180D', '\u18A9', '\u1920', '\u1921', '\u1922', '\u1927', '\u1928', '\u1932', '\u1939', '\u193A', '\u193B', '\u1A17', '\u1A18', '\u1A56', '\u1A58', '\u1A59', '\u1A5A', '\u1A5B', '\u1A5C', '\u1A5D', '\u1A5E', '\u1A60', '\u1A62', '\u1A65', '\u1A66', '\u1A67', '\u1A68', '\u1A69', '\u1A6A', '\u1A6B', '\u1A6C', '\u1A73', '\u1A74', '\u1A75', '\u1A76', '\u1A77', '\u1A78', '\u1A79', '\u1A7A', '\u1A7B', '\u1A7C', '\u1A7F', '\u1B00', '\u1B01', '\u1B02', '\u1B03', '\u1B34', '\u1B36', '\u1B37', '\u1B38', '\u1B39', '\u1B3A', '\u1B3C', '\u1B42', '\u1B6B', '\u1B6C', '\u1B6D', '\u1B6E', '\u1B6F', '\u1B70', '\u1B71', '\u1B72', '\u1B73', '\u1B80', '\u1B81', '\u1BA2', '\u1BA3', '\u1BA4', '\u1BA5', '\u1BA8', '\u1BA9', '\u1BAB', '\u1BE6', '\u1BE8', '\u1BE9', '\u1BED', '\u1BEF', '\u1BF0', '\u1BF1', '\u1C2C', '\u1C2D', '\u1C2E', '\u1C2F', '\u1C30', '\u1C31', '\u1C32', '\u1C33', '\u1C36', '\u1C37', '\u1CD0', '\u1CD1', '\u1CD2', '\u1CD4', '\u1CD5', '\u1CD6', '\u1CD7', '\u1CD8', '\u1CD9', '\u1CDA', '\u1CDB', '\u1CDC', '\u1CDD', '\u1CDE', '\u1CDF', '\u1CE0', '\u1CE2', '\u1CE3', '\u1CE4', '\u1CE5', '\u1CE6', '\u1CE7', '\u1CE8', '\u1CED', '\u1CF4', '\u1DC0', '\u1DC1', '\u1DC2', '\u1DC3', '\u1DC4', '\u1DC5', '\u1DC6', '\u1DC7', '\u1DC8', '\u1DC9', '\u1DCA', '\u1DCB', '\u1DCC', '\u1DCD', '\u1DCE', '\u1DCF', '\u1DD0', '\u1DD1', '\u1DD2', '\u1DD3', '\u1DD4', '\u1DD5', '\u1DD6', '\u1DD7', '\u1DD8', '\u1DD9', '\u1DDA', '\u1DDB', '\u1DDC', '\u1DDD', '\u1DDE', '\u1DDF', '\u1DE0', '\u1DE1', '\u1DE2', '\u1DE3', '\u1DE4', '\u1DE5', '\u1DE6', '\u1DFC', '\u1DFD', '\u1DFE', '\u1DFF', '\u20D0', '\u20D1', '\u20D2', '\u20D3', '\u20D4', '\u20D5', '\u20D6', '\u20D7', '\u20D8', '\u20D9', '\u20DA', '\u20DB', '\u20DC', '\u20E1', '\u20E5', '\u20E6', '\u20E7', '\u20E8', '\u20E9', '\u20EA', '\u20EB', '\u20EC', '\u20ED', '\u20EE', '\u20EF', '\u20F0', '\u2CEF', '\u2CF0', '\u2CF1', '\u2D7F', '\u2DE0', '\u2DE1', '\u2DE2', '\u2DE3', '\u2DE4', '\u2DE5', '\u2DE6', '\u2DE7', '\u2DE8', '\u2DE9', '\u2DEA', '\u2DEB', '\u2DEC', '\u2DED', '\u2DEE', '\u2DEF', '\u2DF0', '\u2DF1', '\u2DF2', '\u2DF3', '\u2DF4', '\u2DF5', '\u2DF6', '\u2DF7', '\u2DF8', '\u2DF9', '\u2DFA', '\u2DFB', '\u2DFC', '\u2DFD', '\u2DFE', '\u2DFF', '\u302A', '\u302B', '\u302C', '\u302D', '\u3099', '\u309A', '\uA66F', '\uA674', '\uA675', '\uA676', '\uA677', '\uA678', '\uA679', '\uA67A', '\uA67B', '\uA67C', '\uA67D', '\uA69F', '\uA6F0', '\uA6F1', '\uA802', '\uA806', '\uA80B', '\uA825', '\uA826', '\uA8C4', '\uA8E0', '\uA8E1', '\uA8E2', '\uA8E3', '\uA8E4', '\uA8E5', '\uA8E6', '\uA8E7', '\uA8E8', '\uA8E9', '\uA8EA', '\uA8EB', '\uA8EC', '\uA8ED', '\uA8EE', '\uA8EF', '\uA8F0', '\uA8F1', '\uA926', '\uA927', '\uA928', '\uA929', '\uA92A', '\uA92B', '\uA92C', '\uA92D', '\uA947', '\uA948', '\uA949', '\uA94A', '\uA94B', '\uA94C', '\uA94D', '\uA94E', '\uA94F', '\uA950', '\uA951', '\uA980', '\uA981', '\uA982', '\uA9B3', '\uA9B6', '\uA9B7', '\uA9B8', '\uA9B9', '\uA9BC', '\uAA29', '\uAA2A', '\uAA2B', '\uAA2C', '\uAA2D', '\uAA2E', '\uAA31', '\uAA32', '\uAA35', '\uAA36', '\uAA43', '\uAA4C', '\uAAB0', '\uAAB2', '\uAAB3', '\uAAB4', '\uAAB7', '\uAAB8', '\uAABE', '\uAABF', '\uAAC1', '\uAAEC', '\uAAED', '\uAAF6', '\uABE5', '\uABE8', '\uABED', '\uFB1E', '\uFE00', '\uFE01', '\uFE02', '\uFE03', '\uFE04', '\uFE05', '\uFE06', '\uFE07', '\uFE08', '\uFE09', '\uFE0A', '\uFE0B', '\uFE0C', '\uFE0D', '\uFE0E', '\uFE0F', '\uFE20', '\uFE21', '\uFE22', '\uFE23', '\uFE24', '\uFE25', '\uFE26', '\u101FD', '\u10A01', '\u10A02', '\u10A03', '\u10A05', '\u10A06', '\u10A0C', '\u10A0D', u'\u10A0E', '\u10A0F', '\u10A38', '\u10A39', '\u10A3A', '\u10A3F', '\u11001', '\u11038', '\u11039', '\u1103A', '\u1103B', '\u1103C', '\u1103D', '\u1103E', '\u1103F', '\u11040', '\u11041', '\u11042', '\u11043', '\u11044', '\u11045', '\u11046', '\u11080', '\u11081', '\u110B3', '\u110B4', '\u110B5', '\u110B6', '\u110B9', '\u110BA', '\u11100', '\u11101', '\u11102', '\u11127', '\u11128', '\u11129', '\u1112A', '\u1112B', '\u1112D', '\u1112E', '\u1112F', '\u11130', '\u11131', '\u11132', '\u11133', '\u11134', '\u11180', '\u11181', '\u111B6', '\u111B7', '\u111B8', '\u111B9', '\u111BA', '\u111BB', '\u111BC', '\u111BD', '\u111BE', '\u116AB', '\u116AD', '\u116B0', '\u116B1', '\u116B2', '\u116B3', '\u116B4', '\u116B5', '\u116B7', '\u16F8F', '\u16F90', '\u16F91', '\u16F92', '\u1D167', '\u1D168', '\u1D169', '\u1D17B', '\u1D17C', '\u1D17D', '\u1D17E', '\u1D17F', '\u1D180', '\u1D181', '\u1D182', '\u1D185', '\u1D186', '\u1D187', '\u1D188', '\u1D189', '\u1D18A', '\u1D18B', '\u1D1AA', '\u1D1AB', '\u1D1AC', '\u1D1AD', '\u1D242', '\u1D243', '\u1D244', '\uE0100', '\uE0101', '\uE0102', '\uE0103', '\uE0104', '\uE0105', '\uE0106', '\uE0107', '\uE0108', '\uE0109', '\uE010A', '\uE010B', '\uE010C', '\uE010D', '\uE010E', '\uE010F', '\uE0110', '\uE0111', '\uE0112', '\uE0113', '\uE0114', '\uE0115', '\uE0116', '\uE0117', '\uE0118', '\uE0119', '\uE011A', '\uE011B', '\uE011C', '\uE011D', '\uE011E', '\uE011F', '\uE0120', '\uE0121', '\uE0122', '\uE0123', '\uE0124', '\uE0125', '\uE0126', '\uE0127', '\uE0128', '\uE0129', '\uE012A', '\uE012B', '\uE012C', '\uE012D', '\uE012E', '\uE012F', '\uE0130', '\uE0131', '\uE0132', '\uE0133', '\uE0134', '\uE0135', '\uE0136', '\uE0137', '\uE0138', '\uE0139', '\uE013A', '\uE013B', '\uE013C', '\uE013D', '\uE013E', '\uE013F', '\uE0140', '\uE0141', '\uE0142', '\uE0143', '\uE0144', '\uE0145', '\uE0146', '\uE0147', '\uE0148', '\uE0149', '\uE014A', '\uE014B', '\uE014C', '\uE014D', '\uE014E', '\uE014F', '\uE0150', '\uE0151', '\uE0152', '\uE0153', '\uE0154', '\uE0155', '\uE0156', '\uE0157', '\uE0158', '\uE0159', '\uE015A', '\uE015B', '\uE015C', '\uE015D', '\uE015E', '\uE015F', '\uE0160', '\uE0161', '\uE0162', '\uE0163', '\uE0164', '\uE0165', '\uE0166', '\uE0167', '\uE0168', '\uE0169', '\uE016A', '\uE016B', '\uE016C', '\uE016D', '\uE016E', '\uE016F', '\uE0170', '\uE0171', '\uE0172', '\uE0173', '\uE0174', '\uE0175', '\uE0176', '\uE0177', '\uE0178', '\uE0179', '\uE017A', '\uE017B', '\uE017C', '\uE017D', '\uE017E', '\uE017F', '\uE0180', '\uE0181', '\uE0182', '\uE0183', '\uE0184', '\uE0185', '\uE0186', '\uE0187', '\uE0188', '\uE0189', '\uE018A', '\uE018B', '\uE018C', '\uE018D', '\uE018E', '\uE018F', '\uE0190', '\uE0191', '\uE0192', '\uE0193', '\uE0194', '\uE0195', '\uE0196', '\uE0197', '\uE0198', '\uE0199', '\uE019A', '\uE019B', '\uE019C', '\uE019D', '\uE019E', '\uE019F', '\uE01A0', '\uE01A1', '\uE01A2', '\uE01A3', '\uE01A4', '\uE01A5', '\uE01A6', '\uE01A7', '\uE01A8', '\uE01A9', '\uE01AA', '\uE01AB', '\uE01AC', '\uE01AD', '\uE01AE', '\uE01AF', '\uE01B0', '\uE01B1', '\uE01B2', '\uE01B3', '\uE01B4', '\uE01B5', '\uE01B6', '\uE01B7', '\uE01B8', '\uE01B9', '\uE01BA', '\uE01BB', '\uE01BC', '\uE01BD', '\uE01BE', '\uE01BF', '\uE01C0', '\uE01C1', '\uE01C2', '\uE01C3', '\uE01C4', '\uE01C5', '\uE01C6', '\uE01C7', '\uE01C8', '\uE01C9', '\uE01CA', '\uE01CB', '\uE01CC', '\uE01CD', '\uE01CE', '\uE01CF', '\uE01D0', '\uE01D1', '\uE01D2', '\uE01D3', '\uE01D4', '\uE01D5', '\uE01D6', '\uE01D7', '\uE01D8', '\uE01D9', '\uE01DA', '\uE01DB', '\uE01DC', '\uE01DD', '\uE01DE', '\uE01DF', '\uE01E0', '\uE01E1', '\uE01E2', '\uE01E3', '\uE01E4', '\uE01E5', '\uE01E6', '\uE01E7', '\uE01E8', '\uE01E9', '\uE01EA', '\uE01EB', '\uE01EC', '\uE01ED', '\uE01EE', '\uE01EF']


def parse_args(args):
    languages = '''hin guj pan ben mal kan tam tel ori
                   eng mar nep bod kok asm urd'''.split()
    modes = '''json stdout'''.split()
    # help messages
    lang_help = "select language (3 letter ISO-639 code) {%s}" % (
        ', '.join(languages))
    # parse command line arguments
    parser = argparse.ArgumentParser(
        prog="indictrans",
        description="Transliterator for Indian Languages including English")
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-v',
                        '--version',
                        action="version",
                        version="%(prog)s 1.0")
    parser.add_argument(
        '-s',
        '--source',
        dest="source",
        choices=languages,
        default="hin",
        metavar='',
        help="%s" % lang_help)
    parser.add_argument(
        '-t',
        '--target',
        dest="target",
        choices=languages,
        default="eng",
        metavar='',
        help="%s" % lang_help)
    parser.add_argument(
        '-b',
        '--build-lookup',
        dest="build_lookup",
        action='store_true',
        help='build lookup to fasten transliteration')
    group.add_argument(
        '-m',
        '--ml',
        action='store_true',
        help='use ML system for transliteration')

    parser.add_argument(
        '-f',
        '--format',
        choices=modes,
        default="stdout",
        dest="output_format",
        help='output format')

    group.add_argument(
        '-r',
        '--rb',
        action='store_true',
        help='use rule-based system for transliteration')

    parser.add_argument(
        '-i',
        '--input',
        dest="infile",
        type=str,
        metavar='',
        help="<input-file>")
    parser.add_argument(
        '-o',
        '--output',
        dest="outfile",
        type=str,
        metavar='',
        help="<output-file>")
    
    args = parser.parse_args(args)
    if args.source == args.target:
        sys.stderr.write(
            'indictrans: error: source must be different from target\n')
        sys.stderr.write(parser.parse_args(['-h']))
    return args


def process_args(args):
    if not (args.ml or args.rb):
        args.rb = True
    if args.infile:
        ifp = io.open(args.infile, encoding='utf-8')
    else:
        if sys.version_info[0] >= 3:
            ifp = codecs.getreader('utf8')(sys.stdin.buffer)
        else:
            ifp = codecs.getreader('utf8')(sys.stdin)

    if args.outfile:
        ofp = io.open(args.outfile, mode='w', encoding='utf-8')
    else:
        if sys.version_info[0] >= 3:
            ofp = codecs.getwriter('utf8')(sys.stdout.buffer)
        else:
            ofp = codecs.getwriter('utf8')(sys.stdout)

    if args.output_format=='stdout':
       
        # initialize transliterator object
        trn = Transliterator(args.source, args.target, rb=args.rb, build_lookup=args.build_lookup)

        # transliterate text
        for line in ifp:
            tline = trn.convert(line)
            ofp.write(tline)

        # close files
        ifp.close()
        ofp.close()
        


    if args.output_format=='json':
       
        
        s=args.source
        t=args.target
        
        forward_transl_full = Transliterator(source=s, target=t, rb=args.rb, build_lookup=True)

        forward_transl_token = Transliterator(source=s, target=t, rb=args.rb, decode='beamsearch')
        back_transl_token = Transliterator(source=t, target=s, rb=args.rb, build_lookup=True)

        tk = Tokenizer(lang=s[:2])
        tk_back = Tokenizer(lang=t[:2])

        instance = Soundex()

        output=[]

        text_precedent_len = 0

        for l in ifp:

            json = {}
            definitive = forward_transl_full.transform(l.strip())
            
            json["text"] = definitive
            json["tokens"] = []
            
            tokens = []
            
            tokens=tk.tokenize(l)

            back_tokens = tk_back.tokenize(definitive)

            for i,t in enumerate(tokens):
                
                inner_json = {}
                choosen = back_tokens[i]
                suggestions = []
                exclusions = []

                forward_out = forward_transl_token.transform(t)

                for c in forward_out:
                    
                    back_out = back_transl_token.transform(c)

                    if back_out == t and c != choosen:
                        suggestions.append(c)
                    else:
                        if c != choosen:
                            exclusions.append(c)

                all_possible_choices = list(suggestions)
                all_possible_choices.insert(0,choosen)

                transformed = []
                for c in all_possible_choices:
                    t = instance.soundex(c)
                    transformed.append(t)

                duplicates = {}

                for i,t in enumerate(transformed):
                    if t not in duplicates:
                        original_text = all_possible_choices[i]
                        duplicates[t] = [] 
                        duplicates[t].append(original_text)
                    else:
                        original_text = all_possible_choices[i]
                        duplicates[t].append(original_text)

                new_duplicates = {}
                suggestion_duplicates = []

                for k,v in duplicates.items():
                    new_duplicates[v[0]] = v[1:]
                    suggestion_duplicates.extend(v[1:])
                    
                inner_json["token"] = choosen
                inner_json["duplicates"] = new_duplicates
                inner_json["exclusions"] = exclusions
                inner_json["suggestions"] = [s for s in suggestions if s not in suggestion_duplicates]
                inner_json["offset"] = text_precedent_len + 1
                inner_json["length"] =sum(1 for c in choosen if not c in UNICODE_NSM)
                json["tokens"].append(inner_json)
                text_precedent_len += inner_json["length"]+1

            output.append(json)
        
        final_output = {"sentences" : output}
        
        r = js.dumps(final_output)
        
        ofp.write(r)
      


        

def main():
    args = parse_args(sys.argv[1:])
    process_args(args)
