import cerberus
from adplus.utils import ConfigException


def normalized_args(self, schema, data, debug=False):
    """
    This takes a cerberus schema and returns a validated document as a dict
    returns: dict

    raises ConfigException if fails to validate.
    """
    appname = self.__class__.__name__
    adapi = self.get_ad_api()

    class CustomValidator(cerberus.Validator):
        def _check_with_validate_entity(self, field: str, entity_id: str) -> None:
            # Requires adapi from closure
            if not adapi.entity_exists(entity_id):
                self._error(field, f"entity_id ({entity_id}) does not exist")

        def _check_with_validate_weekdays(self, field: str, weekdays: str) -> None:
            # "mon,tue,wed,thu,fri,sat,sun"
            dayset = {day.strip()[:3].lower() for day in weekdays.split(",")}
            valid_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            if not dayset <= set(valid_days):
                self._error(
                    field,
                    f"{field} not valid. Must be comma separated subsest of: {valid_days}. got: {dayset}",
                )

        def _check_with_validate_time(self, field: str, timestr: str) -> None:
            # "08:24:32, 13:30:00"
            def parse_time(timestr):
                try:
                    parts = timestr.split(":")
                    parts = [int(part) for part in parts]
                    return (
                        (0 <= parts[0] <= 23)
                        and (0 <= parts[1] <= 59)
                        and (0 <= parts[2] <= 59)
                    )
                except Exception:
                    return False

            if not parse_time(timestr):
                self._error(
                    field,
                    f"{field} not a valid time string like: '08:30:25' or '23:25:00' ",
                )

    validator = CustomValidator(schema, allow_unknown=True)

    if not validator.validate(data):
        self.error(f"{appname}: improper args. Got {data}. Errors: {validator.errors}")
        raise ConfigException(f"{appname}: Configuration failed. {validator.errors}")

    if debug:
        self.log(f"{appname}: normalized_args: initial args: {data}")
        self.log(f"{appname}: normalized_args: normalized: {validator.document}")

    return validator.document


def weekdays_as_set(value):
    # "mon,tue,wed,thu,fri,sat,sun" -> set()
    # Does NOT do validation
    return {day.strip()[:3].lower() for day in value.split(",")}
