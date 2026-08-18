import hashlib, json

def stable_json_for_tests(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def digest_bytes(b):
    return hashlib.sha256(b).hexdigest()

def dedupe_key(workflow_id,workflow_version,trigger_id,input_digest,stage):
    material="\x1f".join([workflow_id,workflow_version,trigger_id,input_digest,stage]).encode()
    return hashlib.sha256(material).hexdigest()

def trigger_id(schedule_id,logical_due_iso):
    return hashlib.sha256(f"{schedule_id}\x1f{logical_due_iso}".encode()).hexdigest()
