# Pricing decision worksheet

The application does not publish a live price by default. Configure price labels only after deciding the paid feature boundary.

## Initial hypothesis to test

- Monthly: **EUR 8.99**
- Annual: **EUR 69**
- Free trial: none, because the Community edition is the free evaluation route
- Founding-user discount: optional 20% for the first year
- Lifetime plan: not recommended initially

These figures are hypotheses, not validated market prices.

## Evidence required before final pricing

- At least 10 users complete two or more sessions
- At least 5 users state which feature they would pay for
- Estimated monthly support effort per paid user
- Hosting and database cost per active user
- Assessment and content-maintenance workload
- Comparison with alternative Linux courses and interactive labs

## Configuration after approval

```toml
[commercial]
monthly_price_label = "€8.99/month"
annual_price_label = "€69/year"
```

The amount displayed by Lemon Squeezy checkout remains the authoritative amount.
