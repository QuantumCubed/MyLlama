from datetime import tzinfo, datetime
from pydantic import validate_call

# @validate_call
# def get_local_time(format: str, timezone: tzinfo | None) -> str:
#     # return "5:35 AM"
#     return str(datetime.now(timezone))

@validate_call
def get_local_time(format: str, timezone: str | None) -> str:
    return "5:35 AM"