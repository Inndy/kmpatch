# -*- coding: utf-8 -*-

import sys

OPTIONS = [
    [ "no-ads", "a", "Remove advertisement" ],
    [ "no-update", "u", "Disable update checking" ]
]

AD_DATA = "http://player.kmpmedia.net/kmp_plus/platform/view/main".encode("utf-16")[2:]
AD_PATCH = "about:blank".encode("utf-16")[2:] + "\0" * 8 + "!!ADVERTISEMENT_BLOCKED!!"
UP_DATA = "http://cdn.kmplayer.com/KMP/Download/KMPVer_"#.encode("utf-16")[2:]
UP_PATCH = "\0" * 8 + "!!UPDATE_BLOCKED!!"

def parse_cmd():
    files = []
    flags = []
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            flags.append(arg[2:])
        elif arg[0] == "-":
            map(flags.append, arg[1:])
        else:
            files.append(arg)
    flag_map = {}
    for opt in OPTIONS:
        flag_map[opt[1]] = opt[0]
    new_flags = []
    for flag in flags:
        new_flags.append(flag if flag not in flag_map else flag_map[flag])
    return (new_flags, files)

def usage():
    print "Usage: %s [options] file1 file2 ..." % sys.argv[0]
    print "\noptions:"
    for opt in OPTIONS:
        print "    --%-10s,-%-4s%s" % tuple(opt)

def do_patch(fileobj, signature, content, description):
    print " -> Patching for %s..." % description
    last = 0
    fileobj.seek(0)
    body = fileobj.read()
    while True:
        pos = body.find(signature, last)
        if pos == -1:
            break
        print " -----> Patch at 0x%.8X" % pos
        fileobj.seek(pos)
        fileobj.write(content)
        last = pos
    if last == 0:
        print " -----> Patch failed"

def patch(file, remove_ad, remove_update):
    try:
        f = open(file, "r+b")
    except IOError as e:
        print "Error occurred while opening file '%s'" % file
        return False
    print "File --- %s" % file
    do_patch(f, AD_DATA, AD_PATCH, "advertisement")
    do_patch(f, UP_DATA, UP_PATCH, "update checking")

def main():
    if len(sys.argv) < 2:
        usage()
        exit()
    (flags, files) = parse_cmd()
    if len(files) == 0:
        print "Err: No input files"
        exit()
    remove_ad = "no-ads" in flags
    remove_update = "no-update" in flags
    for f in files:
        patch(f, remove_ad, remove_update)

if __name__ == '__main__':
    main()