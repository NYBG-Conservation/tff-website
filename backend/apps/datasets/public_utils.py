import re

_MOBILE_UA_RE = re.compile(
    r"android.*mobile|iphone|ipod|blackberry|iemobile|opera mini|mobile",
    re.IGNORECASE,
)
_TABLET_UA_RE = re.compile(r"ipad|tablet|android(?!.*mobile)", re.IGNORECASE)


def is_mobile_user_agent(user_agent: str) -> bool:
    if not user_agent:
        return False
    if _TABLET_UA_RE.search(user_agent):
        return False
    return bool(_MOBILE_UA_RE.search(user_agent))
