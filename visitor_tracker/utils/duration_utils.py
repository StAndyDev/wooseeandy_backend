def timedelta_to_iso8601(duration):
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    iso = "PT"
    if hours:
        iso += f"{hours}H"
    if minutes:
        iso += f"{minutes}M"
    if seconds or iso == "PT":
        iso += f"{seconds}S"
    return iso