import urllib2, urllib, json, sys, html5lib, os, unicodedata, string
from pprint import pprint
from xml.etree import ElementTree as ET

def content(tag):
    return tag.text + u''.join(ET.tostring(e) for e in tag)


def parentchild (tree):
    for parent in tree.getiterator():
        for child in parent:
            yield parent, child


def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters).lower()

API = "http://pzwart3.wdka.hro.nl/mediawiki/api.php"
qvars = {
    'action': 'ask',
    'query':'''{{#ask:[[Category:Grad project]]
|?#
|?Student
|?Project
|?Year
|?Featured image
|?Project
|?Bio
|?Bio URL
|?Project URL
|format=jsonfm
|link=all
}}''',
    'format': 'json'
}
qurl = API + "?" + urllib.urlencode(qvars)
data = json.load(urllib2.urlopen(qurl))
metadata = {}
def unwrap (l):
    if len(l):
        l = l[0]
        if type(l) == dict:
            return l['fulltext']
        return l

for title in data['query']['results']:
    d = {}
    metadata[title] = d
    for key, value in data['query']['results'][title]['printouts'].items():
        # print "\t", key, unwrap(value)
        d[key] = unwrap(value)

qvars = {
    'action': 'query',
    'list':'categorymembers',
    'cmtitle': 'Category:Grad project',
    'format': 'json',
    'cmlimit': 500
}
qurl = API + "?" + urllib.urlencode(qvars)
data = json.load(urllib2.urlopen(qurl))

for item in data['query']['categorymembers']:
    title = item['title']
    qvars = {
        'action': 'parse',
        'pageid': item['pageid'],
        'format': 'json'
    }
    qurl = API + "?" + urllib.urlencode(qvars)
    data = json.load(urllib2.urlopen(qurl))
    # pprint(data)
    src = data['parse']['text']['*']
    tree = html5lib.parseFragment(src, namespaceHTMLElements=False)
    kill = []
    for parent, child in parentchild(tree):
        if child.tag == "table" or child.tag == ET.Comment:
            kill.append((parent, child))
    for p, c in kill:
        p.remove(c)

    md = metadata[title]

    fpath = remove_accents(md.get("Student").lower().replace(" ", "_"))
    fpath = os.path.join("_posts", "2014-05-12-"+fpath+".html")
    with open(fpath, "w") as f:
        out = u"---\n"
        keys = md.keys()
        keys.sort()
        for k in keys:
            if md[k]:
                out += u'{0}: "{1}"\n'.format(k.lower().replace(" ", "-"), md[k].replace("\"", "'"))
        out += u"---\n\n"
        out += content(tree)
        print fpath
        f.write(out.encode("utf-8"))

