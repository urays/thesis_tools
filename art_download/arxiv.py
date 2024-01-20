# -*- coding: UTF-8 -*- 
import requests
import threading

def Handler(start, end, url, filename): 
    # specify the starting and ending of the file 
    headers = {'Range': 'bytes=%d-%d' % (start, end)} 
    # request the specified part and get into variable     
    r = requests.get(url, headers=headers, stream=True) 
    # open the file and write the content of the html page into file. 
    with open(filename, "r+b") as fp: 
        fp.seek(start) 
        var = fp.tell() 
        fp.write(r.content)

def arxiv_download(url_of_file,name,number_of_threads=4): 
    print("url:", url_of_file)
    r = requests.head(url_of_file) 
    if name: 
        file_name = name 
    else: 
        file_name = url_of_file.split('/')[-1] 
    try: 
        file_size = int(r.headers['content-length']) 
    except: 
        print("Invalid URL")
        return 0

    part = int(file_size) / number_of_threads 
    fp = open(file_name, "wb") 
    fp.close() 
    for i in range(number_of_threads): 
        start = int(part * i) 
        end = int(start + part) 
        # create a Thread with start and end locations 
        t = threading.Thread(target=Handler, 
            kwargs={'start': start, 'end': end, 'url': url_of_file, 'filename': file_name}) 
        t.setDaemon(True) 
        t.start() 

    main_thread = threading.current_thread() 
    for t in threading.enumerate(): 
        if t is main_thread: 
            continue
        t.join() 
    return 1