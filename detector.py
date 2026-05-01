def detect_suspicious(p):
    reasons = []

    cpu = p.get('cpu_percent', 0)
    threads = p.get('threads', 0)
    name = p.get('name')
    status = p.get('status')

    if cpu > 80:
        reasons.append("high CPU")

    if threads > 50:
        reasons.append("too many threads")

    if name is None or name == "":
        reasons.append("corrupted process")

    if cpu == 0 and threads > 30:
        reasons.append("possible bug")

    if status == "zombie":
        reasons.append("zombie process")

    return reasons