from appdaemon.plugins.hass.hassapi import Hass
from functools import partial

METHODS = ["success", "warning", "error", "alert", "confirm", "notify", "message"]
METHODS_NO_MSG = ["dismiss_all", "ping"]

class LLNotifyMixin(Hass):
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
        super().__init__(*args, **kwargs)

        # For static analysis
        self.ll_success = self.noop
        self.ll_warning = self.noop
        self.ll_error = self.noop
        self.ll_alert = self.noop
        self.ll_confirm = self.noop
        self.ll_dismiss_all = self.noop
        self.ll_notify = self.noop
        self.ll_message = self.noop
        self.ll_ping = self.noop

        if self.ll_notify_component_installed():
            self.add_methods()
        else:
            self.log(
                "ll_notify component not installed. Any calls to ll_notify will be noops.",
                level="WARNING",
            )

    def ll_notify_component_installed(self) -> bool:
        for service in self.list_services():
            if service.get("domain") == "ll_notify":
                return True
        return False

    def add_methods(self):
        def call_ll_notify_service(method, message, *args, **kwargs):
            """Pass through directly via call_service"""
            return self.call_service(f"ll_notify/{method}", message=message, **kwargs)

        for method in METHODS:
            setattr(self, "ll_" + method, partial(call_ll_notify_service, method))
        for method in METHODS_NO_MSG:
            setattr(self, "ll_" + method, partial(call_ll_notify_service, method, ""))


    @staticmethod
    def noop(*args, **kwargs):
        pass
