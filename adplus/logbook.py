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
from typing import Protocol

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


# For type hints
class _Loggable(Protocol):
    def log(self, *args, **kwargs):
        pass


class LoggingMixin(_Loggable):
    def debug(self, *args, **kwargs):
        return self.log(*args, **kwargs, level="DEBUG")

    def info(self, *args, **kwargs):
        return self.log(*args, **kwargs, level="INFO")

    def warn(self, *args, **kwargs):
        return self.log(*args, **kwargs, level="WARNING")

    def warning(self, *args, **kwargs):
        return self.log(*args, **kwargs, level="WARNING")

    def error(self, *args, **kwargs):
        return self.log(*args, **kwargs, level="ERROR")

    def critical(self, *args, **kwargs):
        return self.log(*args, **kwargs, level="CRITICAL")

    def _write_logbook(self, *args, **kwargs):
        return self._write_logbook(*args, **kwargs)

    def lb_debug(self, *args, **kwargs):
        return self._write_logbook(*args, **kwargs, level="DEBUG")

    def lb_info(self, *args, **kwargs):
        return self._write_logbook(*args, **kwargs, level="INFO")

    def lb_log(self, *args, **kwargs):
        return self._write_logbook(*args, **kwargs, level="INFO")

    def lb_warn(self, *args, **kwargs):
        return self._write_logbook(*args, **kwargs, level="WARNING")

    def lb_warning(self, *args, **kwargs):
        return self._write_logbook(*args, **kwargs, level="WARNING")

    def lb_error(self, *args, **kwargs):
        return self._write_logbook(*args, **kwargs, level="ERROR")

    def lb_critical(self, *args, **kwargs):
        return self._write_logbook(*args, **kwargs, level="CRITICAL")
