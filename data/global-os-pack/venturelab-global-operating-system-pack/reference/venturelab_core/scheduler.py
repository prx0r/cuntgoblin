from .identity import trigger_id

def due_trigger(schedule_id,logical_due_iso,seen):
    tid=trigger_id(schedule_id,logical_due_iso)
    return None if tid in seen else tid

def catchup_times(policy,missed):
    missed=list(missed)
    if not missed:return []
    if policy=="latest_only":return [missed[-1]]
    if policy=="one":return [missed[0]]
    if policy=="all":return missed
    if policy=="skip":return []
    raise ValueError(policy)
