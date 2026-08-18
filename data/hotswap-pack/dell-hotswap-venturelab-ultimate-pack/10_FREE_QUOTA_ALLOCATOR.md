# Free Capacity Allocation

Free inference is a scarce inventory problem when quotas reset.

## Do not treat every free token as identical

For each free route keep:

- remaining requests by window
- remaining tokens by window
- time to reset
- forecast factory demand until reset
- route quality by task cell

## Reservation

Before execution reserve estimated usage.

After execution reconcile actual usage and release unused reservation.

This prevents parallel Hermes workers from all believing the same last 100 free calls exist.

## Quota pressure

For each window:

```text
pressure =
forecast_eligible_demand_until_reset
/
max(remaining_capacity, epsilon)
```

Interpretation:
- < .67 abundant
- .67–1.0 tightening
- 1.0–1.5 scarce
- >1.5 very scarce

These are operational priors to calibrate.

## Shadow cost

A free call can have opportunity cost when a scarce high-quality free route might be
needed later.

Simple v1:

```text
shadow_fraction = clamp((pressure - .67) / .83, 0, 1)

quota_shadow_cost =
shadow_fraction
× cheapest_paid_replacement_cost
× priority_reservation_factor
```

Low-priority tasks receive a larger scarcity penalty on scarce premium free routes.

Release-critical tasks may use reserved premium free quota.

## Reserve bands

Optional explicit policy:

```text
abundant:
  any task
tightening:
  routine+
scarce:
  important+
very_scarce:
  release_gate/production unless no substitute
```

## Multiple quota dimensions

A route is available only when ALL relevant dimensions have capacity:

- RPM
- TPM
- requests/day
- tokens/day
- requests/5h
- weekly token caps
- provider-specific account limits

Never convert these to one fake RPD.

## Unknown quota

If Dell says free but quota is unknown:

- route may be used for low-risk exploratory work if policy allows;
- mark uncertainty;
- do not promise workload completion;
- learn from 429/quota events.
