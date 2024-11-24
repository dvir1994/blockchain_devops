# Snapshot Download Tips and Commands

To save on space, you can extract the content of the archive on the fly (instead of download and extraction)
Another option to save on disk is to setup a temp machine with large disk space, donwload the archive, extract it and then rsync to destination node

Single-threaded

```bash
# Set the URL of the snapshot
URL="<paste the URL of the snapshot>"

# Download and extract the snapshot
wget -O- $URL | lz4 -dc | tar -xaf -  # For lz4-compressed archives
wget -O- $URL | zstd -dc | tar -xaf - # For zstd-compressed archives
```

Multi-threaded

```bash
# Install aria2c
sudo apt update && sudo apt install aria2

# Set the URL of the snapshot, take note of the file extension
URL="<paste the URL of the snapshot>"
FILENAME=$(basename $URL)

# Download and extract the snapshot
aria2c -x 8 -s 8 $URL

# Decompress and extract the snapshot
lz4 -dc $FILENAME | tar -xaf -      # For lz4-compressed archives
zstd -dc $FILENAME -T0 | tar -xaf - # For zstd-compressed archives
```

# Tips

- usually it is the practice to save the data dir in a user dedicated to running the node, under ~/.network_name
- make sure to take a regular backup of your data dir
- use RAID if possible to help with disk corruption cases
- monitor the disk space on your node and setup alerts (Slack, PagerDuty)
- make sure you set correct permissions for the datadir
- use pruning for you node if not running an archive node
- use logrotate to save on disk space, with retention and zip archiving
