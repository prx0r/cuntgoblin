# Global commerce + country intelligence

Marketplaces are typed adapters with explicit country/market support, data-rights policy,
seller eligibility, fees, currencies and publish permissions.

## First adapters

- **Shopify:** query merchant-defined Markets dynamically.
- **Etsy:** authorized Open API v3 shop/listing management; shipping profiles encode origin/destination.
- **eBay:** marketplace IDs are first-class; offers are marketplace-specific.
- **Amazon:** SP-API is region/marketplace-aware; one app can be authorized across marketplaces.

## Country snapshot

```text
CountryMarketSnapshot:
  country_code
  observed_at
  currency
  marketplace_support[]
  category_demand[]
  price_distributions[]
  source_availability[]
  shipping_corridors[]
  tax_duty_status
  regulatory_flags[]
  locale/language
  confidence
  evidence_refs[]
```

The external Unignorant/global Oracle can publish snapshots through this contract.

## Arbitrage opportunity

```text
ArbitrageOpportunity:
  canonical_product_id
  source_market
  target_market
  source_price
  target_price
  fx_rate
  marketplace_fees
  payment_fees
  shipping_cost
  expected_return_cost
  tax_duty_estimate
  inventory_risk
  policy_eligible
  expected_contribution
  confidence
  freshness_deadline
```

Hard gate: expected contribution is UNKNOWN if a mandatory material cost is unknown.

Never implement geographic/account/platform restriction circumvention.
