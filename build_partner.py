# -*- coding: utf-8 -*-
import re

SRC = r"C:\Users\yoriz\momsolve-partner-landing\index.html"
OUT = r"C:\Users\yoriz\momsolve-partner-landing\partner_cafe24.html"
BASE = "https://momsolve7-rgb.github.io/momsolve-partner-landing/"

def scope_css(css, s):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out = []
    i, n = 0, len(css)
    while i < n:
        op = css.find('{', i)
        if op < 0:
            out.append(css[i:]); break
        sel = css[i:op].strip()
        depth, j = 0, op
        while j < n:
            c = css[j]
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
            j += 1
        inner = css[op+1:j]
        low = sel.lower()
        if low.startswith('@media') or low.startswith('@supports'):
            out.append(sel + '{' + scope_css(inner, s) + '}')
        elif sel.startswith('@'):
            out.append(sel + '{' + inner + '}')
        else:
            parts = [p.strip() for p in sel.split(',') if p.strip()]
            np = []
            for x in parts:
                if x == ':root': np.append(':root')
                elif x == '*': np.append(s + ' *')
                elif x in ('html', 'body'): np.append(s)
                else: np.append(s + ' ' + x)
            out.append(', '.join(np) + '{' + inner + '}')
        i = j + 1
    return ''.join(out)

html = open(SRC, encoding='utf-8').read()
html = html.replace('"img/', '"' + BASE + 'img/')
css = re.search(r'<style[^>]*>(.*?)</style>', html, re.S).group(1)
body = re.search(r'<body[^>]*>(.*?)</body>', html, re.S).group(1)
scoped = scope_css(css, '#msv')

fullbleed = ('/* cafe24 본문 영역 좌우 꽉 차게 (이 페이지 한정, brand.html과 동일) */\n'
             '#contents{width:100% !important;max-width:100% !important;padding-left:0 !important;padding-right:0 !important;}\n'
             '#msv{overflow-x:hidden;}\n')

content = ('<!--@layout(/layout/basic/layout.html)-->\n'
           '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">\n'
           '<style>\n' + fullbleed + scoped + '\n</style>\n'
           '<div id="msv">\n' + body + '\n</div>\n')

open(OUT, 'w', encoding='utf-8').write(content)
print("OUT", OUT, "len", len(content))
print("has @layout:", content.startswith('<!--@layout'))
print("has #msv:", '#msv' in content)
print("root preserved:", ':root{' in content or ':root {' in content)
print("keyframes preserved:", '@keyframes badgeShine' in content)
