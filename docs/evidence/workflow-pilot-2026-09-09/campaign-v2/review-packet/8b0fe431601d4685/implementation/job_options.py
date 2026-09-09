"""Job options shared by execution, preview, and heartbeat scheduling."""


def _retries(options):
    retries = options.get("retries")
    return 3 if retries is None else retries


def execution_options(options):
    """Missing/None retries mean 3; zero means no retries."""
    retries = _retries(options)
    return {"retries": retries, "queue": options.get("queue", "default")}


def preview_options(options):
    """Preview uses the same retries contract as execution."""
    retries = _retries(options)
    return {"attempts": retries + 1}


def heartbeat_seconds(options):
    """Missing, None, or zero heartbeat select the 30-second service default."""
    return options.get("heartbeat") or 30
