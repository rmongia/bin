#!/usr/bin/python

# It updates the /etc/hosts file to add the mapping for the given hostnames.

import sys,httplib,time, hashlib, gzip

waittime_sec=0.1 # waittime between subsequent requests in seconds
corrupt_data_dir='/instart/log/corrupt_data/'

def is_utf8(data):
  try:
    d = data.decode('utf-8')
    if d: return True
  except UnicodeDecodeError:
    return False
  except Exception as e:
    print "Caught exception %s"%(str(e))

def is_gzip_utf8(filename):
  # Save the data to a temp file.
  # Read the data and try to unzip it
  # If unzip succeeds and data is still not utf-8, then it is possibly a
  # corruption
  try:
    fin = gzip.open(filename, 'rb')
    content = fin.read()
    fin.close()
    return is_utf8(content)
  except IOError as e:
    print "IOError: '%s' for file [%s]"%(str(e), filename)
  except Exception as e:
    print "Exception '%s' caught for file [%s]"%(str(e), filename)
  return False

def instart_cache_hit(req):
  # Checks whether request hit the instart cache.
  headers = req.getheaders()
  for h in headers:
   if h[0].lower().find("x-cache") >= 0:
    if h[1].lower().find("instart cache hit") >= 0:
      return True
  return False



# A method to try out a url using a given server
def test_url(url, server):
  new_url = url.lower()
  server = server.lower()
  is_http = False
  is_success = False
  scheme = "http"
  if new_url.startswith("http://"):
    is_http = True
  elif new_url.startswith("https://"):
    is_http = False
    scheme = "https"
  else:
    print "Bad URL: %s"%(url)
    return is_success
  #print "url:",url
  #print "server:",server
  host = (url.split("/"))[2]
  path = "/"
  if len (url.split("/")) > 3:
    path = url[ len(host) + len(scheme) + 3 : ]

  h1 = None
  if is_http:
    h1 =  httplib.HTTPConnection(server)
  else:
    h1 = httplib.HTTPSConnection(server)

  headers = {}
  headers["Host"] = host
# headers["User-Agent"] = "instart_python_url_tester"
  headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
  h1.request(method="GET", url=path, headers=headers)
  r1 = h1.getresponse()
  #print r1.status
  #print "path", path
  #print "headers", headers
  t = url.split("/")
  data = r1.read()
  '''
  if instart_cache_hit(r1):
    print "i-Cache-Hit", server, url
  else:
    print "NO i-Cache-Hit", server, url

  if not is_utf8(data):
    filename =corrupt_data_dir + server+url.replace("/",'').replace("?",'').replace(":",'')+str(time.time())+"_.corrupt.data"
    fout = open(filename, 'w')
    fout.write(data)
    fout.close()
    print "Not utf-8 data: " , server, url, "data written to", filename
    if is_gzip_utf8(filename):
      print "Gzip data:", server, url, filename
    else:
      print "Not gzip data:", server, url, filename
  '''
  m = hashlib.md5()
  m.update(data)
  md5sum = m.hexdigest()
  if r1.status >= 400:
    print "FAIL: ", r1.status, md5sum, server, url
  else:
    print "PASS: ", r1.status, md5sum, server, url
    is_success = True

  if h1:
    h1.close()

  return is_success


if len(sys.argv) != 3 :
  print "Usage:",sys.argv[0],"<urls_file> <servers_list_file>"
  print "A line beginning with # is conidered as a comment"
  sys.exit(1)

urls = open(sys.argv[1], 'r').readlines()
servers = open(sys.argv[2], 'r').readlines()

for u in urls:
  for s in servers:
    time.sleep(waittime_sec)
    server = s.strip()
    if server.startswith("#") or server == '':
      #print "Ignoring server line: ", server
      continue
    url = u.strip()
    if url.startswith("#") or url == '':
      #print "Ignoring url line: ", url
      continue
    try:
      test_url(url, server)
    except Exception as e:
      print "Exception %s occurred server %s url %s "% (str(e), server, url)
