from dataclasses import asdict
from venturelab_os.verification.certificate import issue
from venturelab_os.core import hash_object
def test_certificate_commits_artifacts():
    c,h=issue("run",["b","a"],["g"],"root")
    assert c.artifact_hashes==("a","b")
    assert h==hash_object(asdict(c))
