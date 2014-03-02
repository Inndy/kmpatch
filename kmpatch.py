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

def patch(file, remove_ad, remove_update):
    try:
        f = open(file, "r+b")
    except IOError as e:
        print "Error occurred while opening file '%s'" % file
        return False
    print "File --- %s" % file
    (offset_ad, offset_update, offset_ad_patch, offset_update_patch) = status(f)
    print " -> Advertisement is %s for patch (0x%.8X)" % ("available" if offset_ad > -1 else "unavailable", offset_ad & 0xFFFFFFFF)
    if offset_ad_patch > -1:
        print " -> This file seems to be patched at 0x%.8X (Advertisement)" % (offset_ad_patch & 0xFFFFFFFF)
    if remove_ad:
        if offset_ad > -1:
            print " -> Removing advertisement..."
            f.seek(offset_ad)
            f.write(AD_PATCH)
            print " -> Advertisement removed!"
        else:
            print " -> Can't find advertisement signature"
    print " -> Update checking is %s for patch (0x%.8X)" % ("available" if offset_update > -1 else "unavailable", offset_update & 0xFFFFFFFF)
    if offset_update_patch > -1:
        print " -> This file seems to be patched at 0x%.8X (Update checking)" % (offset_update_patch & 0xFFFFFFFF)
    if remove_update:
        if offset_update > -1:
            print " -> Removing update checking..."
            f.seek(offset_update)
            f.write(UP_PATCH)
            print " -> Update checking removed!"
        else:
            print " -> Can't find update checking signature"
    return True

def status(fileobj):
    fileobj.seek(0)
    content = fileobj.read()
    return (content.find(AD_DATA), content.find(UP_DATA), content.find(AD_PATCH), content.find(UP_PATCH))

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