ALLOWED={
 "DRAFT":{"CERTIFIED"},
 "CERTIFIED":{"GITHUB_STAGED"},
 "GITHUB_STAGED":{"GITHUB_PUBLISHED"},
 "GITHUB_PUBLISHED":{"DEPLOYING"},
 "DEPLOYING":{"LIVE_VERIFIED","GITHUB_PUBLISHED"},
 "LIVE_VERIFIED":{"RELEASED"},
 "RELEASED":set(),
}
def transition(current,target):
    if target not in ALLOWED.get(current,set()):
        raise ValueError(f"illegal release transition {current}->{target}")
    return target
