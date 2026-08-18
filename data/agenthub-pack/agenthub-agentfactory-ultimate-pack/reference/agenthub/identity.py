from __future__ import annotations
import hashlib, json


def canonical_json_sha256(obj) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def build_id(system_id: str, source_sha: str, manifest: dict, runtime_adapter: str, runtime_version: str, model_policy: dict) -> str:
    material = {
        "system_id": system_id,
        "source_sha": source_sha,
        "manifest_sha256": canonical_json_sha256(manifest),
        "runtime_adapter": runtime_adapter,
        "runtime_version": runtime_version,
        "model_policy_sha256": canonical_json_sha256(model_policy),
    }
    return "build_" + canonical_json_sha256(material)[:24]
