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

"""
Create new logger that logs:

1. logbook.log
2. appdaemon.log 
3. HA Logbook: call_service(logbook/log, ...)

"""
from appdaemon import adbase

class LoggingMixin(adbase.ADBase):
    def debug(self, *args, **kwargs):
        adbase = self.get_ad_api()
        return adbase.log(*args, **kwargs, level="DEBUG")

    def info(self, *args, **kwargs):
        adbase = self.get_ad_api()
        return adbase.log(*args, **kwargs, level="INFO")

    def warn(self, *args, **kwargs):
        adbase = self.get_ad_api()
        return adbase.log(*args, **kwargs, level="WARNING")

    def warning(self, *args, **kwargs):
        adbase = self.get_ad_api()
        return adbase.log(*args, **kwargs, level="WARNING")

    def error(self, *args, **kwargs):
        adbase = self.get_ad_api()
        return adbase.log(*args, **kwargs, level="ERROR")

    def critical(self, *args, **kwargs):
        adbase = self.get_ad_api()
        return adbase.log(*args, **kwargs, level="CRITICAL")

    def lb_debug(self, message, *args, **kwargs):
        return self._write_logbook(message, *args, level="DEBUG", **kwargs)

    def lb_info(self, message, *args, **kwargs):
        return self._write_logbook(message, *args, level="INFO", **kwargs)

    def lb_log(self, message, *args, **kwargs):
        return self._write_logbook(message, *args, level="INFO", **kwargs)

    def lb_warn(self, message, *args, **kwargs):
        return self._write_logbook(message, *args, level="WARNING", **kwargs)

    def lb_warning(self, message, *args, **kwargs):
        return self._write_logbook(message, *args, level="WARNING", **kwargs)

    def lb_error(self, message, *args, **kwargs):
        return self._write_logbook(message, *args, level="ERROR", **kwargs)

    def lb_critical(self, message, *args, **kwargs):
        return self._write_logbook(message, *args, level="CRITICAL", **kwargs)

    def _write_logbook(self, message, level=None, entity_id=None, domain=None):
        """
        Note - this only allows a single, pre-merged message.
        This will NOT work as implemented: x.log('{value1}', {'value1': 'value'})
        """
        adbase = self.get_ad_api()
        adbase.log(message)
        if adbase.get_user_log("logbook"):
            adbase.log(message, log="logbook")

        kwargs = {}
        if entity_id:
            kwargs["entity_id"] = entity_id
        if domain:
            kwargs["domain"] = domain
        adbase.call_service("logbook/log", name=self.name, message=message, **kwargs)
