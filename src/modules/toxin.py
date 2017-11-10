#!/usr/bin/python3
# -*- coding: latin-1 -*-
# This file is part of v3n0m
# See LICENSE for license details.


try:
    import re, random, threading, socket, urllib.request, urllib.error, urllib.parse, http.cookiejar, subprocess, \
        time, sys, os, math, itertools, queue, asyncio, aiohttp, argparse, socks, httplib2, requests, codecs
    from signal import SIGINT, signal
    import pprint
    from aiohttp import ClientSession
    from codecs import lookup, register
    from random import SystemRandom
    import ftplib, tqdm
    from ftplib import FTP
    from os import getpid, kill, path
    from sys import argv, stdout
    from random import randint
    from aiohttp import web
    import async_timeout

except:
    exit()


def killpid(signum=0, frame=0):
    print("\r\x1b[K")
    os.kill(os.getpid(), 9)


W = "\033[0m"
R = "\033[31m"
G = "\033[32m"
O = "\033[33m"
B = "\033[34m"
msf_Vulns = [line.strip() for line in open("lists/vuln-ftp-checklist.txt", 'r')]
global LoadedIPCache


def banner():
    print('''       NovaCygni's
        .---..----..-..-..-..-..-.
        `| |'| || | >  < | || .` |
         `-' `----''-'`-``-'`-'`-'
           V3n0M Metasploitable Scanner Version 0.1.2

    ''')



class IPChecker:
    """A class to check if an IP is in a range of IPs"""
    ipdict = {}
    fulls = [{}, {}, {}]

    def __init__(self):
        # Create dictionaries for rest of ip sequences for caching
        for i in range(0, 256):
            self.fulls[0][i] = True
        for i in range(0, 256):
            self.fulls[1][i] = self.fulls[0]
        for i in range(0, 256):
            self.fulls[2][i] = self.fulls[1]

    def loadIPs(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            i = 0
            for line in f:
                i += 1
                try:
                    ip = line.split("#")[0].strip()
                except:
                    raise ValueError("Error while parsing line: \"" + line + "\"")
                if len(ip) == 0:
                    continue
                if not re.match("^[0-9\*-]+\.[0-9\*-]+\.[0-9\*-]+\.[0-9\*-]+$", ip):
                    raise ValueError("Error in format while parsing line: \"" + line + "\"")
                added = self.addIP(ip)
                if added != 0:
                    raise ValueError(str(added) + ": Error while parsing IP on line: \"" + line + "\"")

    def generateValidIP(self):
        ip = ""
        curdict = self.ipdict
        for i in range(0,4):
            randip = randint(0,255)
            while (randip in curdict.keys()) and ((i!=3 and (len(curdict[randip].keys())>=255)) or i==3):
                randip = randint(0,255)
            if randip in curdict.keys():
                curdict = curdict[randip]
            else:
                curdict = {}
            ip += str(randip)
            if i!=3:
                ip += "."
            else:
                ip += ""
        return ip

    def addIP(self, ipstr):
        parts = re.findall("[0-9\*-]+", ipstr)
        return self.addFirstPart(self.ipdict, parts)

    def addFirstPart(self, partDict, parts):
        if parts[0] == "*":
            return self.addRange(partDict, parts, 0, 255)
        elif len(parts[0].split("-")) == 2:
            first = int(parts[0].split("-")[0])
            second = int(parts[0].split("-")[1])
            return self.addRange(partDict, parts, first, second)
        elif len(parts[0].split("-")) == 1:
            only = int(parts[0])
            return self.addRange(partDict, parts, only)
        else:
            return -1

    def addRange(self, partDict, parts, first, second=-1):
        if second == -1:
            second = first
        if not first in partDict.keys():
            nextDict = {}
        else:
            nextDict = partDict[first]
        for i in range(first, second + 1):
            if not i in partDict.keys():
                partDict[i] = nextDict
            elif first != second:
                return -2
            if len(parts) != 1:
                rest = True
                for j in range(0, len(parts)):
                    if parts[j] != "*":
                        rest = False
                if rest:
                    partDict[i] = self.fulls[len(parts) - 1]
                else:
                    self.addFirstPart(partDict[i], parts[1:])
            else:
                partDict[i] = True
        return 0

    def checkIP(self, ip):
        if not re.match("^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$", ip):
            raise ValueError("Error in format while parsing ip: " + str(ip))
        parts = re.findall("[0-9]+", ip)
        parts[0] = int(parts[0])
        parts[1] = int(parts[1])
        parts[2] = int(parts[2])
        parts[3] = int(parts[3])
        if parts[0] in self.ipdict:
            if parts[1] in self.ipdict[parts[0]]:
                if parts[2] in self.ipdict[parts[0]][parts[1]]:
                    if parts[3] in self.ipdict[parts[0]][parts[1]][parts[2]]:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False


def makeips(amount):
    IPList = []
    c = IPChecker()
    # Path to Honeypot file with IP's and Ranges that should NOT be generated. Only a retard wouldnt do this!
    c.loadIPs("lists/honeypot_ranges.txt")
    amt = int(amount)
    ping = ping_checker()
    a_holder = int(amt / 10)
    b_holder = 0
    global c_holder
    c_holder = 0
    while b_holder <= amt:
        for i in range(0, a_holder):
            ip = c.generateValidIP()
            try:
                assert (c.checkIP(ip) == False)
                b_holder += 1
            except:
                print(ip + " Failed to generate")
                b_holder -= 1
                raise
            IPList.append(ip)
    print("Ips Generated That are online: " + str(len(IPList) - a_holder))
    print("[1] Save IP addresses to file")
    print("[2] Print IP addresses")
    print("[3] Return to Toxins Menu")
    print("[4] Setup Port specific attacks")
    print("[0] Exit Toxin Module")
    # Create a secondry Log file for working with without corrupting main IP List.
    log = "IPLogList.txt"
    logfile = open(log, "a")
    for t in IPList:
        logfile.write(t + "\n")
    logfile.close()
    chce = input("Option: ")
    if chce == '1':
        print("Save IP addresses?")
        listname = input("Filename: ")
        try:
            print("Saving valid Ip Addresses")
            list_name = open(listname, "a")
            IPList.sort()
            for t in IPList:
                list_name.write(t + "\n")
            list_name.close()
            print("Urls saved, please check", listname)
        except:
            print("Failed to save")
    if chce == '2':
        pp = pprint.PrettyPrinter(width=68, compact=True)
        pp.pprint(IPList)
        print("Do you wish to start Toxin again or Exit to V3n0M")
        print("[1] Stay within Toxin")
        print("[2] Exit to V3n0M")
        chc = input("Option: ")
        if chc == '1':
            menu()
        if chc == '2':
            exit()
    if chce == '3':
        menu()
    if chce == '4':
        print("[1] Launch FTP Checks")
        print("[0] Exit")
        choice = input("Which Option:")
        if choice == '1':
            in_a_loop = asyncio.get_event_loop()
            in_a_loop.run_until_complete(main(in_a_loop))
        if choice == '0':
            exit()
    if chce == '0':
        exit()


class CoroutineLimiter:
        """
        If `invoke_as_tasks` is true, wrap the invoked coroutines in Task
        objects. This will ensure ensure that the coroutines happen in the
        same order `.invoke()` was called, if the tasks are given
        to `asyncio.gather`.
        """

        def __init__(self, limit, *, loop=None, invoke_as_tasks=False):
            if limit <= 0:
                raise ValueError('Limit must be nonzero and positive')
            if loop is None:
                loop = asyncio.get_event_loop()
            self._loop = loop
            self._sem = asyncio.Semaphore(limit, loop=loop)
            self._count = itertools.count(1)
            self._invoke_as_tasks = invoke_as_tasks

        def invoke(self, coro_callable, *args):
            coro = self._invoke(coro_callable, *args)
            if self._invoke_as_tasks:
                return self._loop.create_task(coro)
            else:
                return coro

        async def _invoke(self, coro_callable, *args):
            n = next(self._count)
            fmt = 'Acquiring semaphore for coroutine {count} with args {args}'
            print(fmt.format(count=n, args=args))
            await self._sem.acquire()
            fmt = 'Semaphore acquired. Invoking coroutine {count} with args {args}'
            print(fmt.format(count=n, args=args))
            try:
                return await coro_callable(*args)
            finally:
                print('Coroutine {count} finished, releasing semaphore'.format(
                    count=n,
                ))
                self._sem.release()


class ping_checker(object):
    status = {'alive': [], 'dead': []}  # Populated while we are running
    hosts = []  # List of all hosts/ips in our input queue

    # How many ping process at the time.
    thread_count = 1

    # Lock object to keep track the threads in loops, where it can potentially be race conditions.
    lock = threading.Lock()

    def ping(self, ip):
        # Use the system ping command with count of 1 and wait time of 1.
        ret = subprocess.call(['ping', '-c', '1', '-W', '1', ip],
                              stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))

        return ret == 0  # Return True if our ping command succeeds

    def pop_queue(self):
        ip = None

        self.lock.acquire()  # Grab or wait+grab the lock.

        if self.hosts:
            ip = self.hosts.pop()

        self.lock.release()  # Release the lock, so another thread could grab it.

        return ip

    def dequeue(self):
        while True:
            ip = self.pop_queue()

            if not ip:
                return None

            result = 'alive' if self.ping(ip) else 'dead'
            self.status[result].append(ip)

    def start(self):
        threads = []

        for i in range(self.thread_count):
            # Create self.thread_count number of threads that together will
            # cooperate removing every ip in the list. Each thread will do the
            # job as fast as it can.
            t = threading.Thread(target=self.dequeue)
            t.start()
            threads.append(t)

        # Wait until all the threads are done. .join() is blocking.
        [t.join() for t in threads]

        return self.status


async def download_coroutine(session, url):
    with async_timeout.timeout(3):
        async with session.get(url) as response:
            filename = os.path.basename(url)
            with open(filename, 'wb') as f_handle:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f_handle.write(chunk)
            return await response.release()


async def main(in_a_loop):
    urls = LoadedIPCache
    async with aiohttp.ClientSession(loop=in_a_loop) as session:
        tasks = [download_coroutine(session, url) for url in urls]
        await asyncio.gather(*tasks)




def menu():
    banner()
    global IPList
    amount = input("How many IP addresses do you want to scan: ")
    makeips(amount)


while True:
        menu()

