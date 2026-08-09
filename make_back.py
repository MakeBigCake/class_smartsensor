#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""책 뒤쪽 찾아보기 생성
   index-terms.html  용어 색인
   index-figs.html   그림 · 표 색인
   index-abbr.html   약어 목록
   index-refs.html   참고문헌
"""
import re, os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from build import SHELL, FLAT, COURSE, COURSE_2, META, AUTHOR, WRITTEN, build_toc, around
from refdata import PUB, CAT_ORDER, CAT_DESC, ABBR

REF_POLICY = """    <p>각 장 끝의 참고자료는 두 종류다. <strong>관련 이미지</strong>는 제조사가 공개한 제품 페이지로
    실물 형상을 확인할 때 쓰고, <strong>근거 자료</strong>는 본문의 수치와 정의가 어디서 왔는지 확인할 때 쓴다.</p>
    <h4>관련 이미지 — 제조사 공개 자료</h4>
    <ul>
    <li><b>센서 · 안전 · 공압</b> — SICK, FESTO, Balluff, ifm, Banner, Panasonic, SANTEST</li>
    <li><b>제어기 · 구동 · 네트워크</b> — 미쓰비시전기 MELSEC, 지멘스, 보쉬렉스로스, 슈나이더일렉트릭</li>
    <li><b>로봇 · 충전</b> — 야스카와 모토맨, 뉴로메카, Xnergy</li>
    <li><b>기계 요소</b> — MISUMI</li>
    <li><b>통신 규격 단체</b> — IO-Link Community, OPC Foundation, ODVA, PLCopen</li>
    </ul>
    <p>제조사를 고를 때는 <strong>독일 · 일본 · 미국 · 유럽 순</strong>으로 찾고, 각 지역에서 상위 업체를 우선했다.
    국내 자료가 있으면 국내 페이지를 썼다.</p>

    <h4>근거 자료 — 표준 · 학술</h4>
    <ul>
    <li><b>IEC 60947-5-2</b> 근접 스위치 — 감지 원리 · 응차 · 반복 정밀도</li>
    <li><b>IEC 61496-1</b> 기계 안전 — 전기적 감지 보호 설비(ESPE)</li>
    <li><b>IEC 61131-9</b> SDCI(IO-Link) · <b>IEC 62541</b> OPC UA ·
    <b>IEC 62439-2/-3</b> 링 이중화(MRP · PRP/HSR) · <b>IEC 61784-2</b> CC-Link IE</li>
    <li><b>IEEE 1451</b> 스마트 트랜스듀서 인터페이스 · TEDS</li>
    <li><b>JCGM 200(VIM)</b> 국제 계량 용어집 — 감도 · 분해능 · 반복성의 표준 정의 (무료 공개)</li>
    <li><b>MDPI Sensors · PMC · arXiv</b> 오픈 액세스 논문 — 와전류 · 초음파 · 온도 보정</li>
    </ul>
    <p>표준 본문은 유료인 경우가 많아, 같은 내용을 무료로 확인할 수 있는 자료를 함께 달았다.</p>"""

CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
GROUP = {"ㄲ": "ㄱ", "ㄸ": "ㄷ", "ㅃ": "ㅂ", "ㅆ": "ㅅ", "ㅉ": "ㅈ"}


def head(w):
    c = w[0]
    if "가" <= c <= "힣":
        g = CHO[(ord(c) - 0xAC00) // 588]
        return GROUP.get(g, g)
    return c.upper() if c.isalpha() else "기타"


def collect():
    terms, refs, figs = [], [], []
    for num, title, fn, chap in FLAT:
        stem = fn[:-5]
        s = open(os.path.join(BASE, "content", fn), encoding="utf-8").read()
        for m in re.finditer(r'<dt id="([^"]+)">(.*?)</dt>\s*<dd>(.*?)</dd>', s, re.S):
            terms.append((re.sub(r"<[^>]+>", "", m.group(2)).strip(),
                          re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(3))).strip(),
                          num, stem, m.group(1)))
        for m in re.finditer(r'<div class="(fig|tbl)-label" id="([^"]+)">(.*?)</div>', s, re.S):
            raw = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(3))).strip()
            no, _, cap = raw.partition("·")
            figs.append(("그림" if m.group(1) == "fig" else "표",
                         no.strip(), cap.strip(), m.group(2), num))
        for li in re.findall(r"<li>(.*?)</li>", s, re.S):
            a = re.search(r'href="(https?://[^"]+)"[^>]*>(.*?)</a>', li, re.S)
            if not a:
                continue
            w = re.search(r'class="where">(.*?)</span>', li, re.S)
            refs.append((a.group(1),
                         re.sub(r"\s+", " ", re.sub("<[^>]+>", "", a.group(2))).strip(),
                         re.sub(r"\s+", " ", re.sub("<[^>]+>", "", w.group(1))).strip() if w else "",
                         num))
    return terms, refs, figs


def page(fn, num, title, body):
    open(os.path.join(BASE, fn), "w", encoding="utf-8").write(
        SHELL.format(num=num, title=title, course=COURSE, course2=COURSE_2, meta=META,
                     author=AUTHOR, written=WRITTEN,
                     toc=build_toc(fn), chapter="찾아보기",
                     prev=around(fn)[0], next=around(fn)[1],
                     idx="—", total=len(FLAT), body=body))
    print("생성:", fn)


def main():
    terms, refs, figs = collect()
    nf = len([f for f in figs if f[0] == "그림"]); nt = len([f for f in figs if f[0] == "표"])
    print("수집: 용어 %d · 참고 %d · 그림 %d · 표 %d" % (len(terms), len(refs), nf, nt))
    if not (terms and refs and nf and nt):
        sys.exit("★ 색인 추출 실패 — 본문 마크업과 정규식이 어긋났습니다.")

    # ---------- 용어 색인 ----------
    uniq = {}
    for dt, dd, num, stem, aid in terms:
        uniq.setdefault(dt, {"dd": dd, "at": []})["at"].append((num, stem, aid))
    buckets = {}
    for w in sorted(uniq, key=lambda x: (head(x), x)):
        buckets.setdefault(head(w), []).append(w)
    order = [c for c in CHO if c in buckets and c not in GROUP]
    order += sorted(k for k in buckets if k not in order)

    b = ['    <div class="lesson-tag">찾아보기</div>', "    <h1>용어 색인</h1>",
         '    <p class="subtitle">이 책에 나오는 용어 %d개 — 초성순</p>' % len(uniq),
         '    <p class="lead" style="font-size:14.5px">항목 오른쪽의 장 번호를 누르면 그 용어를 설명한 자리로 바로 이동한다. '
         '여러 장에 나오는 용어는 장마다 따로 걸려 있다.</p>',
         '    <div class="idx-nav">' + " ".join('<a href="#g%d">%s</a>' % (i, c) for i, c in enumerate(order)) + "</div>"]
    for i, c in enumerate(order):
        b += ['    <section class="sec" id="g%d">' % i, '      <div class="sec-no">%s</div>' % c,
              '      <dl class="terms idx">']
        for w in buckets[c]:
            d = uniq[w]
            at = " · ".join('<a href="%s.html#%s">%s</a>' % (st, aid, n) for n, st, aid in d["at"])
            b += ['        <dt>%s<span class="idx-at">%s</span></dt>' % (w, at),
                  "        <dd>%s</dd>" % d["dd"]]
        b += ["      </dl>", "    </section>"]
    page("index-terms.html", "색인", "용어 색인", "\n".join(b))

    # ---------- 그림 색인 · 표 색인 (분리) ----------
    def make_list(kind, fn, title, desc):
        items = [f for f in figs if f[0] == kind]
        b = ['    <div class="lesson-tag">찾아보기</div>', "    <h1>%s</h1>" % title,
             '    <p class="subtitle">%s %d개 — 장 순서</p>' % (kind, len(items)),
             '    <p class="lead" style="font-size:14.5px">%s</p>' % desc]
        for num, t, _fn, _chap in FLAT:
            mine = [f for f in items if f[4] == num]
            if not mine:
                continue
            b += ['    <section class="sec">', '      <div class="sec-no">%s장 · %s</div>' % (num, t),
                  '      <ul class="idx-list">']
            for _k, no, cap, aid, _ in mine:
                b.append('        <li><a href="%s.html#%s"><span class="no">%s</span>%s</a></li>'
                         % (num.replace(".", "-"), aid, no, cap))
            b += ["      </ul>", "    </section>"]
        page(fn, "색인", title, "\n".join(b))

    NUMDESC = ('번호는 <b>장 번호 + 그 장에서의 순번</b>이다. 예를 들어 <b>%s</b>는 1.1장의 세 번째 %s를 '
               '뜻하며, 절 번호와는 무관하다. 제목을 누르면 해당 자리로 이동한다.')
    make_list("그림", "index-figs.html", "그림 색인", NUMDESC % ("그림 1.1-3", "그림"))
    make_list("표", "index-tables.html", "표 색인", NUMDESC % ("표 1.1-3", "표"))

    # ---------- 약어 목록 ----------
    body_all = " ".join(re.sub("<[^>]+>", " ", open(os.path.join(BASE, "content", fn), encoding="utf-8").read())
                        for _, _, fn, _ in FLAT)
    b = ['    <div class="lesson-tag">찾아보기</div>', "    <h1>약어 목록</h1>",
         '    <p class="subtitle">이 책에 나오는 약어 %d개</p>' % len(ABBR),
         '    <p class="lead" style="font-size:14.5px">본문은 현장에서 쓰는 표기를 그대로 따르므로 약어가 자주 나온다. '
         '정식 명칭이 필요할 때 여기서 찾는다.</p>',
         '    <section class="sec">', '      <div class="sec-no">가나다 · 알파벳순</div>',
         "      <table>", "        <thead>",
         "          <tr><th>약어</th><th>정식 명칭</th><th>뜻</th></tr>",
         "        </thead>", "        <tbody>"]
    for a, full, kor in ABBR:
        b.append("          <tr><td>%s</td><td style=\"font-size:12.5px\">%s</td><td>%s</td></tr>" % (a, full, kor))
    b += ["        </tbody>", "      </table>", "    </section>"]
    page("index-abbr.html", "색인", "약어 목록", "\n".join(b))

    # ---------- 참고문헌 ----------
    byurl = {}
    for url, title, where, num in refs:
        e = byurl.setdefault(url, {"title": title, "where": where, "at": []})
        if num not in e["at"]:
            e["at"].append(num)
    cats = {}
    for url, e in byurl.items():
        d = re.sub(r"^www\.", "", url.split("/")[2])
        name, cat = PUB.get(d, (d, "해설"))
        cats.setdefault(cat, {}).setdefault(name, []).append((url, e))

    b = ['    <div class="lesson-tag">찾아보기</div>', "    <h1>참고문헌</h1>",
         '    <p class="subtitle">이 책이 인용한 외부 자료 %d건</p>' % len(byurl),
         '    <div class="note">',
         '      <span class="t">개념 · 이 목록을 정리한 방식</span>',
         "      <p><b>자료의 종류</b>로 먼저 나누고, 그 안에서 <b>발행처 이름순</b>으로 배열했다. "
         "규격을 찾을 때는 맨 앞 「국제 표준」 묶음을, 특정 제조사의 자료를 찾을 때는 「제조사 기술자료」 묶음에서 "
         "회사 이름으로 찾으면 된다.</p>",
         "      <p style=\"margin-bottom:0\">각 항목 끝의 장 번호는 그 자료를 <b>인용한 자리</b>다. 누르면 해당 장으로 이동한다. "
         "무료로 볼 수 있는 자료를 우선했으며, 유료 규격은 미리보기나 발췌본을 함께 실었다.</p>",
         "    </div>",
         '    <section class="sec">',
         '      <h2>자료를 고른 기준<span class="en">무엇을 근거로 삼았는가</span></h2>',
         REF_POLICY,
         "    </section>"]
    for cat in CAT_ORDER:
        if cat not in cats:
            continue
        title, desc = CAT_DESC[cat]
        n = sum(len(v) for v in cats[cat].values())
        b += ['    <section class="sec">', '      <div class="sec-no">%s · %d건</div>' % (cat, n),
              "      <h2>%s</h2>" % title, '      <p class="lead" style="font-size:14.5px">%s</p>' % desc]
        for name in sorted(cats[cat], key=lambda x: (0 if x[0].isascii() else 1, x.lower())):
            b += ["      <h3>%s</h3>" % name, '      <ol class="linklist">']
            for url, e in sorted(cats[cat][name], key=lambda x: x[1]["title"]):
                at = " · ".join('<a href="%s.html">%s</a>' % (x.replace(".", "-"), x) for x in e["at"])
                b += ["        <li>",
                      '          <a href="%s" target="_blank" rel="noopener">%s</a>' % (url, e["title"]),
                      '          <span class="where">인용 %s</span>' % at, "        </li>"]
            b += ["      </ol>"]
        b += ["    </section>"]
    page("index-refs.html", "참고문헌", "참고문헌", "\n".join(b))


if __name__ == "__main__":
    main()
