# dnf-plugin-container
Update containers like you update packages.

**THIS IS A WORK IN PROGRESS**
In other words, this is a starting point for further work.


## WIP Assumptions

- It may not work and possibly do weird things :-P
- Only tested with system containers so far
- The atomic commands libraries are available in the same site-packages that dnf uses
- Updates always update all containers to the latest version for the installed tag


## Usage

**WARNING** This may break stuff!!

1. Create a path for plugins
2. Add ``pluginpath=$YOUR_NEW_PATH``
3. Place ``container.py``in $YOUR_NEW_PATH
4. Use ``dnf container``

### Example
```
$ sudo atomic containers list --no-trunc
   CONTAINER ID IMAGE  COMMAND         CREATED          STATE      BACKEND    RUNTIME
   aaaaz test:0.4.rc2 /usr/bin/run.sh 2017-10-18 09:17 failed     ostree     runc
$ sudo atomic images list
   REPOSITORY   TAG       IMAGE ID       CREATED            VIRTUAL SIZE   TYPE
   test   0.4.rc2   2848e6699c97   2017-10-17 17:34                  ostree
$ sudo dnf container check
Checking 1 local container(s) for updates
The following containers need updating:
        aaaaz

To update your containers use dnf containers update or, to update specific containers, the atomic command
Example: sudo atomic containers update aaaaz
$ sudo dnf container update -y
Checking 1 local container(s) for updates
The following containers need updating:
        aaaaz

To update your containers use dnf containers update or, to update specific containers, the atomic command
Example: sudo atomic containers update aaaaz
Pulling test:0.4.rc2 ...
Updating aaaaz ...
Extracting to /var/lib/containers/atomic/aaaaz.1
systemd-tmpfiles --remove /etc/tmpfiles.d/aaaaz.conf
systemctl daemon-reload
systemd-tmpfiles --create /etc/tmpfiles.d/aaaaz.conf
$ sudo atomic images list
   REPOSITORY   TAG       IMAGE ID       CREATED            VIRTUAL SIZE   TYPE
   test   0.4.rc2   aa3d7accac3b   2017-10-18 09:18                  ostree
$ sudo dnf container check
Checking 1 local container(s) for updates
No updates found
```

### Commands

#### check
Reports on containers which have updates available.

```
$ sudo dnf container check
Checking 1 local container(s) for updates
The following containers need updating:
        aaaaz

To update your containers use dnf containers update or, to update specific containers, the atomic command
Example: sudo atomic containers update aaaaz
```

#### update
Updates all system containers to the latest image for the installed tag.


```
$ sudo dnf container update -y
Checking 1 local container(s) for updates
The following containers need updating:
        aaaaz

To update your containers use dnf containers update or, to update specific containers, the atomic command
Example: sudo atomic containers update aaaaz
Pulling <test image> ...
Updating aaaaz ...
Extracting to /var/lib/containers/atomic/aaaaz.1
systemd-tmpfiles --remove /etc/tmpfiles.d/aaaaz.conf
systemctl daemon-reload
systemd-tmpfiles --create /etc/tmpfiles.d/aaaaz.conf
$
$ sudo dnf container check
Checking 1 local container(s) for updates
No updates found
```
