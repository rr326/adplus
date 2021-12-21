"""
LLNotifyMixin
"""

import appdaemon.adbase as adbase

METHODS = ["success", "warning", "error", "alert", "confirm", "notify", "message"]
METHODS_NO_MSG = ["dismiss_all", "ping"]


class LLNotifyMixin(adbase.ADBase):
    """
    Helper function to make it easy to call add alerts to Lovelace.

    class Hass(_Hass, LLNotifyMixin,):
        pass

    class MyApp(MyHass):
        def initialize(self):
            self.ll_success("This will create a success notification in Lovelace!", wait=0)

    Methods:
        * ll_success
        * ll_warning
        * ll_error
        * ll_alert
        * ll_confirm
        * ll_dismiss_all
        * ll_notify
        * ll_message
        * ll_ping

    """

    def ll_success(self, message, **kwargs):
        return self.__call_ll_notify_service("success", message, **kwargs)

    def ll_warning(self, message, **kwargs):
        return self.__call_ll_notify_service("warning", message, **kwargs)

    def ll_error(self, message, **kwargs):
        return self.__call_ll_notify_service("error", message, **kwargs)

    def ll_alert(self, message, **kwargs):
        return self.__call_ll_notify_service("alert", message, **kwargs)

    def ll_confirm(self, message, **kwargs):
        return self.__call_ll_notify_service("confirm", message, **kwargs)

    def ll_notify(self, message, **kwargs):
        return self.__call_ll_notify_service("notify", message, **kwargs)

    def ll_message(self, message, **kwargs):
        return self.__call_ll_notify_service("message", message, **kwargs)

    def ll_dismiss_all(self, message, **kwargs):
        return self.__call_ll_notify_service("dismiss_all", "", **kwargs)

    def ll_ping(self, message, **kwargs):
        return self.__call_ll_notify_service("ping", "", **kwargs)

    def __call_ll_notify_service(self, method, message, **kwargs):
        if not self.__ll_notify_component_installed():
            return
        return self.get_ad_api().call_service(
            f"ll_notify/{method}", message=message, **kwargs
        )

    def __ll_notify_component_installed(self) -> bool:
        for service in self.get_ad_api().list_services():
            if service.get("domain") == "ll_notify":
                return True
        return False
