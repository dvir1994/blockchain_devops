# Gaia Node Exporter

A Prometheus exporter for Cosmos SDK-based Gaia blockchain nodes that exposes various metrics about node status and peer connections.

## Metrics Exposed

The exporter provides the following metrics:

- `gaia_block_height`: Current block height of the node
- `gaia_block_time_drift_seconds`: Time difference between now and the latest block timestamp
- `gaia_peers_count`: Number of connected peers
- `gaia_version_by_peers`: Number of peers grouped by their node version

## Requirements

- Go 1.16 or later
- A running Gaia node with RPC endpoint accessible
- Prometheus server (for scraping metrics)

By default, the exporter connects to: <http://localhost:26657>

- Configure the endpoint otherwise if needed

Exporter metrics endpoint: `9100`
