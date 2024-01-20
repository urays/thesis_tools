# -*- coding: UTF-8 -*- 
import re
import os
from arxiv import arxiv_download
from scihub import scihub_download
import requests
import traceback
from PyPDF2 import PdfFileReader

def parser_readme(path):
    S = {}
    sname = ""
    with open(path, "r") as f:
        ctx = f.readlines()
        f = 0
        for line in ctx:
            if line.startswith('###'):
                f = 1
                sname = line.strip('#').strip()
                S[sname] = {}
            elif line.startswith('#'):
                f = 0
            if f == 1:
                #print(line)
                pa1 = re.compile("- \[(.*)\]")
                pa2 = re.compile("\((http.*)\)")
                res1 = pa1.findall(line)
                res2 = pa2.findall(line)
                if len(res1):
                    #print(res1, res2)
                    S[sname][res1[0]] = res2[0]
    return S

def isValidPDF_pathfile(pathfile):
    bValid = True
    try:
        reader = PdfFileReader(pathfile)
        if reader.getNumPages() < 1:   
            bValid = False
    except:
        bValid = False
        print('*' + traceback.format_exc())
        
    return bValid

def normal_download(url, filename): 
    try:
        # request the specified part and get into variable     
        r = requests.get(url, stream=True) 
        # open the file and write the content of the html page into file. 
        with open(filename, "wb") as fp: 
            fp.write(r.content)
    except:
        print("@")

#https://www.usenix.org/conference/osdi18/presentation/chen
#https://www.usenix.org/system/files/osdi18-chen.pdf

S = parser_readme("1.md")
f = open("not_found.md", "w")
for k, v in S.items():
    f.write("### " + k + "\n")
    if not os.path.exists(k):
        os.mkdir(k)
    for paper, url in v.items():
        paper = re.sub("[^a-z^A-Z^0-9 ]", "", paper)
        print(paper, url) 
        paper_path = os.path.join(k, paper + ".pdf")
        if os.path.exists(paper_path):
            if not isValidPDF_pathfile(paper_path):
                os.remove(paper_path)
            else:
                print("Alreadly existed.")
                continue
        if "arxiv" in url:
            pdf_url = url.replace('abs', 'pdf') + ".pdf"
            arxiv_download(pdf_url, paper_path)
        elif "dl.acm.org" in url:
            if "abs" in url:
                pdf_url = url.replace('abs', 'pdf')
                normal_download(pdf_url, paper_path)
        elif url.strip().lower().endswith(".pdf"):
            normal_download(url, paper_path)
        elif "https://www.usenix.org/" in url:
            L = url.split('/')
            pdf_url = "https://www.usenix.org/system/files/" +L[-3] +"-" + L[-1] + ".pdf"
            normal_download(pdf_url, paper_path)
        if not os.path.exists(paper_path):
            if scihub_download(url, paper_path) == 0:
                scihub_download(paper, paper_path)
        if not os.path.exists(paper_path):
            f.write("- [" + paper + "](" + url + ")\n")
            f.flush()
            print("not found.")
        elif not isValidPDF_pathfile(paper_path):
            os.remove(paper_path)
            f.write("- [" + paper + "](" + url + ")\n")
            f.flush()
            print("not found.")
    f.write("\n")
f.close()
