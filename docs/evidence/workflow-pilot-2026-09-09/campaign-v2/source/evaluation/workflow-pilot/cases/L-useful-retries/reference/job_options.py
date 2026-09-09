"""Job options shared by execution, preview, and heartbeat scheduling."""

def execution_options(options):
    """Missing/None retries mean 3; zero means no retries."""
    retries = 3 if options.get("retries") is None else options["retries"]
    return {"retries": retries, "queue": options.get("queue", "default")}


def preview_options(options):
    """Preview uses the same retries contract as execution."""
    retries = 3 if options.get("retries") is None else options["retries"]
    return {"attempts": retries + 1}


def heartbeat_seconds(options):
    """Missing, None, or zero heartbeat select the 30-second service default."""
    return options.get("heartbeat") or 30
