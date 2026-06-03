# Discovery Notes

Useful questions for a light automation discovery call:

- What manual task is repeated often enough to justify automation?
- What signal currently proves the job is complete?
- Which machine states create the most downtime?
- What safety interlocks must be visible to operators?
- Is the first goal labor relief, quality consistency, traceability, or throughput?
- Where should live status be consumed: HMI, dashboard, phone alert, or ERP/MES?

For this demo, the assumed cell is a cobot machine-tending station with part presence, safety gate, E-stop health, robot busy, fault code, cycle count, average cycle time, and downtime.
