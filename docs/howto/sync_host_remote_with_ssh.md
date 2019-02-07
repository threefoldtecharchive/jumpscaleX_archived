# Syncing host to remote machines

## (SSH from host)
1) **Create SSHKEY client instance**
    ```
    j.clients.sshkey.get(name=sshkey_test_name,
                        path=path_to_ssh_key)
    ```
    where
    - *path* : path to the ssh key
2) **Create SSH client** (opens ssh connection to remote machine)
    ```
    ssh_client_instance = j.clients.ssh.get(name=ssh_test_name,
                                            addr=remote_machine_IP,
                                            port=remote_machine_port,
                                            sshkey_name=sshkey_test_name) 
    ```
    where
    - *addr* : remote machine address
    - *port* : remote machine port
    - *sshkey_name* : name of sshkey client created

    To make sure the host and remote are connected:
    ```
    ssh_client_instance.isconnected
    ```
    if *True* then the ssh connection is alive, otherwise *False*

## (Sync host to remote)
3) **Create Syncer instance**
    ```
    syncer_client = j.tools.syncer.get(name=syncer_test,
                                       sshclient_name=ssh_test_name,
                                       paths=paths_list)  
    ```
    where
    - *paths_list* : list of paths to be synced
        Different paths can be given for the host and source.
        - Same paths for source and destination:
            ```
            paths_list = ["path1_in_source","path2_in_source"...]
            ```
        - Different paths for source and destination:
            ```
            paths_list = ["path1_in_source:path1_in_dest","path2_in_source:path2_in_dest"...]
            ```
    - *sshclient_name* : name of ssh client created

4) **Sync host to remote directories**  (continously monitor and sync when changes occur on host directory)
    ```
    syncer_client.sync()
    ```

