# Backup / Restore

Back up:
1. PostgreSQL
2. content-addressed artifact store
3. schemas/WorkflowSpecs
4. release/deployment config
5. secrets separately

Because artifacts are content-addressed, restore verification checks DB references against
actual digests.

Monthly restore test:
- restore DB into fresh environment;
- restore/sample artifacts;
- verify latest Merkle checkpoint;
- rebuild queue/read projections;
- run doctor.

A backup that has never been restored is not certified.
