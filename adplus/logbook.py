"""
# WIP
This is not working. 

# Usage:
    add_logbook(hass.Hass)

# Results
    hass.lb = Logger with special features

    hass.lb.log (.info, .debug, ...)
        Default writes to:
            * current app log
            * adaemon logbook log
            * Home Assitant logbook (with call_service('logbook/log'))
        Special parameters:
            * hass.info("message", _skip_applog = True) # Skip app log
            * hass.info("message", _skip_adlogbook = True) # Skip Appdaemon logbook
            * hass.info("message", _skip_halogbook = True) # Skip HomeAssistant logbook
"""
from functools import partialmethod
from typing import Union

from adplus.mqplus import MqPlus
from appdaemon.plugins.hass.hassapi import Hass
from appdaemon.plugins.mqtt.mqttapi import Mqtt

AnyADBase = Union[Hass, Mqtt, MqPlus]

"""
Create new logger that logs:

1. logbook.log
2. appdaemon.log 
3. HA Logbook: call_service(logbook/log, ...)

"""


def _write_logbook(self, message, level=None, entity_id=None, domain=None):
    """
    Note - this only allows a single, pre-merged message.
    This will NOT work as implemented: x.log('{value1}', {'value1': 'value'})
    """
    self.log(message)
    if self.get_user_log("logbook"):
        self.log(message, log="logbook")

    kwargs = {}
    if entity_id:
        kwargs["entity_id"] = entity_id
    if domain:
        kwargs["domain"] = domain
    self.call_service("logbook/log", name=self.name, message=message, **kwargs)


def logging_monkeypatch(obj: AnyADBase):
    # Logging helpers
    obj.debug = partialmethod(obj.log, level="DEBUG")
    obj.info = partialmethod(obj.log, level="INFO")
    obj.warn = partialmethod(obj.log, level="WARNING")
    obj.warning = partialmethod(obj.log, level="WARNING")
    # obj.error = partialmethod(obj.log, level="ERROR")
    obj.critical = partialmethod(obj.log, level="CRITICAL")

    # Logbook
    obj.lb_debug = partialmethod(_write_logbook, level="DEBUG")
    obj.lb_info = partialmethod(_write_logbook, level="INFO")
    obj.lb_warn = partialmethod(_write_logbook, level="WARNING")
    obj.lb_warning = partialmethod(_write_logbook, level="WARNING")
    obj.lb_log = partialmethod(_write_logbook, level="INFO")
    obj.lb_error = partialmethod(_write_logbook, level="ERROR")
    obj.lb_critical = partialmethod(_write_logbook, level="CRITICAL")
