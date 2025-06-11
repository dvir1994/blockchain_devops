When getting the following error in OP based network,
```gap in the chain between ancients```

Steps for fix:
1. Stop geth
2. Take a backup of the data dir
    if using a docker volume for the data dir:
    ```cp /var/lib/docker/volumes/* ~/bup/TODAY_DATE/```
    if using a data dir on the file system
    ```cp data_dir_folder ~/bup/TODAY_DATE/```
3. Run a new alpine container and attach the datadir volume
    ```docker run -it -v soneium-node_op-geth-storage:/data alpine sh```
4. cd into the datadir volume chaindata
    ```cd /data/geth/chaindata/```
5. Delete all files in the folder other than the ancient dir
    ```rm -f *.sst MANIFEST* CURRENT OPTIONS* *.log LOCK```
6. Restart the node
    ```docker compose up -d --build```
    or if using a serivce
    ```systemctl stop service_name && systemctl start service_name```
