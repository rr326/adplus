# Adplus

## 1/22/23 IMPORTANT - DOES NOT WORK IN `--EDITABLE MODE`

** Installed as NON-editable mode. **

* Currently installed as ` pip install appdaemon_proj/conf/apps/adplus`
* In other words, if you make changes to adplus, you need to restart
  the appdaemon docker container, which *should* reinstall it.
* Note - the fix to this is in requirements.txt !

### Explanation

* This is a long, complex problem. I don't completely understand it.
* Bottom line is that **`pip`** 22.3 brought in a change of behavior
  that broke the way my appdaemon worked. With 21.2.4 everything was
  fine. 
* Somehow the new style of pip distributions broke the ability to properly
  import adplus. Example:
    ```
    Error:      adplus.importlib.reload(adplus)
    Error:  AttributeError: module 'adplus' has no attribute 'importlib'
    ``` 
* If you install it without editable, it works fine.
* I *suspect* it has something to do with [this bug](https://github.com/pypa/pip/issues/11467) 
  but when I tried to reproduce it with their repo, it showed differnt functionlity. So maybe not.
* Also, interestingly, VSCode saw the same issue. It would not properly 
  recognize the `import adplus` when done with `--editable` but would when 
  not editable.
* I've wasted an entire week on this! So just going to punt on it. 
* Hopefully at some point between pip, python, and appdaemon, it will just work again. 

# TODO
* Go through all of adplus. Remove / simplify what I don't use. 
  That might be most of it!
* Especially the way I do reload. 
* **Programming warning: MqPlus.listen_event is getting a Task returned, not a value!**

# AdPlus
AppdaemonPlus - Support functions for AppDaemon

## About
These are support functions I use in my Appdaemon apps. In general they 
are globally available (like all Appdaemon functionality) and do not change
existing fuctionality.

You are welcome to use them. I certainly find them handy. But if you use any of my apps, you'll need to be sure to have these available.

## Installation
You need to include the source code in your `appdaemon/conf/apps` directory, just like AD apps. 

```
git clone https://github.com/rr326/adplus <destination_directory>
```

```bash
# Here is an appreviated directory structure I use
appdaemon/conf/apps
    ├──apps.yaml
    ├──code
    │  ├──__init__.py
    │  ├──adplus
    │  │  ├──adplus
    │  │  │  ├──__init__.py
    │  │  │  └──*.py
    │  ├──.py # Apps
    │  └──*.yaml # Sample config that might have come with installed apps
    └──config
        └──*.yaml # Real config
```

```yaml
# appdaemon.yaml
appdamon:
    # ...
  exclude_dirs:
    - code/adplus

logs:
    # Optional - if you want a separate logbook for key AD actions.
    logbook:
        name: Logbook
        filename: <path_to>/logbook.log

```

Now you **use** this in two ways:
1. By including the directory structure as above (or something like it), Appdaemon will find and use it happily.
2. You can also do a `pip install --editable <path_to_adplus>`. Now your IDEA can find the code and do proper code inspection, highlighting, etc. 



## Features

### Auto-Reload
Appdaemon will auto-reload any APPS it finds. But it does not auto-reload modules imported by those apps.
So if you are changing AdPlus (or any other imported apps), you have to reload Appdaemon for the code changes
to take effect. This is annoying.

Instead, do this:

```python
import adplus

adplus.importlib.reload(adplus)
```
This will auto-reload all the modules within AdPlus.
## update_state
Appdaemon has a [`self.set_state()`](https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.set_state) function. It seems that this *should* update only changed states. And it *sometimes* seems to do just that. But I ran into problems where it was deleting my `friendly_name` when I was not including that in the attributes. I asked in forum or somewhere (and can no longer find it) and the response was that you can't trust that it won't overwrite un-included attributes.

So now, `self.update_state()` will update only changed states.

## ll_notify Helpers
[ll_notify](https://github.com/rr326/ha_ll_notify) Is a component that adds front-end notifications to Lovelace. AdPlus adds simple helper functions:
* `self.ll_success(message, **kwargs)`
* `self.ll_warning(message, **kwargs)`
* `self.ll_error(message, **kwargs)`
* `self.ll_alert(message, **kwargs)`
* `self.ll_confirm(message, **kwargs)`
* `self.ll_dismiss_all(**kwargs)`

Usage:
```python
self.ll_success("This will create a success notification in Lovelace (5 secs)")
self.ll_error("This will create dismissable error notification in Lovelace", wait=0)
```

## Logging - self.debug, self.warn, ...
Appdaemon includes `self.log()` and `self.error()`. But if you want to do a `warn` you have to do something cumbersome like `self.log('message', level = "WARN")`. That's annoying.  With AdPlus you can do:
* `self.log()`
* `self.info()`
* `self.warn()`
* `self.warning()`
* `self.error()`
* `self.critical()`

## Logging - Logbook
I like to log certain key messages to a custom AppDaemon logbook that tracks my main AD log messages, without getting lost within a ton of debug info.

So in my apps I often do something: `self.lb_log('GentleWakeup Running')`

This writes the message in three places:

1. appdaemon.log (default log file)
2. HomeAssistant logbook
3. logbook.log (custom log for these key messages). Note - you must create add a "logbook" entry in the "logs" section of appdaemon.yaml. See "Installation" above.

## normalized_args()
I use [Cerberus](https://docs.python-cerberus.org/en/stable/index.html) for schema validation for my apps. (I chose this over HA's default Voluptuous since it seems that Vol is no longer under development and Cerberus has a lot of current traction.)

Use it this way:

```python
# In app

# Example Schema
SCHEMA = {"test_mode": {"required": False, "type": "boolean", "default": False}}

class MyApp():
    def initialize(self):
        self.argsn=adplus.normalized_args(self, self.SCHEMA, self.args, debug=False)
        # Now you are guaranteed to have args that you can count on. Like:
        self.test_mode = self.argsn["test_mode"]

```

## MQPlus
This is a complicated one. See [mqplus.py](./mqplus.py) for more details.

Basically this makes using MQTT events as easy as using AD events.  It probably loses 
some subtle gains you could get from using MQ Mqtt directly, but makes it much simpler. 

I use Mqtt (and hence MQPlus) in order to signal from my HA Dashboard to trigger an event in an AD app.

For instance:
```yaml
# main_dashboard.yaml
- type: "custom:button-card"
entity: app.heat_state
name: Turn off heat
tap_action:
    action: call-service
    service: mqtt.publish
    service_data:
    topic: "app.turn_heat_off"
    payload: ""
```

```python
class MyApp(adplus.MqPlus):
    def initialize(self):
        # ...
        self.mq_listen_event(self.turn_heat_off, 'app.turn_heat_off')

     def turn_heat_off(self, event_name, data, kwargs): 
        # ...
```

## Not a Criticism of AppDaemon
I realize that some of the above comments could be seen as critical of AD. I **love** AD and think it's amazingly well done. But as a developer I have my own idiosyncracies and hence these changes. 
