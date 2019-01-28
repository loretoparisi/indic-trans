#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import io
import os,sys

parentPath = os.path.abspath("indictrans")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

import codecs
import json as js
import argparse
from libindic_.soundex import Soundex
import datetime
from ._utils import UrduNormalizer, WX
from .transliterator import Transliterator
from polyglot_tokenizer import Tokenizer
from unicode_marks import UNICODE_NSM_ALL

import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')

__all__ = ['Transliterator', 'UrduNormalizer', 'WX']

__author__ = "Irshad Ahmad Bhat"
__version__ = "1.0"

def clean_str(t):
    t=t.replace(u"\u0000","").strip()
    return t
    


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
        sys.stderr.write('error: source must be different from target\n')
        #sys.stderr.write(parser.parse_args(['-h']))
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

            #transform entire sentence as first choice
            definitive = forward_transl_full.transform(l.strip())


            json["text"] = clean_str(definitive)
            json["tokens"] = []
            
            tokens = []
            
            # tokenize initial sentence in tokens
            tokens=tk.tokenize(l)

            #backtokenize text transformed
            back_tokens = tk_back.tokenize(definitive)

            for i,(t,choosen) in enumerate(zip(tokens,back_tokens)):
                print(i)
                print(t)
                
                inner_json = {}
                
                suggestions = []
                exclusions = []

                forward_out = forward_transl_token.transform(t)

                for c in forward_out:
                    
                    back_out = back_transl_token.transform(c)

                    if back_out == t and c != choosen:
                        suggestions.append(c)
                    else:
                        if c != choosen:
                            exclusions.append(c.replace(u"\u0000",""))

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
                        duplicates[t].append(clean_str(original_text))
                    else:
                        original_text = all_possible_choices[i]
                        duplicates[t].append(clean_str(original_text))

                new_duplicates = {}
                suggestion_duplicates = []

                for k,v in duplicates.items():
                    new_duplicates[v[0]] = v[1:]
                    suggestion_duplicates.extend(v[1:])
                

                inner_json["token"] = clean_str(choosen)
                inner_json["duplicates"] = new_duplicates
                inner_json["exclusions"] = exclusions
                inner_json["suggestions"] = [s for s in suggestions if s not in suggestion_duplicates]
                inner_json["offset"] = text_precedent_len + 1
                inner_json["length"] =len([1 for c in choosen if not c in UNICODE_NSM_ALL])
                json["tokens"].append(inner_json)
                text_precedent_len += inner_json["length"]+1

            output.append(json)
        
        final_output = {"sentences" : output}
        
        r = js.dumps(final_output)
        ofp.write(r)

def main():
    args = parse_args(sys.argv[1:])
    process_args(args)
