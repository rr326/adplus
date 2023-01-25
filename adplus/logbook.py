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
import appdaemon.adbase as adbase


class LoggingMixin(adbase.ADBase):
    def debug(self, *args, **kwargs):
        my_adapi = self.get_ad_api()
        return my_adapi.log(*args, **kwargs, level="DEBUG")

    def info(self, *args, **kwargs):
        my_adapi = self.get_ad_api()
        return my_adapi.log(*args, **kwargs, level="INFO")

    def warn(self, *args, **kwargs):
        my_adapi = self.get_ad_api()
        return my_adapi.log(*args, **kwargs, level="WARNING")

    def warning(self, *args, **kwargs):
        my_adapi = self.get_ad_api()
        return my_adapi.log(*args, **kwargs, level="WARNING")

    def error(self, *args, **kwargs):
        my_adapi = self.get_ad_api()
        return my_adapi.log(*args, **kwargs, level="ERROR")

    def critical(self, *args, **kwargs):
        my_adapi = self.get_ad_api()
        return my_adapi.log(*args, **kwargs, level="CRITICAL")

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

    def _write_logbook(
        self, message, level=None, entity_id=None, domain=None
    ):  # pylint: disable=unused-argument
        """
        Note - this only allows a single, pre-merged message.
        This will NOT work as implemented: x.log('{value1}', {'value1': 'value'})
        """
        my_adapi = self.get_ad_api()
        my_adapi.log(message)
        if my_adapi.get_user_log("logbook"):
            my_adapi.log(message, log="logbook")

        kwargs = {}
        if entity_id:
            kwargs["entity_id"] = entity_id
        if domain:
            kwargs["domain"] = domain
        my_adapi.call_service("logbook/log", name=self.name, message=message, return_result=False, **kwargs)
