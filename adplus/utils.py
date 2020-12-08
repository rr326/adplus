from appdaemon.utils import sync_wrapper


@sync_wrapper
async def _update_state(self, entity, state=None, attributes={}):
    """
    In AD, when you update a state, it overwrites all the attributes (but only sometimes!)
    So if you want to set_state="on" but don't want to overwrite "friendly_name", use this:

    from adplus.utils import update_state

    update_state(self, entity, state="value", attributes={})
    """
    current = await self.get_state(entity, attribute="all")
    if current == None:
        current = await self.set_state(entity, state="off")
        if current == None:
            self.log(f"Unable to create state for {entity}")
            return current
    merged_state = state if state else current["state"]
    merged_attributes = current["attributes"].copy()
    merged_attributes.update(attributes)
    return await self.set_state(
        entity, state=merged_state, attributes=merged_attributes
    )


class ConfigException(Exception):
    """
    Invalid configuration
    """
