# coding=utf-8
import re
import random
import sys
import getUID
import subprocess
import os
import cgi
import gzip
import json
import time

from jinja2 import Environment, FileSystemLoader
from os import listdir
from os.path import isfile, join


class Count:
    def __init__(self):
        self.number = 1
        self.indexes = []
        self.last_use = ""

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

class Main:
    def __init__(self, path):
        self.env = Environment(loader=FileSystemLoader('/var/www/templates'))
        self.template = self.env.get_template('template.html')
        self.file = None
        self.most_active = {}
        # per user statistics
        self.user_question = {}
        self.user_exclamation = {}
        self.user_actions = {}
        self.user_givemodes = {}
        # total statistics
        self.total_question = Count()
        self.total_exclamation = Count()
        self.total_actions = Count()
        self.total_givemodes = Count()
        self.activity_graph = [0]*24
        # urls
        self.urls = {}
        self.path = path
        self.name = path.split("/")[-1]
        self.file = []
        self.onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

    def bulk_lines(self):
        def test_if_gz(filename):
            if (filename.split(".")[::-1][0] == "gz"):
                # print("gz")
                return gzip.open("%s/%s" % (sys.argv[1], filename))
            else:
                # print("log")
                return open("%s/%s" % (sys.argv[1], filename))
        for filename in self.onlyfiles:
            lines = (line.rstrip('\n') for line in test_if_gz(filename))
            for index, line in enumerate(lines):
                self.one_line(line, index, filename)

    def one_line(self, line, n, filename):
        index = n
        line = line
        filename = filename
        if len(line) < 7:
            return None

        if line[6] == "-":
            m = re.match("\d{2}:\d{2}\s-!-\smode/#\w+\s\[(.{2})\s(.+)\].*", line)
            self.total_givemodes.number += 1
            try:
                if m.group(2) in self.user_givemodes:
                    self.user_givemodes[m.group(2)].number += 1
                    self.user_givemodes[m.group(2)].indexes += [n]
                else:
                    self.user_givemodes.update({m.group(2): Count()})
                    self.user_givemodes[m.group(2)].indexes += [n]
            except AttributeError:
                return None

        if line[6] == "<":
            m = re.match("\d{2}:\d{2}\s<(\W|\s)(.*)>\s(.*)", line)
            url_r = re.findall("(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)", line)
            time = re.match("(\d{2}:\d{2})", line);

            if not(m.group(2) == "TheKubaX"):
                try:
                    time = time.group(1).split(":")[0]
                    self.activity_graph[int(time)] += 1
                except AttributeError:
                    pass
                try:
                    for i in url_r:
                        if i in self.urls:
                            self.urls[i].number += 1
                            self.urls[i].last_use = m.group(2)
                        else:
                            self.urls.update({i: Count()})
                            self.urls[i].last_use = m.group(2)
                except AttributeError:
                    pass
                try:
                    try:
                        if "!" == m.group(3)[0]:
                            return None
                    except IndexError:
                        pass
                    if "!" in m.group(3):
                        self.total_exclamation.number += 1
                        if m.group(2) in self.user_exclamation:
                            self.user_exclamation[m.group(2)].number += 1
                            self.user_exclamation[m.group(2)].indexes += [n]
                        else:
                            self.user_exclamation.update({m.group(2): Count()})
                            self.user_exclamation[m.group(2)].indexes += [n]
                    if "?" in m.group(3):
                        self.total_question.number += 1
                        if m.group(2) in self.user_question:
                            self.user_question[m.group(2)].number += 1
                            self.user_question[m.group(2)].indexes += [n]
                        else:
                            self.user_question.update({m.group(2): Count()})
                            self.user_question[m.group(2)].indexes += [n]
                    if m.group(2) in self.most_active:
                        self.most_active[m.group(2)].number += 1
                        self.most_active[m.group(2)].indexes += [n]
                    else:
                        self.most_active.update({m.group(2): Count()})
                        self.most_active[m.group(2)].indexes += [n]
                except AttributeError:
                    return None
            else:
                pass

        if line[6] == " ":
            m = re.match("\d{2}:\d{2}\s{2}\*\s([^\s]+)\s(.*)", line)
            self.total_actions.number += 1
            try:
                if m.group(1) in self.user_actions:
                    self.user_actions[m.group(1)].number += 1
                    self.user_actions[m.group(1)].indexes += [n]
                else:
                    self.user_actions.update({m.group(1): Count()})
                    self.user_actions[m.group(1)].indexes += [n]
            except AttributeError:
                return None

    def get_most_active(self):
        keys = self.most_active.keys()
        my_x = {}
        for i in keys:
            my_x.update({i: self.most_active[i].number})
        return sorted(my_x, key=my_x.get)[::-1][:25]

    def get_runner_ups_active(self):
        keys = self.most_active.keys()
        my_x = {}
        for i in keys:
            my_x.update({i: self.most_active[i].number})
        try:
            return sorted(my_x, key=my_x.get)[::-1][25:35]
        except IndexError:
            return sorted(my_x, key=my_x.get)[::-1][25:]

    def get_random_line(self, nick):
        mine = u""
        with cd(sys.argv[1]):
            base = "<\W%s>" % re.escape(nick)
            user_input = "zgrep \"%s\" * | shuf -n 1" % base
            mine = subprocess.Popen("%s" % user_input, shell=True, stdout=subprocess.PIPE).stdout.read()[20:].decode("utf-8")
        return mine[3:]
        

    def save_page(self):
        my_keys = self.get_most_active()
        most_active = []
        for i in my_keys:
            item = self.most_active[i]
            uid = getUID.GetUID(i).uid
            most_active += [(i, item.number, cgi.escape(self.get_random_line(i)), uid)]
        runner_ups = self.get_runner_ups_active()

        def get_contents(what):
            keys = what.keys()
            my_x = {}
            for i in keys:
                my_x.update({i: what[i].number})
            # print(sorted(my_x, key=my_x.get)[::-1][:2])
            get_who = lambda n: sorted(my_x, key=my_x.get)[::-1][:2][n] 
            return [(get_who(0), what[get_who(0)].number), (get_who(1), what[get_who(1)].number)]
        
        # graph percentage calculation
        sum = 0
        for i in self.activity_graph:
            sum += i
        sum = sum/240.0
        for i in xrange(0, 24):
            self.activity_graph[i] = int(self.activity_graph[i]) # int(self.activity_graph[i]/sum)
        
        self.screaming = get_contents(self.user_exclamation)
        self.asking = get_contents(self.user_question)
        self.telling = get_contents(self.user_actions)
        self.modding = get_contents(self.user_givemodes)
        being = {"screaming": self.screaming, "asking": self.asking, "telling": self.telling, "modding": self.modding}

        keys = self.urls.keys()
        my_x = {}

        for i in keys:
            my_x.update({i: self.urls[i].number})
        my_keys = sorted(my_x, key=my_x.get)[::-1][:10]
        most_urls = []
        for i in my_keys:
            item = self.urls[i]
            most_urls += [(i, item.number, item.last_use)]

        total_num = [self.total_question.number, self.total_exclamation.number, self.total_actions.number, self.total_givemodes.number]

        output_from_parsed_template = self.template.render(name=self.name,
            most_active=most_active, runner_ups=runner_ups, being=being,
            urls_used=most_urls, total=total_num, activity_graph=self.activity_graph) # All necessary variables goes here

        with open("/var/www/alltime/%s.html" % self.name, "wb") as fh:
            fh.write(output_from_parsed_template.encode("utf-8"))
        with open("/var/www/alltime/json/%s.json" % self.name, "w") as fh:
            json.dump(
                {"name": self.name, "total_numbers": total_num, "most_active": most_active,
                "runner_ups": runner_ups, "being": being, "most_used_urls": most_urls,
                "activity_graph": self.activity_graph}, fh)


start_time = time.time()

a = Main(str(sys.argv[1]))
a.bulk_lines()
a.save_page()

print("%s --- %s seconds ---" % (a.name, (time.time() - start_time)))
