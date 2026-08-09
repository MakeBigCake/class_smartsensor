#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단일 HTML 책 생성기

content/*.html + assets/*.css  →  Understanding-the-Data-Flow-of-Logistics-Automation-Processes-Based-on-Sensors.html  (파일 1개)

· CSS를 내부에 심어 외부 파일 의존을 없앤다
· 15개 절을 한 문서에 담고 좌측 목차는 내부 앵커로 이동
· 인터넷 없이 열리고, 파일 하나만 보내면 된다

사용법:  python3 bundle.py
"""
import os, re, sys, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from build import TOC, FLAT, COURSE, COURSE_2, META, AUTHOR, WRITTEN, sub_items, sub_block, wrap_head  # 목차 정의 재사용

OUT = os.path.join(BASE, "Understanding-the-Data-Flow-of-Logistics-Automation-Processes-Based-on-Sensors.html")


def read(*p):
    return open(os.path.join(BASE, *p), encoding="utf-8").read()


def anchor(num):
    return "L" + num.replace(".", "-")


def build_toc():
    out = ['  <a href="#cover" data-lesson="cover" data-part="start">목차</a>',
           '  <a href="#Lpreface" data-lesson="preface" data-part="start">머리말</a>']
    out += sub_block("preface", sub_items("preface.html"))
    for chap, items in TOC:
        part = chap.split("부")[0]
        out.append('  <a class="toc-group" href="#C%s" data-part="%s">%s</a>' % (part, part, chap))
        for num, title in items:
            stem = num.replace(".", "-")
            out.append('  <a href="#%s" data-lesson="%s" data-part="%s">%s장 %s</a>'
                       % (anchor(num), stem, num.split(".")[0], num, title))
            subs = sub_items(stem + ".html")
            if not subs:
                continue
            out += sub_block(stem, subs)
    out.append('  <div class="toc-group" data-part="index">찾아보기</div>')
    for aid, lb in (("Lterms","용어 색인"),("Lfigs","그림 색인"),("Ltables","표 색인"),
                    ("Labbr","약어 목록"),("Lrefs","참고문헌")):
        out.append('  <a href="#%s" data-lesson="%s" data-part="index">%s</a>' % (aid, aid[1:].lower(), lb))
    return "\n".join(out)


SPY = """
<script>
(function(){
  var blocks = [].slice.call(document.querySelectorAll('.nav-block'));
  var links  = [].slice.call(document.querySelectorAll('.toc a[data-lesson]'));
  var groups = [].slice.call(document.querySelectorAll('.toc-group[data-part]'));
  var subs   = [].slice.call(document.querySelectorAll('.toc-sub'));
  if(!blocks.length) return;
  function apply(){
    var y = window.scrollY + 140, cur = blocks[0];
    for(var i=0;i<blocks.length;i++){ if(blocks[i].offsetTop <= y) cur = blocks[i]; }
    var nav  = cur.getAttribute('data-nav');
    var part = cur.getAttribute('data-part');
    links.forEach(function(a){ a.classList.toggle('on', a.getAttribute('data-lesson')===nav); });
    groups.forEach(function(g){ g.classList.toggle('on', part!==null && g.getAttribute('data-part')===part); });
    subs.forEach(function(d){ d.style.display = (d.getAttribute('data-for')===nav)?'block':'none'; });
    var open = document.querySelector('.toc-sub[data-for="'+nav+'"]');
    if(!open) return;
    var inner = [].slice.call(open.querySelectorAll('a')), hit = null;
    inner.forEach(function(a){
      var t = document.getElementById(a.getAttribute('href').slice(1));
      if(t && t.getBoundingClientRect().top <= 150) hit = a;
    });
    inner.forEach(function(a){ a.classList.toggle('here', a===hit); });
  }
  var tick=false;
  window.addEventListener('scroll', function(){
    if(tick) return; tick=true;
    requestAnimationFrame(function(){ apply(); tick=false; });
  });
  window.addEventListener('load', apply);
  apply();
})();
</script>
"""


def to_anchor(s):
    """페이지 간 링크를 단일 문서용 내부 앵커로 바꾼다."""
    s = re.sub(r'href="\d-\d\.html#([^"]+)"', lambda m: 'href="#%s"' % m.group(1), s)
    s = re.sub(r'href="(\d)-(\d)\.html"', lambda m: 'href="#L%s-%s"' % (m.group(1), m.group(2)), s)
    s = s.replace('href="index-terms.html"', 'href="#Lterms"')
    s = s.replace('href="index-figs.html"', 'href="#Lfigs"')
    s = s.replace('href="index-tables.html"', 'href="#Ltables"')
    s = s.replace('href="index-abbr.html"', 'href="#Labbr"')
    s = s.replace('href="index-refs.html"', 'href="#Lrefs"')
    s = s.replace('href="preface.html"', 'href="#Lpreface"')
    s = s.replace('href="index.html"', 'href="#cover"')
    return s


def article_body(fn):
    """build.py가 만든 완성본 페이지에서 본문(article)만 뽑는다."""
    h = read(fn)
    m = re.search(r'<article class="article">\n(.*?)\n  </article>', h, re.S)
    return to_anchor(m.group(1)) if m else ""


def strip_cover_shell(html):
    """index.html에서 표지 본문만 뽑아내고, 절 링크를 내부 앵커로 바꾼다."""
    m = re.search(r'<div class="cover-wrap">(.*)</div>\s*</body>', html, re.S)
    return to_anchor(m.group(1) if m else "")


def main():
    css = read("assets", "style.css")
    css_idx = read("assets", "index.css")
    idx = read("index.html")

    # 단일 문서용 추가 스타일
    extra = """
/* ===== 단일 문서 전용 ===== */
.doc-note{background:var(--gold-tint);border:1px solid #EFDCB6;border-left:3px solid var(--gold);
  padding:16px 22px;margin:0 0 34px;font-size:13.5px;color:#5C4310;}
.doc-note b{color:var(--gold-ink);}
.lesson-block{margin-top:64px;}
.lesson-block:first-of-type{margin-top:36px;}
.chapter-divider{margin:80px 0 0;padding:34px 30px 32px;background:var(--navy);color:#fff;}
.chapter-divider h2 > .cd-no{display:inline;font-size:inherit;font-weight:700;
  letter-spacing:.02em;color:inherit;margin:0 16px 0 0;}
.chapter-divider h2{color:#fff;font-size:34px;line-height:1.3;letter-spacing:-.025em;margin:0 0 8px;}
.chapter-divider p{color:#DCE7F3;font-size:15.5px;margin:0;}
.totop{display:block;text-align:right;font-size:11.5px;color:var(--ink-3);
  text-decoration:none;margin-top:40px;padding-top:12px;border-top:1px solid var(--line);}
.totop:hover{color:var(--navy);}
.cover-wrap{max-width:none;padding:0;}
.toc a[href^="#L"]{border-left:3px solid transparent;}
.toc-sub{display:none;}
@media print{
  .toc{display:none;} .totop{display:none;}
  .lesson-block{break-before:page;}
  .chapter-divider{break-before:page;}
}
"""

    chap_theme = {
        "1": ("센서의 기초", "데이터의 생성 — 값은 어디서 태어나는가"),
        "2": ("스마트센서의 구조", "데이터의 지능화 — 센서가 자기 이야기를 한다"),
        "3": ("자동화 장비와 스마트센서", "데이터의 활용 — 값이 설비를 움직인다"),
        "4": ("자동화 공정의 운영", "데이터의 통합 — 공장 전체가 하나로 이어진다"),
    }

    body = []
    body.append('<section id="cover" class="nav-block" data-nav="cover" data-part="start">')
    body.append(strip_cover_shell(idx))
    body.append("</section>")

    body.append('<section class="lesson-block nav-block" id="Lpreface" data-nav="preface" data-part="start">')
    body.append(wrap_head(to_anchor(read("content", "preface.html").rstrip())))
    body.append('<a class="totop" href="#cover">▲ 맨 위로</a>')
    body.append("</section>")

    prev_chap = None
    for num, title, fn, chap in FLAT:
        c = num.split(".")[0]
        if c != prev_chap:
            t, th = chap_theme[c]
            body.append(
                '<div class="chapter-divider nav-block" id="C%s" data-nav="part%s" data-part="%s">'
                '<h2><span class="cd-no">%s부</span>%s</h2><p>%s</p></div>' % (c, c, c, c, t, th)
            )
            prev_chap = c

        part = wrap_head(to_anchor(read("content", fn)))
        # 각 절의 상단에 위치 표시
        body.append('<section class="lesson-block nav-block" id="%s" data-nav="%s" data-part="%s">'
                    % (anchor(num), num.replace(".", "-"), c))
        body.append(part)
        body.append('<a class="totop" href="#cover">▲ 맨 위로</a>')
        body.append("</section>")

    for fn, aid in (("index-terms.html", "Lterms"), ("index-figs.html", "Lfigs"), ("index-tables.html", "Ltables"),
                    ("index-abbr.html", "Labbr"), ("index-refs.html", "Lrefs")):
        body.append('<section class="lesson-block nav-block" id="%s" data-nav="%s" data-part="index">'
                    % (aid, aid[1:].lower()))
        body.append(article_body(fn))
        body.append('<a class="totop" href="#cover">▲ 맨 위로</a>')
        body.append("</section>")

    stamp = datetime.date.today().strftime("%Y-%m-%d")

    html = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{course} — {course2}</title>
<style>
{css}
{css_idx}
{extra}
</style>
</head>
<body>
<div class="layout">

<aside class="toc">
  <div class="toc-head" data-part="start">
    <a class="course-link" href="#cover">
      <div class="course">제목 : {course}</div>
      <div class="course-desc">지은이 : 강승태</div>
      <div class="course-desc">작성일 : 2026-08-10</div>
    </a>
  </div>

{toc}
</aside>

<div class="main">
  <article class="article">
{body}
  </article>
</div>
</div>
{spy}
</body>
</html>
""".format(course=COURSE, course2=COURSE_2, meta=META, css=css, css_idx=css_idx,
           extra=extra, toc=build_toc(), body="\n".join(body), stamp=stamp, spy=SPY)

    open(OUT, "w", encoding="utf-8").write(html)
    kb = os.path.getsize(OUT) // 1024
    print("생성: %s  (%d KB)" % (os.path.basename(OUT), kb))


if __name__ == "__main__":
    main()
