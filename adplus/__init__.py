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
import logging  # noqa
import sys  # noqa
import types

from appdaemon.plugins.hass.hassapi import Hass as _Hass
from appdaemon.plugins.mqtt.mqttapi import Mqtt as _Mqtt

from .args import normalized_args, weekdays_as_set  # noqa
from .logbook import LoggingMixin
from .mqplus import MqPlus  # noqa
from .utils import ConfigException, UpdateStateMixin  # noqa

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
# Monkey Patch - Logging, UpdateSate
#


class Hass(_Hass, LoggingMixin, UpdateStateMixin):
    pass


class Mqtt(_Mqtt, LoggingMixin, UpdateStateMixin):
    pass
