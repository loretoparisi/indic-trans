#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from indictrans import Transliterator
from polyglot_tokenizer import Tokenizer


flag = True
s='hin'
t='eng'


forward_transl_full = Transliterator(source=s, target=t, build_lookup=True)

forward_transl_token = Transliterator(source=s, target=t, decode='beamsearch')
back_transl_token = Transliterator(source=t, target=s, build_lookup=True)

tk = Tokenizer(lang=s[:2])
tk_back = Tokenizer(lang=t[:2])

l= u"रज्ज के रुलाया"#\nरज्ज के हंसाया\n\nमैंने दिल खो' के इश्क़ कमाया\n"

l = l.lower().strip()

lines = l.split("\n")
print(lines)


output=[]
if flag == True:
    for l in lines:
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

print(unicode(final_output))