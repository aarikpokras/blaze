#!/usr/bin/env python3

import sys
from time import sleep
import json

def eprint(message, color=False):
  if (color):
    print("\033[0;31m" + message + "\033[0m", file=sys.stderr)
  else:
    print(message, file=sys.stderr)

args = sys.argv

if (len(args) < 2):
  eprint("Command missing")
  sys.exit(1)
else:
  if (args[1] == "--find-entry" or args[1] == "-f"):
    key_des = args[2]
    print("> Loading JSON file")
    with open('h.json', 'r') as hf:
      c = json.load(hf)
      print(">> |")
      try:
        print(">>> Fetching value")
        print(">>> Value: \033[1;37m" + c[key_des] + "\033[0m")
        print(">>> |")
      except KeyError:
        eprint(">>>! Key not found", True)
        sys.exit(4)
  elif (args[1] == "--delete-entry"):
    d = {}
    key_des = args[2]
    print("> Loading JSON file")
    with open('h.json', 'r') as hf:
      d = json.load(hf)
      print(">> |")
      print(">> Finding key")
      if (d[key_des]):
        print(">>> |")
        print(">>> Sleeping 2")
        sleep(2)
        print(">>> |")
        print(">>> Opening new FP")
      else:
        eprint(">>>! Key not found", True)
        sys.exit(4)

    with open('h.json', 'w') as hf:
      print(">>> |")
      print(">>> Deleting KVP")
      del d[key_des]
      print(">>> |")
      print(">>> Pre-write sleep 4")
      sleep(4)
      json.dump(d, hf)

  else:
    eprint("Command unknown")
    sys.exit(2)
