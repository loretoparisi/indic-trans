#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import io
import sys
import codecs
import argparse

from ._utils import UrduNormalizer, WX
from .transliterator import Transliterator
from polyglot_tokenizer import Tokenizer

__all__ = ['Transliterator', 'UrduNormalizer', 'WX']

__author__ = "Irshad Ahmad Bhat"
__version__ = "1.0"


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

    group.add_argument(
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
        
        forward_transl_full = Transliterator(source=s, target=t, build_lookup=True)

        forward_transl_token = Transliterator(source=s, target=t, decode='beamsearch')
        back_transl_token = Transliterator(source=t, target=s, build_lookup=True)

        tk = Tokenizer(lang=s[:2])
        tk_back = Tokenizer(lang=t[:2])

        output=[]
        for l in ifp:
            json = {}

            definitive = forward_transl_full.transform(l)
            
            json["text"] = definitive
            json["tokens"] = []
            
            tokens = []
            text_precedent = ""

            tokens=tk.tokenize(l)
            
            back_tokens = tk_back.tokenize(definitive)

            for i,t in enumerate(tokens):
                
                inner_json = {}
                choosen = back_tokens[i]
                suggestions = []
                forward_out = forward_transl_token.transform(t)

                for c in forward_out:
                    back_out = back_transl_token.transform(c)

                    if back_out == t and c != choosen:
                        suggestions.append(c)
                
                inner_json["token"] = choosen
                inner_json["suggestions"] = suggestions
                inner_json["offset"] = len(text_precedent)+1
                inner_json["length"] = len(t)
                
                json["tokens"].append(inner_json)
                
                text_precedent+=t + " "

            output.append(json)
        
    final_output = {"sentences" : output}
    ofp.write(unicode(final_output))

def main():
    args = parse_args(sys.argv[1:])
    process_args(args)
