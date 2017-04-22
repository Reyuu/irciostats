# coding=utf-8
import re
import urllib2
import urllib

class GetUID:
    def __init__(self, nick):
        nick = urllib.quote_plus(nick)
        self.url = "https://osu.ppy.sh/u/%s" % nick
        self.nick = nick
        cache_check = self.check_cache()
        if not(cache_check):
            self.webpage = self.get_webpage()
            self.uid = self.get_uid()
        if cache_check:
            self.webpage = ""
            self.uid = cache_check
        self.cache_outcome()

    def get_webpage(self):
        return urllib2.urlopen(self.url).read()

    def get_uid(self):
        try:
            return re.search(r"var\suserId\s=\s(\d+);", self.webpage).group(1)
        except AttributeError:
            return str(-1)

    def check_cache(self):
        cache = []
        try:
            with open("cache", "r") as h:
                cache = h.read().split("\n")
        except IOError:
            open("cache", 'a').close()

        cache_d = {}
        for i in xrange(len(cache)):
            try:
                cache_d.update({cache[i].split(":")[0]: cache[i].split(":")[1]})
            except IndexError:
                pass

        if self.nick in cache_d.keys():
            return cache_d[self.nick]
        return False

    def cache_outcome(self):
        formatted_text = "%s:%s" % (self.nick, self.uid)
        try:
            with open("cache", "r") as h:
                cache = h.read().split("\n")
        except IOError:
            open("cache", 'a').close()
            cache = []

        if not(formatted_text in cache):
            with open("cache", "a") as f:
                f.write("%s\n" % formatted_text)
