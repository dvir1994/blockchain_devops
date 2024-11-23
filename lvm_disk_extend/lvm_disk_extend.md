# Extend LVM Disks

## Instructions

1. Get a list of disks with `lsblk`

    You should see for example both `nvme3n1` and `nvm1n1` are both part of `lvm` as `vg0-root`.
    The only disk thats not part of lvm for example might be `nvme2n1`, you should see it is not related to any LVM configuration. This is the one we will be extending LVM with.

2. Get the volume group name by running `sudo lvs`

    You might see a volume group name like `vg0`

3. Get the name of the root filesystem with: `df -h`

    Look for a name like `/dev/mapper/vg0-root`

4. Find out where `nvme2n1` (the disk to extend) is mounted. There are a few ways to do so, for example you can run `sudo fdisk -l`

    You might see that its mounted at `/dev/nvme2n1`

5. Create a physical volume (PV) from the disk `sudo pvcreate /dev/nvme2n1`

    ```bash
    $ sudo pvcreate /dev/nvme2n1
    
    # Output: Physical volume "/dev/nvme2n1" successfully created
    ```

6. Add the newly created PV to the lvm volume group (the volume group name found on step 2) `sudo vgextend vg0 /dev/nvme2n1`

    ```bash
    $ sudo vgextend vg0 /dev/nvme2n1
    
    # Output: Volume group "vg0" successfully extended
    ```

7. Extend the existing `/dev/vg0/root` (from step 1) with: `sudo lvm lvextend -l +100%FREE /dev/vg0/root`

    ```bash
    $ sudo lvm lvextend -l +100%FREE /dev/vg0/root
    
    # Output: Size of logical volume vg0/root changed from <1.83 TiB (478653 extents) to <3.69 TiB (967031 extents).
    # Output: Logical volume vg0/root successfully resized.
    ```

8. Finally enlarge the root filesystem in the root volume with: `sudo resize2fs -p /dev/mapper/vg0-root` (from step 3)

    ```bash
    $ sudo resize2fs -p /dev/mapper/vg0-root
    
    # Output: Filesystem at /dev/mapper/vg0-root is mounted on /; on-line resizing required
    # Output: old_desc_blocks = 234, new_desc_blocks = 473
    # Output: The filesystem on /dev/mapper/vg0-root is now 990239744 (4k) blocks long.
    ```

9. Finally run `df -h` to verify that the root filesystem was expanded

    You should see that the `dev/mapper/vg0-root`is bigger in size now.

## Commands only

```bash
# create
sudo pvcreate /dev/nvme2n1

# vgextend
sudo vgextend vg0 /dev/nvme2n1

# extend lvm
sudo lvm lvextend -l +100%FREE /dev/vg0/root /dev/nvme2n1

# resize root
sudo resize2fs -p /dev/mapper/vg0-root
```

## Debugging

```bash
# [ERROR] Can't open /dev/nvme1n1 exclusively.  Mounted filesystem?
# [SOLUTION] The drive has partitions. You must remove the partitions before trying to extend a volume
# Run the following
sudo fdisk /dev/nvme1n1
# New prompt, enter 'd'
Command (m for help): d
# New prompt, enter default, repeat until no more partitions (N is sum of partitions)
Partition number (1-N, default N):
# It will output partition N has been deleted. Now type p to see update
Command (m for help): p
# Now type w to write changes
Command (m for help): w
# Now it will output "The kernel still uses the old partitions. The new table will be used upon reboot"
sudo reboot
# Now to wait for the server to be up, ping the IP until it responds
ping IP
# Now that it is back, ssh in and run lsblk to verify changes
```

