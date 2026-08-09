#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터를 읽는 감각 — 물류 자동화 현장의 센서
책 빌드 스크립트

content/1-1.html … content/4-3.html  (본문만)
        ↓  좌측 목차 · 상단 브레드크럼 · 이전/다음 자동 주입
      1-1.html … 4-3.html            (배포용 완성본)

사용법:  python3 build.py
"""
import os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))

COURSE   = "데이터를 읽는 감각"
COURSE_2 = "물류 자동화 현장의 센서"
META     = "전 4부 15장 · 비전공 기술자를 위한 책"
AUTHOR   = "강승태"
WRITTEN  = "2026-08-10"          # 작성일 (자동 갱신하지 않는다)

# (챕터 제목, [(번호, 제목), ...])
TOC = [
    ("1부 · 센서의 기초 : 데이터의 생성", [
        ("1.1", "센서의 정의와 원리"),
        ("1.2", "다양한 센서 분류"),
        ("1.3", "현장 확인 성능 지표"),
        ("1.4", "오작동 방지와 기본 세팅"),
    ]),
    ("2부 · 스마트센서의 구조 : 데이터의 지능화", [
        ("2.1", "스마트센서의 등장"),
        ("2.2", "핵심 내부 구조"),
        ("2.3", "플러그 앤 플레이"),
        ("2.4", "지능형 기능"),
    ]),
    ("3부 · 자동화 장비와 센서 : 데이터의 활용", [
        ("3.1", "장비 제어의 기본 원리"),
        ("3.2", "서보 모터와 센서의 융합"),
        ("3.3", "현장 통신 프로토콜"),
        ("3.4", "예지 보전"),
    ]),
    ("4부 · 자동화 공정의 운영 : 데이터의 통합", [
        ("4.1", "산업용 IoT 게이트웨이"),
        ("4.2", "에지 컴퓨팅 정책"),
        ("4.3", "생존형 네트워크 인프라"),
    ]),
]

# 부 도입 면 : (부 제목, 부제)
PART_THEME = {
    "1": ("센서의 기초", "데이터의 생성 — 값은 어디서 태어나는가"),
    "2": ("스마트센서의 구조", "데이터의 지능화 — 센서가 자기 이야기를 한다"),
    "3": ("자동화 장비와 센서", "데이터의 활용 — 값이 설비를 움직인다"),
    "4": ("자동화 공정의 운영", "데이터의 통합 — 공장 전체가 하나로 이어진다"),
}

# 평탄화 : [(번호, 제목, 파일명, 챕터제목), ...]
FLAT = []
for chap, items in TOC:
    for num, title in items:
        FLAT.append((num, title, num.replace(".", "-") + ".html", chap))
TOTAL = len(FLAT)

# 앞뒤 이동 순서 (부 도입 면 포함)
ORDER = ["index.html", "preface.html"]
_seen = set()
for _n, _t, _f, _c in FLAT:
    _p = _n.split(".")[0]
    if _p not in _seen:
        ORDER.append("part%s.html" % _p); _seen.add(_p)
    ORDER.append(_f)
ORDER += ["index-terms.html", "index-figs.html", "index-tables.html",
          "index-abbr.html", "index-refs.html"]


def around(fn):
    """이 페이지의 이전/다음 링크"""
    i = ORDER.index(fn) if fn in ORDER else -1
    p = '<a href="%s">◀ 이전</a>' % ORDER[i - 1] if i > 0 else '<span class="disabled">◀ 이전</span>'
    n = ('<a href="%s">다음 ▶</a>' % ORDER[i + 1] if 0 <= i < len(ORDER) - 1
         else '<span class="disabled">다음 ▶</span>')
    return p, n


SECNO_RE = re.compile(r'<div class="sec-no">([^<]+)</div>\s*<h2>')


def inline_secno(s):
    """절 번호를 제목 안으로 들여, 번호와 제목이 한 덩어리로 읽히게 한다.
       '참고자료'처럼 제목과 겹치는 표기는 번호를 붙이지 않는다."""
    def sub(m):
        no = m.group(1).strip()
        if not re.match(r"^[\d.]+$", no):
            return "<h2>"
        return '<h2><span class="sec-no">%s</span>' % no
    return SECNO_RE.sub(sub, s)


HEAD_RE = re.compile(
    r'(\s*<div class="lesson-tag">.*?</div>\s*<h1>.*?</h1>\s*<p class="subtitle">.*?</p>)', re.S)


def wrap_head(s):
    """장 머리를 .lesson-head 띠로 감싸고, 장 번호와 절 번호를 제목 안으로 들인다."""
    s = inline_secno(s)

    def band(m):
        def tag(x):
            t = x.group(1).strip()
            sep = "" if re.match(r"^[\d.]+$", t) else " :"
            return '<h1><span class="lesson-tag">%s%s</span>' % (t, sep)

        head = re.sub(r'<div class="lesson-tag">(.*?)</div>\s*<h1>', tag, m.group(1), count=1)
        return '\n    <div class="lesson-head">%s\n    </div>' % head

    return HEAD_RE.sub(band, s, count=1)


def sub_items(fn):
    """content/N-N.html 에서 3뎁스 (번호, 제목) 목록을 뽑는다."""
    p = os.path.join(BASE, "content", fn)
    if not os.path.exists(p):
        return []
    s = open(p, encoding="utf-8").read()
    out = []
    for m in re.finditer(
            r'<div class="sec-no">([^<]*)</div>\s*<h2>(.*?)(?:<span class="en">|</h2>)', s, re.S):
        no = m.group(1).strip()
        title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        out.append((no, title))
    return out


def sub_block(stem, subs, extra=""):
    """3뎁스 하위 목차 블록. 앵커는 s{stem}-{i} / r{stem}."""
    out = ['  <div class="toc-sub" data-for="%s"%s>' % (stem, extra)]
    for i, (no, title) in enumerate(subs, 1):
        if no == "참고자료":
            out.append('    <a href="#r%s">참고자료</a>' % stem)
        elif no.isdigit():                       # 머리말 : 번호 대신 제목만
            out.append('    <a href="#p%s">%s</a>' % (no, title))
        else:
            out.append('    <a href="#s%s-%d">%s %s</a>' % (stem, i, no, title))
    out.append('  </div>')
    return out


def build_toc(current_file):
    IDXF = ("index-terms.html", "index-figs.html", "index-tables.html",
            "index-abbr.html", "index-refs.html")
    out = ['  <a href="index.html"%s>목차</a>'
           % (' class="on"' if current_file == "index.html" else "")]
    pre = current_file == "preface.html"
    out.append('  <a href="preface.html"%s>머리말</a>'
               % (' class="on"' if pre else ""))
    if pre:
        out += sub_block("preface", sub_items("preface.html"))
    cur_part = current_file[0] if current_file[:1].isdigit() else None
    if current_file.startswith("part"):
        cur_part = current_file[4]
    for chap, items in TOC:
        part = chap.split("부")[0]
        pf = "part%s.html" % part
        on = " on" if (part == cur_part or current_file == pf) else ""
        out.append('  <a class="toc-group%s" href="%s">%s</a>' % (on, pf, chap))
        for num, title in items:
            fn = num.replace(".", "-") + ".html"
            cur = fn == current_file
            out.append('  <a href="%s"%s>%s장 %s</a>'
                       % (fn, ' class="on"' if cur else "", num, title))
            if not cur:
                continue
            stem = num.replace(".", "-")
            subs = sub_items(fn)
            if not subs:
                continue
            out += sub_block(stem, subs)
    out.append('  <div class="toc-group%s">찾아보기</div>'
               % (" on" if current_file in IDXF else ""))
    for fn, label in (("index-terms.html", "용어 색인"), ("index-figs.html", "그림 색인"), ("index-tables.html", "표 색인"),
                      ("index-abbr.html", "약어 목록"), ("index-refs.html", "참고문헌")):
        on = ' class="on"' if fn == current_file else ""
        out.append('  <a href="%s"%s>%s</a>' % (fn, on, label))
    return "\n".join(out)


SHELL = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{num} {title} — {course}</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="layout">

<!-- ================= 좌측 목차 (build.py 자동 생성) ================= -->
<aside class="toc">
  <div class="toc-head" data-part="start">
    <a class="course-link" href="index.html">
      <div class="course">제목 : {course}</div>
      <div class="course-desc">지은이 : {author}</div>
      <div class="course-desc">작성일 : {written}</div>
    </a>
  </div>

{toc}
</aside>

<!-- ================= 본문 ================= -->
<div class="main">

  <div class="topbar">
    <div class="crumb">
      <span class="c1">{chapter}</span>
      <span>›</span>
      <span class="c2">{num} {title}</span>
    </div>
    <div class="nav">
      <a href="index.html" class="home">목차</a>
      {prev}
      <span class="count">{idx} / {total}</span>
      {next}
    </div>
  </div>

  <article class="article">
{body}
  </article>
</div>
</div>
</body>
</html>
"""


def main():
    src_dir = os.path.join(BASE, "content")
    if not os.path.isdir(src_dir):
        sys.exit("content/ 폴더가 없습니다.")

    made, skipped = [], []
    for i, (num, title, fn, chap) in enumerate(FLAT):
        src = os.path.join(src_dir, fn)
        if not os.path.exists(src):
            skipped.append(fn)
            continue
        body = wrap_head(open(src, encoding="utf-8").read().rstrip())

        prev_html, next_html = around(fn)

        html = SHELL.format(
            num=num, title=title, course=COURSE, course2=COURSE_2, meta=META,
            toc=build_toc(fn), chapter=chap, prev=prev_html, next=next_html,
            author=AUTHOR, written=WRITTEN,
            idx=i + 1, total=TOTAL, body=body,
        )
        open(os.path.join(BASE, fn), "w", encoding="utf-8").write(html)
        made.append(fn)

    cov = os.path.join(src_dir, "cover.html")
    if os.path.exists(cov):
        html = SHELL.format(
            num="", title="목차", course=COURSE, course2=COURSE_2, meta=META,
            author=AUTHOR, written=WRITTEN,
            toc=build_toc("index.html"), chapter=COURSE,
            prev=around("index.html")[0], next=around("index.html")[1],
            idx="—", total=TOTAL,
            body=open(cov, encoding="utf-8").read().rstrip())
        open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
        made.append("index.html")

    for c in sorted(PART_THEME):
        t, th = PART_THEME[c]
        p, n = around("part%s.html" % c)
        body = ('    <div class="part-open">\n'
                '      <h1><span class="part-no">%s부</span>%s</h1>\n'
                '      <p>%s</p>\n'
                '    </div>\n' % (c, t, th))
        body += '    <ul class="part-list">\n'
        for num, title, fn2, chap2 in FLAT:
            if num.split(".")[0] == c:
                body += '      <li><a href="%s"><b>%s장</b> %s</a></li>\n' % (fn2, num, title)
        body += '    </ul>\n'
        html = SHELL.format(
            num="%s부" % c, title=t, course=COURSE, course2=COURSE_2, meta=META,
            author=AUTHOR, written=WRITTEN,
            toc=build_toc("part%s.html" % c), chapter=COURSE,
            prev=p, next=n, idx="—", total=TOTAL, body=body)
        open(os.path.join(BASE, "part%s.html" % c), "w", encoding="utf-8").write(html)
        made.append("part%s.html" % c)

    pre = os.path.join(src_dir, "preface.html")
    if os.path.exists(pre):
        html = SHELL.format(
            num="머리말", title="값을 고치는 사람과 값을 읽는 사람",
            course=COURSE, course2=COURSE_2, meta=META,
            toc=build_toc("preface.html"), chapter="머리말", author=AUTHOR, written=WRITTEN,
            prev=around("preface.html")[0], next=around("preface.html")[1],
            idx="—", total=TOTAL,
            body=wrap_head(open(pre, encoding="utf-8").read().rstrip()))
        open(os.path.join(BASE, "preface.html"), "w", encoding="utf-8").write(html)
        made.append("preface.html")

    print("생성 완료 (%d):" % len(made), " ".join(made))
    if skipped:
        print("본문 없음 (%d):" % len(skipped), " ".join(skipped))


if __name__ == "__main__":
    main()
