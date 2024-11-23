# Blockchain DevOps Tools

<p align="center">
    <img src="res/eth_logo.png" alt="Ethereum Foundation Logo" width="300"/>
    <img src="res/cosmos_logo.png" alt="Cosmos Network Logo" width="300"/>
    </p>

Open-source collection of tools for blockchain operations and monitoring.

## Tools

📊 Arbitrum sequencer feed parsing  
A tool for monitoring and processing Arbitrum sequencer feed data.

🗂️ Detect archive node  
Find archive nodes from a list of websocket endpoints.

🔎 Block height comparison - your node vs. public RPC  
A monitoring feature for Gatus to support fetching latest block diff between local and Public RPC.

✍🏻 Generate a signed TX  
Generate a signed transaction for a given chain and private key.

🪪 Generate multiple wallets from same seed  
Generate multiple wallets from a given seed phrase.

🔐 Convert mnemonic to a private key  
Create a private key from a given mnemonic.

👯‍♀️ Find network peers, recursivley  
Iterate over your peers, and run admin_peers to find theirs, recursivley.

⏱️ Measure time to fetch txpool_content  
Calculate the time taken to fetch the txpool content from a list of endpoints.

🧱 Get latest eth_blockNumber from multiple endpoints  
Get the latest block from a list of endpoints and verify if they are in sync.

🖥️ Monitor funds on multiple wallets and networks  
Monitoring tool to check the funds of different wallets on several blockchains.

💿 Extend LVM VG  
Instructions to extend LVM on your node with a new attached disk.

🔄 Nginx - reverse proxy for RPC and WS  
Install and configure Nginx as reverse proxy with RPC and WS locations and SSL support.

🎯 Ansible playbooks (various purposes)  
A collection of Ansible playbooks for managing blockchain nodes operations.

⏬ Snapshot handling tips and commands  
A collection of Ansible playbooks for managing blockchain nodes operations.

## Node operations best practices

- Setup [2FA for SSH authentication](https://ubuntu.com/tutorials/configure-ssh-2fa#1-overview) using PAM and Google authenticator (in resources)
- Use system user accounts for each component - principal of least privilege
- Protect against DDoS spam of the p2p port of the node - use [sentry nodes](https://forum.cosmos.network/t/sentry-node-architecture-overview/454/3) and allow the validator to communicate only with the trusted peers you set up
- Make sure the node is not an easy target for fingerprinting node infrastructure
- Use uptime monitoring with alerting to see that you node is online and also has enough RAM/disk/CPU etc.
- Do not manage your node from root, use a dedicated app user with required permissions only
- SSH access: disable root, disable password login, allow ssh key login, allow office IP
- Never hard code the private key in any script
- Implement rate limit via reverse proxy to limit DDoS attack surface
- Regularly run an nmap scan on your infrastructure of nodes and see what ports are open and what data can be extracted from the nodes
- Dont use ufw if using docker, since docker is using iptables and it will be above the rules of ufw
- Run [lynis](https://cisofy.com/lynis/) audit system and make sure you get a score of above 80
- [Support for ban](https://github.com/fail2ban/fail2ban) of multiple failed SSH attempts (fail2ban)
- Make sure firewall rules are set up
- Allow access to RPC/WS only over reverse proxy with SSL and basic_auth, use non standard DNS names to reduce scanning surface
- Make sure to setup the moniker to a generic name, not something that will reveal the owner or the infrastructure of the node, if the moniker is unset it will default to using the hostname which can also be too revealing for attackers
- Dont include a too-specific version name in your node, for example, if it has v1.2-mev1 it makes sense to understand it is a validator
- Use a ledger or any other physical wallet stored in a bank that is accessible 24/7
- Use WireGuard Mesh VPN or VPCs if running on AWS to allow your single-sign or co-sign validators to communicate with one another securely
- When using the client to run your node, prefer to download the GitHub source code of the client and built it locally instead of downloading pre-built binaries
- In case of urgent handling, better to miss a few blocks and risk downtime slashing and have enough time to research instead of making a mistake and double sign and get slashing for you delegators (you are allowed to miss 13 hours of blocks in Cosmos before risking downtime slashing)
- Sometimes in Cosmos, it is good practice just to delete the priv key, you can do so by renaming private state files to .old suffix (using a script)
- DR: Have your keys backed up in a very secure setup
- [VeraCrypt](https://veracrypt.eu/en/Beginner%27s%20Tutorial.html) file container to securely save keys
- Use monitoring to check performance of validators - e.g. [tenderduty](https://github.com/blockpane/tenderduty)
- Utilize DVT if running your validator on Ethereum
- Horcrux - validators can create multiple instances of their node, each functioning as an independent entity with the same validator identity and voting power. These individual instances are often referred to as “Horcruxes.”
- Use [Cosmovisor](https://docs.cosmos.network/main/build/tooling/cosmovisor) when working with Cosmos nodes
- Use [tmkms](https://github.com/iqlusioninc/tmkms) for Cosmos nodes - a separate process which extracts signing logic from your validator node and can run separately from your validator host
- It is possible to never store identity key on the filesystem of the server
  - The downside to this approach is that the key must be added to the running validator at startup
    - Automatic restarts from systemd will not work
    - Increases operational overhead

## Terminology

- **WS**: WebSockets - a communication protocol that provides full-duplex communication channels over a single TCP connection
- **JSON RPC**: RPC calls using JSON to query your node ([docs](https://ethereum.org/en/developers/docs/apis/json-rpc/))
- **P2P**: Peer-to-Peer, those are the nodes that are connected to your node and share blocks and transactions with you, also help you sync
- **Syncing**: The process of your node downloading the blockchain data from the network to catch up with the latest network consensus
- **LVM**: Logical Volume Manager - used to manage disk space in a flexible way, usually used in nodes since data increases over time
- **Mempool**: Memory Pool - a set of unconfirmed transactions in a blockchain network waiting to be included in a block, some networks allow this functionality, some don't
- **Data dir**: Data directory - where the blockchain data is stored (usually can be found under `~/.network_name`)
- **Moniker**: A name that identifies a node in the network
- **Horcrux**: A term used in Cosmos to describe multiple instances of a validator node, each functioning as an independent entity with the same validator identity and voting power
- **Validator**: A node that participates in the consensus process of a blockchain network and proposes and validates new blocks
- **Sequencer**: A node that orders transactions in a rollup chain, usually centralized, but can be decentralized (e.g. Metis)
- **Archive node**: A node that stores all historical data of the blockchain, useful for querying historical data
- **Full node**: Like archive node, but implements pruning and does not store ALL historical data
- **Consensus client**: A node that participates in the consensus process of a blockchain network
- **Execution client**: A node that processes transactions and smart contracts
- **TPS**: A lousy but sometimes useful metric that networks like to flex, # of transactions per second (lousy since no standard and 1 tx can be more compute heavy than another)

## DVT

- If a validator private key is compromised, an attacker can control the validator, potentially leading to slashing or the loss of the staker's ETH. (validator key will not allow attacker to withdraw funds but can hurt the validator by acting wrongly and getting the validator slashed). DVT can help mitigate this risk,
- Stakers participate in staking while keeping the validator private key offline
  - This is achieved by encrypting the original, full validator key and then splitting it into key shares
  - The key shares live online and are distributed to multiple nodes which enable the distributed operation of the validator
- A DVT solution contains the following components:
  - Shamir's secret sharing - Validators use key shares that are combined to a single aggregated key (signature). In DVT, the private key for a validator is the combined BLS signature of each operator in the cluster. (demo in resources)
  - Threshold signature scheme - Determines the number of individual key shares that are required for signing duties, e.g., 3 out of 4.
  - Distributed key generation (DKG) - Cryptographic process that generates the key shares and is used to distribute the shares of an existing or new validator key to the nodes in a cluster.
  - Multiparty computation (MPC) - The full validator key is generated in secret using multiparty computation. The full key is never known to any individual operator—they only ever know their own part of it (their "share").
  - Consensus protocol - The consensus protocol selects one node to be the block proposer. They share the block with the other nodes in the cluster, who add their key shares to the aggregate signature. When enough key shares have been aggregated, the block is proposed on Ethereum.

## DevOps initiatives

- Export node metrics to Prometheus and setup alerts for important metrics such as block height, peers, etc.
- Create a Docker compose for the node running (if performance is not an issue)
- Development environment in a click, sandboxed, on cloud or local
- Fork management - practice on how forks are going to look like, mimic a situation of a lack of consensus and a need to fork to a new blockchain
- Logging and tracing - use APM and publish client logs to New Relic
- Set up alerts and notifications to Slack based on occurrences of specific messages or log message severity in the logs (e.g. “panic”)
- CI security tools - use code coverage tools and SAST to catch security issues before they are committed
- CI tools - use linting and formatting enforcers and checkers like rustfmt/clippy via precommit, so pushed code is aligned with best standards
- Create a status page to show the status of the network in the public testnet (Atlassian status page)
- Create a block explorer for the testnet using blockscout/BigDipper (for both EVM and Cosmos-based chains)
- Automated testing suite, create E2E tests to be run on every commit to make sure we adhere to security standards, catch end cases and avoid regression in the development phase

## Resources

- [Validator Security: Information Leaks](https://www.youtube.com/watch?v=5MKV7EDJiS4)
- [Security Best Practices for your ETH staking validator node | CoinCashew](https://www.coincashew.com/coins/overview-eth/archived-guides/guide-or-how-to-setup-a-validator-on-eth2-mainnet/part-i-installation/guide-or-security-best-practices-for-a-eth2-validator-beaconchain-node)
- [Pulse chain validator security](https://github.com/rhmaxdotorg/pulsechain-validator?tab=readme-ov-file#security)
- [What are hardware security modules (HSM), why we need them and how they work.](https://www.youtube.com/watch?v=szagwwSLbXo)
- [DVT](https://ethereum.org/en/staking/dvt/)
- [BLS key shares demo app](https://iancoleman.io/shamir/)
- [Sentry node](https://forum.cosmos.network/t/sentry-node-architecture-overview/454/3)
- [Security best practices for a Cosmos validator](https://medium.com/coinmonks/security-best-practices-for-a-cosmos-validator-78f17c49c66c)
- [Horcrux setup](https://medium.com/@stanisloe/horcrux-ha-signing-with-quark-1-neutron-testnet-64c79bace514)
- [Horcrux explanation by Todd G](https://blockpane.medium.com/an-overview-of-block-panes-validator-architecture-8d7ace1e2140)
- <https://www.coincashew.com/coins/overview-eth/archived-guides/guide-or-how-to-setup-a-validator-on-eth2-mainnet/part-i-installation/guide-or-security-best-practices-for-a-eth2-validator-beaconchain-node>
- [SSH 2FA](https://ubuntu.com/tutorials/configure-ssh-2fa#1-overview)
- [TextBelt - Send SMS message to manager on every SSH login](https://textbelt.com/)
- [Solana Validator Education - Security Best Practices](https://www.youtube.com/watch?v=ORYNQrBcT0g)
- [Running Docker Containers as a Non-root User with a Custom UID / GID](https://www.youtube.com/watch?v=sXfaogNlc7Y&t=7s)

## Contributing

To contribute to this project, please follow the steps below:

1. **Fork the repository**

2. **Clone the forked repository**:

    ```bash
    git clone https://github.com/your-username/blockchain_devops_tools.git
    ```

    - Replace `your-username` with your GitHub username.

3. **Create a new branch**: Navigate to the repository directory and create a new branch:

    ```bash
    git checkout -b feature/feature-name
    ```

    Replace `feature-name` with a descriptive name.

4. **Make your changes**: Implement your changes.

5. **Commit your changes**: Commit with a descriptive message:

    ```bash
    git commit -am 'Add feature: description'
    ```

6. **Push to the branch**: Push your changes:

    ```bash
    git push origin feature/feature-name
    ```

7. **Create a Pull Request**

Thank you for contributing! 🎉
