"""Central application constants. Import from here — never hardcode values elsewhere."""

APP_NAME = "ShellWeaver"
VERSION  = "2.0.0"

# HTTP defaults
DEFAULT_METHOD  = "GET"
DEFAULT_TIMEOUT = 15          # seconds per request

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Sentinel injected into wrapped commands so we can reliably parse CWD back
CWD_SENTINEL = "__SW_CWD__"
