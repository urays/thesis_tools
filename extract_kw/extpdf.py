# -*- encoding: utf-8 -*-

import re
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
# from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfinterp import PDFResourceManager, process_pdf


class PDF_Extractor(object):
    def __init__(self,
                 password='',
                 encoding='utf-8',
                 maxpages=2,
                 normalize_spaces=True,
                 caching=True,
                 detect_vertical=True,
                 char_margin=1.0,
                 line_margin=0.3,
                 word_margin=0.3):

        self.password = password
        self.encoding = encoding
        self.normalize_spaces = normalize_spaces
        self.caching = caching
        self.maxpages = maxpages

        self.laparams = LAParams()
        self.laparams.detect_vertical = detect_vertical
        self.laparams.char_margin = char_margin
        self.laparams.line_margin = line_margin
        self.laparams.word_margin = word_margin

    def extract(self, stream):
        outfp = StringIO()
        rsrcmgr = PDFResourceManager(caching=self.caching)
        device = TextConverter(rsrcmgr, outfp, laparams=self.laparams)

        process_pdf(
            rsrcmgr,
            device,
            stream,
            set(),
            maxpages=self.maxpages,
            password=self.password,
            caching=self.caching,
            check_extractable=True,
        )

        text = outfp.getvalue()
        outfp.close()
        if self.normalize_spaces:
            return re.sub(r'  +', ' ', text)
        else:
            return text


class extract_keywords():
    def __init__(self,
                 maxpages=2,
                 s_marks=["eywords—", "eywords-", "erms—", "erms-"],
                 e_marks=["."],
                 sepchar=[';', ','],
                 region=200,
                 maxchars=50,
                 maxcnt=10):
        self.maxpages = maxpages
        self.s_marks = s_marks
        self.e_marks = e_marks
        self.region = region
        self.maxchars = maxchars  # 一个 keyword 最多可能包含的字符数
        self.maxcnt = maxcnt
        self.sepchar = sepchar

    def search(self, paper):
        kws = []
        st = 0
        EXT = PDF_Extractor(maxpages=self.maxpages)
        with open(paper, 'rb') as stream:
            text = EXT.extract(stream)
            for x in self.s_marks:
                st = text.find(x)
                if st > 0:
                    st += len(x)
                    x = text[st:st + self.region]
                    # print(x)
                    kws = self.__deep_search(s="".join(x))
                    # print(kws)
                    break
        return kws

    def __deep_search(self, s):
        count = 0
        i = 0
        j, sj = i + 1, 0
        w = []
        ll = len(s)
        while count < self.maxcnt and j < ll:
            if j - i > self.maxchars:  # Inductive Logic Programming  Continuous Integration
                break
            if s[j] in self.sepchar:
                # print("----", s[i:j])
                w.append(s[i:j].replace('\n', ' ').strip())
                count += 1
                sj = j
                i = j + 1
            j += 1
        e = min([s[sj + 2:].find(x[0]) + x[1] for x in self.e_marks] + [ll - sj - 2])
        w.append(s[sj + 1:sj + e + 2].replace('\n', ' ').strip())
        return w
