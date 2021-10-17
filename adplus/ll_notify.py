from appdaemon.plugins.hass.hassapi import Hass
from appdaemon import adbase
from appdaemon.adapi import ADAPI

from functools import partial

METHODS = ["success", "warning", "error", "alert", "confirm", "notify", "message"]
METHODS_NO_MSG = ["dismiss_all", "ping"]

class LLNotifyMixin(adbase.ADBase):
    """
    Helper function to make it easy to call add alerts to Lovelace.

    class MyHass(LLNotifyMixin, appdaemon.plugins.hass.hassapi.Hass):
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
    def __init__(self, *args, **kwargs):
        super(adbase.ADBase, self).__init__(*args, **kwargs)

        # For static analysis
        self.ll_success = self.__noop
        self.ll_warning = self.__noop
        self.ll_error = self.__noop
        self.ll_alert = self.__noop
        self.ll_confirm = self.__noop
        self.ll_dismiss_all = self.__noop
        self.ll_notify = self.__noop
        self.ll_message = self.__noop
        self.ll_ping = self.__noop

    # def initialize(self):
    #     super().initialize()

        adbase = self.get_ad_api()

        if self.__ll_notify_component_installed():
            self.__add_methods()
        else:
            adbase.log(
                "ll_notify component not installed. Any calls to ll_notify will be noops.",
                level="WARNING",
            )

    def __ll_notify_component_installed(self) -> bool:
        adbase = self.get_ad_api()

        for service in adbase.list_services():
            if service.get("domain") == "ll_notify":
                return True
        return False

    def __add_methods(self):
        def call_ll_notify_service(method, message, *args, **kwargs):
            """Pass through directly via call_service"""
            adbase = self.get_ad_api()
            return adbase.call_service(f"ll_notify/{method}", message=message, **kwargs)

        for method in METHODS:
            setattr(self, "ll_" + method, partial(call_ll_notify_service, method))
        for method in METHODS_NO_MSG:
            setattr(self, "ll_" + method, partial(call_ll_notify_service, method, ""))


    @staticmethod
    def __noop(*args, **kwargs):
        pass
