ALLOWED = {
    "PENDING":{"READY","CANCELLED"},
    "READY":{"LEASED","CANCELLED"},
    "LEASED":{"RUNNING","READY","CANCELLED"},
    "RUNNING":{"VERIFYING","RETRY_WAIT","FAILED","BLOCKED","DEADLETTER","CANCELLED"},
    "VERIFYING":{"SUCCEEDED","RETRY_WAIT","FAILED","BLOCKED","DEADLETTER"},
    "RETRY_WAIT":{"READY","DEADLETTER","CANCELLED"},
    "BLOCKED":{"READY","FAILED","CANCELLED"},
    "DEADLETTER":{"READY","CANCELLED"},
    "SUCCEEDED":set(),"FAILED":set(),"CANCELLED":set(),
}
def transition(current,target):
    if target not in ALLOWED.get(current,set()):
        raise ValueError(f"illegal transition {current}->{target}")
    return target
