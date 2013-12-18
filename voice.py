# voice.py
# A Colloquy plugin for speaking chat and events 
#
# Copyright 2014 Mike Bethany

# Inspired by speech.py by James Tatum

# Version 0.1.0
# Initial design. Lots of redundant code; could be more meta.
# 
# No unused code or includes, best practices followed where I know them,
# Metaprogramming where appropritate, single responsiblity methods(!),
# code should be self commenting so comments held to a minimum.
#
# Also, I don't care what PEP says, LINE UP YOUR DAMN VARIABLES!

import sys
import objc
from AppKit import *

# Module level settings
__setting_on        = True
__setting_join      = True
__setting_nick      = True
__setting_rate      = 250
__setting_volume    = 1.0
__setting_voice     = None

__ON_OFF = {'on': True, 'off': False}

# Colloquy hooks

# Plugin init function called by Colloquy
def load(scriptFile):
    pass

# Called when user enters a /command
def processUserCommand(command, attributed_string_argument, connection, view):

    if not command == 'voice':
        return False
    
    setting, argument = parse_arguments(attributed_string_argument)
    
    #dm('set: [' + setting + ']; arg: [' + argument + ']', view)
    
    # Special case for help
    if setting == '?' or setting == '':
        _voice_help('', view)
        return False
    
    # Call the setter method dynamically
    method_name = "_voice_" + setting
    if hasattr(sys.modules[__name__], method_name):
        return getattr(sys.modules[__name__], method_name)(argument, view)
    else:
        dm("Setting '%s' not found." % setting, view)
        _voice_help('', view)
        return False        

def processIncomingMessage(raw_message, view):
    if not __setting_on:
        return

    msg_source = view.identifier().strip().lower()
    if not msg_source.startswith('chat room'):
        return
    
    message = raw_message.bodyAsPlainText()
    if __setting_nick:
        message = raw_message.senderNickname() + " " + message
    
    speak(message)
    #dm("ident: " + msg_source, view)
  

def memberJoined(member, room):
    if __setting_join:
        nick = member.nickname()
        speak(nick + ' joined the room')
    
def memberParted( member, room, reason ):
    if __setting_join:
        nick = member.nickname()
        speak(nick + ' left the room')

def joinedRoom( room ):
   pass

# Setting commands

def _voice_help(argument, view):
    help_lines = [
        '           ',
        'Voice help:',
        '----------',
        '/voice on',
        '/voice off',
        '/voice nick on',
        '/voice nick off',     
        '/voice join on',
        '/voice join off',
        '/voice vol 0.0-1.0',
        '/voice rate 100-400',
        '/voice help',
        '           '
        ]
    for help_line in help_lines:
        dm(help_line, view, '')
    
    return True


def _voice_on(argument, view):
    global __setting_on
    __setting_on = True
    dm("On", view)
    return True

def _voice_off(argument, view):
    global __setting_on
    __setting_on = False
    dm("Off", view)
    return True

def _voice_nick(argument, view):
    global __setting_nick
    global __ON_OFF
    
    if argument in __ON_OFF:
        __setting_nick = __ON_OFF[argument]
        dm("nick set to '%s'" % argument, view)
    else:
        dm("can't set nick to '%s'" % argument, view)
    
    return True
_voice_n = _voice_nick

def _voice_join(argument, view):
    global __setting_join
    global __ON_OFF

    if argument in __ON_OFF:
        __setting_join = __ON_OFF[argument]
        dm("join set to '%s'" % argument, view)
    else:
        dm("can't set join to '%s'" % argument, view)
    
    return True
_voice_j = _voice_join

def _voice_volume(argument, view):
    global __setting_volume
    volume = float(argument)
    __setting_volume = limit(volume, [0.0, 1.0])
    
    dm("volume set to %0.2f" % __setting_volume, view)
    return True
_voice_vol  = _voice_volume
_voice_v    = _voice_volume

def _voice_rate(argument, view):
    global __setting_rate
    rate = float(argument)
    __setting_rate = limit(rate, [100, 400])

    dm("rate set to %d" % __setting_rate, view)
    return True
_voice_r = _voice_rate

# Voice methods

def speak(text):
    synthisizer().startSpeakingString_(text)


def synthisizer():
    global __setting_volume
    
    voice = NSSpeechSynthesizer.defaultVoice()
    synth = NSSpeechSynthesizer.alloc().initWithVoice_(voice)
    synth.setVolume_(__setting_volume)
    synth.setRate_(__setting_rate)
    
    return synth

def voiceNames():
    voiceList = NSSpeechSynthesizer.availableVoices()
    

# Helper methods
    
# Display Message (don't like the prefix)
def dm(message, view = None, prefix = 'Voice: '):
    
    # We can comment this out and just try catch when we're done
    # if message is None:
    #     return
    # if view is None:
    #     return
    # # We can't display a message if their isn't a place to put it
    # if not hasattr(view, 'addEventMessageToDisplay_withName_andAttributes_'):
    #     return
    
    view.addEventMessageToDisplay_withName_andAttributes_(prefix + message, 'feedback', None)

def parse_arguments(attributed_string_argument):
    clean_args      = (attributed_string_argument.string()).lowercaseString()
    argument_array  = clean_args.split(' ')
    setting         = argument_array[0] or ''
    argument        = argument_array[-1] or ''
    return setting, argument
    

def limit(value, range):
    return max(range[0], min(value, range[1]))