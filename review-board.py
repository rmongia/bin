import json
import os
import urllib, urllib2, cookielib, base64

REVIEWBOARD_URL="https://reviewboard.insnw.net"

class RB:
  def __init__(self):
    path = os.path.expanduser('~/.post-review-cookies.txt')
    cj  = cookielib.MozillaCookieJar(path)

    if path:
        try:
            cj.load(path, ignore_expires=True)
        except IOError:
            pass

    http_handler = urllib2.HTTPSHandler(debuglevel=0)
    self.opener = urllib2.build_opener(
        urllib2.HTTPCookieProcessor(cj),
        http_handler)
    self.username = 'rmongia'

  def login(self, password):
    request = urllib2.Request('%s/api/users/%s/' % (
      REVIEWBOARD_URL,
      self.username))
    base64string = base64.encodestring('%s:%s' % (
      self.username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    self.opener.open(request)

  def request(self, url, method='GET', data=None):
    if data:
      data = urllib.urlencode(data)
    request = urllib2.Request('%s%s' % (REVIEWBOARD_URL, url), data)
    request.get_method = lambda: method
    return self.opener.open(request)

  def review_comment(self, id):
    res = self.request('/api/review-requests/%s/reviews/' % id)
    res_obj = json.loads(res.read())
    comment = []
    for r in res_obj['reviews']:
      comment.append('%s(%s)' % (r['links']['user']['title'], r['body_top']))
    return ','.join(comment)

  def all_open_reviews(self):
    res = self.request('/api/review-requests/?from-user=%s&status=pending' % self.username)
    json_obj = json.loads(res.read())
    for r in json_obj['review_requests']:
      review_comment = self.review_comment(r['id'])
      print r['id'], r['last_updated'], r['summary'], '|', review_comment

  def all_shipped_open_reviews(self):
    res = self.request('/api/review-requests/?from-user=%s&ship-it=1&status=pending' % self.username)
    json_obj = json.loads(res.read())
    for r in json_obj['review_requests']:
      review_comment = self.review_comment(r['id'])
      print r['id'], r['last_updated'], r['summary'], '|', review_comment

  def close_review(self, id):
    r = json.loads(self.request(
        '/api/review-requests/%s/' % id,
        data={'status':'submitted'},
        method='PUT').read())
    print "Closed", r['review_request']['summary'], r['stat']

if __name__ == '__main__':
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("-o", "--open",
      action="store_true",
      dest="open",
      default=False)
  parser.add_option("-c", "--close", dest="close")
  parser.add_option("-p", "--password", dest="password")

  (options, args) = parser.parse_args()

  rb = RB()
  rb.login(options.password)
  if options.open:
    rb.all_open_reviews()
  elif options.close is None:
    rb.all_shipped_open_reviews()
  else:
    for c in options.close.split(','):
      rb.close_review(c)
