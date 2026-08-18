# Commit-Time Validation

Before any durable external effect:
- publish
- deploy
- canonical promotion
- factory activation
- provider/account activation

re-check:
1. input/dependency digests still match;
2. prerequisite evidence still valid/current enough;
3. cancellation/supersession not present;
4. permission still valid;
5. budget reservation still valid;
6. destination state/branch unchanged;
7. schema versions still accepted.

Create a CommitIntent first, perform the external effect, reconcile its external ID,
then finalize the event/state transition.

A long-running agent result is evidence; it is not permanent authority to write later.
