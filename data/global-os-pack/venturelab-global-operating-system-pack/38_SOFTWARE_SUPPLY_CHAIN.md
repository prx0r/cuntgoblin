# Software Supply Chain

Maintain `third_party/lock.yaml`.

For every imported repo:
- repository
- exact commit SHA
- license
- purpose
- reviewed date
- production dependency? yes/no
- update policy

Do not benchmark floating `main`.

Production OCI images pin digests.

Lock Python/JS dependencies.

Released products should generate a software bill of materials when available and store it
with the release artifact.

Use standard OCI labels for source/revision/version/license where possible.
