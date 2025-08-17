from typing import Protocol

from appdaemon.utils import sync_decorator


class _Loggable(Protocol):
    def log(self, *args, **kwargs):
        pass


class UpdateStateMixin(_Loggable):
    @sync_decorator
    async def update_state(self, entity, state=None, attributes=None):
        """
        In AD, when you update a state, it overwrites all the attributes (but only sometimes!)
        So if you want to set_state="on" but don't want to overwrite "friendly_name", use this:

        from adplus.state import update_state

        update_state(self, entity, state="value", attributes={})
        """
        if attributes is None:
            attributes = {}
        current = await self.get_state(entity, attribute="all")  # type: ignore
        if current is None:
            current = await self.set_state(entity, state="off")  # type: ignore
            if current is None:
                self.log(f"Unable to create state for {entity}")
                return current
        merged_state = state if state else current["state"]
        merged_attributes = current["attributes"].copy()
        merged_attributes.update(attributes)
        return await self.set_state(  # type: ignore
            entity, state=merged_state, attributes=merged_attributes
        )


class EnsureStateMixin(_Loggable):
    @sync_decorator
    async def ensure_state(
        self,
        entity,
        state=None,
        attributes=None,
        success_cb=None,
        error_cb=None,
        already_set_cb=None,
        wait=0.5,
        retries=2,
    ):
        """
        Similar to set_state(), except:
        * Callbacks (success, error, already_set) are called after. Very handy for logging or notifying of success / error
        * wait - Seconds to wait before testing for success
        * retries - Number of retries to test for success before declaring error

        Example:
        def success_cb(self, entity, state, attribute, old, new, kwargs):
            self.log(f'Successfully set {entity} to state: {state} and attributes: {attributes}.')
        def error_cb(self, entity, state, attribute, old, new, kwargs, errobj):
            self.error(f'Failed to set {entity} to state: {state} and attributes: {attributes}. errobj: {errobj}')
        def already_set_cb(self, entity, state, attribute, old, new, kwargs):
            pass # State was already at desired state. Don't bother logging.

        new_state = self.set_state('climate.my_ecobee', state="perm_hold", attributes={"temperature":41}, success_cb=success_cb, error_cb=error_cb, wait=3, retries=2)
        """
        raise RuntimeError("Not implemented yet. WIP.")
