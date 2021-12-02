import asyncio
import atexit
import json

from appdaemon.plugins.mqtt.mqttapi import Mqtt
from appdaemon.utils import sync_wrapper

from .ll_notify import LLNotifyMixin
from .logbook import LoggingMixin
from .state import UpdateStateMixin


class MqPlus(Mqtt, LLNotifyMixin, LoggingMixin, UpdateStateMixin):
    """
    Helper that makes using MQ as easy as using normal AD events.

    Usage:
        import adplus
        adplus.importlib.reload(adplus)

        class Test(MqPlus):
            event = "unique_event_name_string"

            cancel_handle = self.mq_listen_event(my_callback, event, **kwargs)

            self.mq_fire_event(event, **kwargs)

            def my_callback(self, event_name, data, kwargs):
                # data -   data supplied by fire_event
                # kwargs - args supplied by listen_event
                pass

            self.mq_cancel_listen_event(cancel_handle)


    def my_callback(self, event_name, data, kwargs):
        pass

    Note:
        1. This simplifies *and limits* MQ. There are features not available using
           this helper. (eg: Subscribe to wild cards)
        2. This creates a one-to-one mapping of events to MQ "topics"
        3. This uses mqtt_publish() and mqtt_subscribe() but subscription does not seem to
           have any effect.
        4. You can add qos= and retain= keywords to fire_event. (Low level MQ concepts.)
        5. You can also use the raw listener events with:
            ha_listen_event()
            ha_cancel_listen_event()
            ha_fire_event()

    ## Dev Notes
    * You need to be really careful with namespaces and always use it
    * I do not do is_client_connected(). Maybe I should!
    * Subscription does NOT seem to matter. It seems you get EVERY MQTT_MESSAGE event whether
      you are subscribed or not. But I try to do proper subscribe() / unsubscribe() in case
      it starts working.
    * I don't understand asycio and am getting unexpected behavior in mq_listen_event
        * I would think cancel_handle = await self.ha_listen_event() would give
          a value, but instead I'm getting a Task.

    ## MQ
    qos
        0 - at most once
        1 - at least once
        2 - exactly once (default)
    retain - True(defualt)
        The broker stores the last known state and sends it to a new subscriber.
        Retained messages help newly-subscribed clients get a status update immediately after they subscribe to a topic. The retained message eliminates the wait for the publishing clients to send the next update.
    """

    MQ_QOS = 2
    MQ_RETAIN = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.namespace = self.config["plugins"]["mqtt"]["namespace"]
        self._registered_listeners = {}  # see _listener_register
        atexit.register(self.cleanup)

        self.ha_listen_event = super().listen_event
        self.ha_fire_event = super().fire_event
        self.ha_cancel_listen_event = super().cancel_listen_event

    def listen_event(*args, **kwargs):
        raise RuntimeError(
            "Do not use listen_event directly when using MqPlus. Instead use mq_listen or ha_listen "
        )

    def cancel_listen_event(*args, **kwargs):
        raise RuntimeError(
            "Do not use cancel_listen_event directly when using MqPlus. Instead use mq_cancel_listen or ha_cancel_listen "
        )

    def fire_event(*args, **kwargs):
        raise RuntimeError(
            "Do not use fire directly when using MqPlus. Instead use mq_fire or ha_fire "
        )

    def _get_handle(self, event_name):
        for handle, name in self._registered_listeners.items():
            if name == event_name:
                return handle  # Found it!
        return None  # Not found

    def _listener_register(self, event_name: str, cancel_handle: str) -> None:
        """
        This tracks handles and events, so given an handle, you can cancel the corresponding topic

        self._registered_listeners = {"cancel_handle": "event_name"}
        """
        self._registered_listeners[cancel_handle] = event_name

    def _listener_unregister(self, cancel_handle: str) -> None:
        if cancel_handle in self._registered_listeners:
            del self._registered_listeners[cancel_handle]
        else:
            self.log(
                f"_listener_unregister is trying to unregister a cancel_handle it does not know about: {cancel_handle}"
            )

    @sync_wrapper
    async def mq_listen_event(self, callback, event, **kwargs):
        """
        event - 'event_string' within namespace="mqtt"

        Note - this will prevent multiple callback/event listeners, which would otherwise happen
        as a module that uses this reloads (and doesn't know to delete listeners in this app). To do this it will delete the old listener first.

        Note - this will not capture an app that disables itself (and does not know to unregister its listeners!)

        ROSS TODO: The right solution is for apps that want to use this to inherit from this. Maybe as a mixin. THINK!

        """
        if "namespace" in kwargs:
            raise RuntimeError(f"Do not set namespace. Will cause errors: {kwargs}")
        if "topic" in kwargs:
            raise RuntimeError(f"Do not set topic. The event IS the topic {kwargs}")
        if type(event) is not str:
            raise RuntimeError(
                f"Event must be a string got: {event} - type: {type(event)}"
            )

        kwargs = self.clean_kwargs(kwargs)

        self.log(f"Subscribe topic: '{event}' -- kwargs: {kwargs}")

        self.mqtt_subscribe(event, namespace=self.namespace)
        cancel_handle = await self.ha_listen_event(
            callback,
            event="MQTT_MESSAGE",
            topic=event,
            namespace=self.namespace,
            **kwargs,
        )
        if isinstance(cancel_handle, asyncio.Task):
            # I think this is a bug in appdaemon
            # Issue: https://github.com/AppDaemon/appdaemon/issues/1085
            self.log(
                "Programming warning: MqPlus.listen_event is getting a Task returned, not a value!",
                level="WARNING",
            )
            cancel_handle = cancel_handle._result
        self._listener_register(event, cancel_handle)

        return cancel_handle

    @sync_wrapper
    async def mq_cancel_listen_event(self, handle):
        event_name = self._registered_listeners.get(handle)
        self.log(
            f"cancel_listen_event handle: {handle} - event_name: '{event_name}''",
            level="DEBUG",
        )
        self.ha_cancel_listen_event(handle)
        if event_name is None:
            self.log(
                f"cancel_listen_event - no event_name found for handle: {handle}. Can not unsubscribe",
                level="WARNING",
            )
        else:
            self.mqtt_unsubscribe(event_name, namespace=self.namespace)

        self._listener_unregister(handle)

    @sync_wrapper
    async def mq_fire_event(self, event, qos=MQ_QOS, retain=MQ_RETAIN, **kwargs):
        cleanargs = self.clean_kwargs(kwargs)

        keys = list(cleanargs.keys())
        if len(keys) > 1:
            payload = json.dumps(cleanargs)
        elif (
            len(keys) == 1
            and keys[0] == "message"
            and type(cleanargs["message"]) is str
        ):
            payload = cleanargs["message"]
        else:
            raise NotImplementedError(
                f"Received unexpected payload requies to MQHelper.fire_event. cleanargs: {cleanargs}"
            )
        self.log(
            f"Firing: topic: '{event}' -- payload: {payload} -- namespace = '{self.namespace}'"
        )
        self.mqtt_publish(
            event, payload, qos=qos, retain=retain, namespace=self.namespace
        )

    def clean_kwargs(self, kwarg_dict):
        # AD callbacks receive keys like '__thread_id'. remove those
        return {
            k: v for k, v in kwarg_dict.items() if k not in {"__thread_id", "namespace"}
        }

    def cleanup(self):
        self.log("Class exiting. Going to clean up.")
        for handle, _ in self._registered_listeners.items():
            self.cancel_listen_event(handle)
