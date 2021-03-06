'''
  Functionality for embedded message creation
  Can only be accessed from admins
'''

import discord
import json
import os

# Initialization
# timestamp? provider?
attributes = ['color', 'description', 'timestamp', 'title', 'type', 'title-url']
valid_dict_names = ['author', 'footer', 'image', 'thumbnail', 'video', 'fields']
valid_dict_attributes = ['name', 'url', 'value', 'icon_url', 'inline', 'text', 'proxy_url', 'width', 'height']
attribute_mappings = {
  'author': ['name', 'url', 'icon_url'],
  'footer': ['text', 'icon_url'],
  'image': ['url', 'proxy_url', 'width', 'height'],
  'thumbnail': ['url', 'proxy_url', 'width', 'height'],
  'video': ['url', 'width', 'height'],
  'fields': ['name', 'value', 'inline']
}

default_template = {
  'title': "Template Title",
  'color': 0x0be0e0,
  'description': "Template Description"
}
embed = {}

folder = 'templates'
fpath = folder + '/'

# Creates a new default embed
def new():
  print("Creating new embed")
  global embed
  embed.clear()
  embed = default_template.copy()
  return

# show the current state of the embedded message before publishing
# returns the embedded message to be printed
def preview():
  print("Previewing embed")
  global embed
  return discord.Embed.from_dict(embed)

# updates content to the embedded message
# returns true on success, false otherwise
def add(msg):
  print("Updating attribute")
  # verification
  words = msg.split(' ')
  if len(words) < 3:
    return False
  attr = words[1]
  val = words[2]
  for i in range(3, len(words)):
    val += ' ' +words[i]
  print("Attribute:",attr)
  print("Value:",val)
  
  # regular embedded attributes
  if attr in attributes:
    if attr == 'color':
      embed.update({attr: int(val, 16)})
    elif attr == 'title-url':
      embed.update({'url', val})
    else:
      embed.update({attr: val})
    return True

  # nested embedded attributes
  words = attr.split('-')
  dict_name = words[0]
  dict_attr = words[1]
  if dict_name in valid_dict_names and dict_attr in valid_dict_attributes:
    print("dict_name:", dict_name)
    print("dict_attr:", dict_attr)
    print("Original Embed:",embed)

    # makes sure the attr is an existing attribute
    if not dict_attr in attribute_mappings[dict_name]:
      return False
    
    # update dict_name if it already exists
    if dict_name in embed.keys():
      d = embed[dict_name]
      d.update({dict_attr: val})
      embed[dict_name].update(d)
    # add new dictionary to the embed dict
    else:
      embed.update({dict_name: {dict_attr: val}})
    print("Updated embed:", embed)
    return True
  return False

# removes content from the embedded message
# returns true on success, false otherwise
def remove(msg):
  print("Removing attribute")
  words = msg.split(' ')
  if len(words) < 2:
    return False
  attr = words[1]
  print("Attr:",attr)
  if attr in attributes:
    if attr == 'title-url':
      attr = 'url'
    embed.pop(attr)
    return True
  return False

# shows all saved templates
# returns a list of embeds to be shown
def templates():
  print("Printing Templates")
  msgs = []
  # each element is a tuple of (name, Embedded message)
  for fname in os.scandir(folder):
    if fname.is_file():
      f = open(fname.path, 'r')
      js = json.load(f)
      f.close()
      msgs.append((str(fname), discord.Embed.from_dict(js)))
  print("Msgs:", msgs)
  return msgs
  
# loads embedded message from a saved template
# second arg should be templatenae, no path/extension
def load(msg):
  # verification
  print("Loading Template")
  fname = second_arg(msg)
  print("fname:", fname)
  if fname == '':
    return False
  fname += '.json'

  # opening json file and loading contents into
  # global embed object
  try:
    f = open(fpath + fname, 'r')
    print("fpath + fname:", fpath+fname)
    t = json.load(f)
    f.close()
    global embed
    embed = t.copy()
    print("embed:",embed)
    return True
  except:
    return False

# save the current embedded message as a template
# second arg should be templatename, no path/extension
def save(msg):
  # verification
  print("Saving Template")
  fname = second_arg(msg)
  print('fname:', fname)
  if fname == '':
    return False
  fname += '.json'

  # saving embed dictionary to json file in templates folder
  global embed
  js = json.dumps(embed)
  f = open(fpath + fname, 'w')
  f.write(js)
  f.close()
  return True

# deletes template from saved templates
def delete(msg):
  # verification
  print("Deleting Template")
  fname = second_arg(msg)
  if fname == '':
    return False
  fname += '.json'

  # delete the local json filename in templates folder
  if os.path.exists(fpath+fname):
    os.remove(fpath+fname)
  else:
    return False
  return True

# returns the second arg of an input as a continuous string
def second_arg(msg):
  words = msg.split(' ')
  s = words[1]
  for i in range(2, len(words)):
    s += ' ' + words[i]
  return s

# returns an embedded message containing a list of accessible 
# channels with their respective servers
# c is an ordered list of (server, channel)
def channels(list):
  print("Generating accessible channels")
  e = discord.Embed(title="Accessible Channels", description="List of channels that I'm able to publish to", color = 0x55FDF9)
  e.set_footer(text="run !publish [channel_id] to publish the current message to that channel")
  id = 0
  while id < len(list):
    channels = ''
    server = list[id][0]
    while id < len(list) and list[id][0] == server:
      channel = list[id][1]
      channels += 'ID: ' + str(id) + ' | Channel: ' + str(channel) + '\n'
      id += 1
    # create a field where the title is the server name 
    # and the contents are the accessible channels with their id
    e.add_field(name="Server: "+str(server), value=channels, inline=False)
  return e
  
# returns embedder help functionality
def help():
  f = open('bot_embeds/help.json', 'r')
  help = json.load(f).copy()
  f.close()
  return discord.Embed.from_dict(help)