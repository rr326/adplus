"""
# adplus Development Space

This creates a adplus development space, with some monkey patching
that I can then use for all my apps. Since everything is globally 
available in AD, this basically just adds new functionality to AD

## Usage
    import adplus
    adplus.importlib.reload(adplus)

    class Test(adplus.Hass):
        ...
        
## Objects
    * Hass
    * Mqtt
    * MqPlus
    * normalized_args
    * weekdays_as_set
    * ConfigException
 
## Explanation
    * MqPlus - Helper class built on Mqtt that allows you to use fire_event & listen_event 
        without thinking about the MQ transport at all. (Hides publish/subscribe.)
        class Test(MqPlus):
            ...
    * Hass / Mqtt
        * self.update_state - like `set_state` but will only update changed state / attributes
        * logging methods: self.info, warning, warn
    * normalized_args - takes a cerberus schema and returns a validated document as a dict

"""
import importlib
import logging
import sys
import types
from functools import partial, partialmethod
from pathlib import Path

from appdaemon.adbase import ADBase
from appdaemon.plugins.hass.hassapi import Hass
from appdaemon.plugins.mqtt.mqttapi import Mqtt
from adplus.mqplus import MqPlus

from .args import normalized_args, weekdays_as_set
from .logbook import logging_monkeypatch
from .utils import ConfigException, _update_state

#
# Reload all modules
#
"""
This is because Appdaemon takes care of reloading apps that change, 
but does not know to reload changes to supporting code.
"""
for module in globals().copy().values():
    if isinstance(module, types.ModuleType):
        importlib.reload(module)
#
# Monkey Patch
#
Hass.update_state = _update_state
Mqtt.update_state = _update_state


#
# Logging Monkey Patch
#
logging_monkeypatch(Hass)
logging_monkeypatch(Mqtt)
logging_monkeypatch(MqPlus)
