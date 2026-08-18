RETRYABLE={"TRANSIENT_NETWORK","TRANSIENT_RATE_LIMIT","SERVER","LEASE_EXPIRED"}

def should_retry(error_class,attempt_no,max_attempts):
    return error_class in RETRYABLE and attempt_no<max_attempts

def backoff_seconds(attempt_no,base=10,cap=900):
    raw=min(cap,base*(2**max(0,attempt_no-1)))
    return raw*1.17

def priority(value,confidence,success_prob,urgency,cost,blocker=1,unlock=1,stale=1,finish=1):
    numerator=max(0,value)*max(0,confidence)*max(0,success_prob)*max(0,urgency)
    return numerator/max(float(cost),1e-9)*blocker*unlock*stale*finish
