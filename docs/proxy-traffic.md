# Proxy traffic controls

Android system-proxy traffic passes through `damru/proxy_bridge.py` before the
authenticated upstream proxy. Optional host filtering works even when browser
capture does not attach Chrome DevTools. It does not decrypt HTTPS traffic.

Set `DAMRU_PROXY_POLICY_FILE` to a local JSON file before starting bridges:

```json
{
  "name": "telemetry-comparison",
  "blocked_domains": ["browser-intake-datadoghq.com", "googletagmanager.com"],
  "allowed_domains": ["shopee.com.br", "smiles.com.br"]
}
```

Use hostnames without `:443`. A domain matches itself and its subdomains, so the
second entry includes `www.googletagmanager.com`. Allowed domains take precedence.
No filtering is enabled when the environment variable is absent. A configured
but missing or malformed policy rejects a new connection instead of silently
disabling the requested filter.

The bridge rejects a blocked CONNECT locally before connecting to the upstream
proxy. Replace the policy file atomically to change new-connection behavior.
Existing tunnels keep their original decision; finish captures and close their
browser connections before comparing policies. The policy applies to the bridge,
so use separate bridges when clients need different policies.

Set `DAMRU_PROXY_METRICS_DIR` for a bounded traffic measurement. Daily JSONL files
contain destination hostname, policy name, block count events, bridge port,
timestamps and bytes sent/received. They contain no URLs, headers, credentials or
response bodies. Records are emitted when connections finish, including error
paths. For HTTP upstreams, counters include CONNECT negotiation; SOCKS negotiation
bytes are excluded. These are transport measurements, not the provider's billing
meter. Traffic that bypasses this bridge is not measured.

Leave metrics disabled for routine operation unless retention is managed by the
operator. Restrict the directory to the deployment account and remove old test
logs after retaining aggregated evidence. A logging disk error does not change
capture behavior.

Validate schema and semantic parity before enabling blocking on normal traffic.
Tag Manager can load scripts used by the target site. Datadog can also be routed
through a first-party endpoint, which a hostname-only filter cannot distinguish
from required same-host traffic. Do not broadly block a capture/API host to reach
those endpoints. See [Datadog's intake documentation](https://docs.datadoghq.com/real_user_monitoring/)
and [first-party proxy behavior](https://docs.datadoghq.com/real_user_monitoring/guide/proxy-rum-data/).
