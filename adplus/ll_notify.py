from appdaemon.plugins.hass.hassapi import Hass
from functools import partial

METHODS = [
    "success",
    "warning",
    "error",
    "alert",
    "confirm",
    "dismiss_all",
    "notify",
    "message",
    "ping",
]


class LLNotifyMixin(Hass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log("ll_notify helper initialized")

        if self.ll_notify_component_installed():
            self.add_methods()
        else:
            self.add_noops()

    def ll_notify_component_installed(self) -> bool:
        for service in self.list_services():
            if service.get("domain") == "ll_notify":
                return True
        return False

    def add_methods(self):
        def call_ll_notify_service(method, *args, **kwargs):
                """Pass through directly via call_service"""
                self.log(
                    f"ADPLUS PASSTHROUGH: ll_notify/{method}, args: {args}, kwargs: {kwargs}",
                    level="DEBUG",
                )
                print(
                    f"ADPLUS PASSTHROUGH: ll_notify/{method}, args: {args}, kwargs: {kwargs}, cb: {id(call_ll_notify_service)}"
                )
                return self.call_service(f"ll_notify/{method}", **kwargs)

        for method in METHODS:            
            setattr(self, "ll_" + method, partial(call_ll_notify_service, method))
            self.log(
                f"Registered method: ll_{method}, cb id:{id(call_ll_notify_service)}"
            )
            print(f'Registering {method}, cb id:{id(call_ll_notify_service)} - hass id: {id(self)}')
        print('After add_methods')


    def add_noops(self):
        self.log(
            "ll_notify component not installed. Any calls to ll_notify will be noops.",
            level="WARNING",
        )

        def noop(*args, **kwargs):
            pass

        for method in METHODS:
            setattr(self, "ll_" + method, noop)
