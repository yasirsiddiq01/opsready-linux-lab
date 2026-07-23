"""Reviewed simulated outputs for the Guided command explorer.

The catalogue contains concise teaching metadata. This module supplies command-
specific output so learners do not see generic repeated placeholders. Outputs
are synthetic and never come from the hosting system.
"""

from __future__ import annotations

from typing import Any

_OUTPUTS: dict[str, str] = {
    "cd": "(no stdout; exit status 0)\nCurrent directory: /var/log",
    "tree": "/etc/nginx\n├── nginx.conf\n├── conf.d\n│   └── default.conf\n└── sites-enabled\n    └── default",
    "stat": "  File: /etc/hosts\n  Size: 186\tBlocks: 8\tIO Block: 4096 regular file\nAccess: (0644/-rw-r--r--) Uid: (0/root) Gid: (0/root)\nModify: 2026-07-14 10:12:04 +0000",
    "file": "/usr/bin/python3: symbolic link to python3.12",
    "touch": "(no stdout; exit status 0)\nCreated or updated: /tmp/opsready-test.txt",
    "mkdir": "(no stdout; exit status 0)\nCreated directory: /tmp/opsready/logs",
    "rmdir": "(no stdout; exit status 0)\nRemoved empty directory: /tmp/opsready/empty",
    "cp": "(no stdout; exit status 0)\nCopied /etc/nginx to /tmp/nginx-backup preserving metadata",
    "mv": "(no stdout; exit status 0)\nRenamed /tmp/report.tmp to /tmp/report.txt",
    "rm": "remove regular empty file '/tmp/opsready-test.txt'? y\n(no stdout after confirmation; exit status 0)",
    "ln": "(no stdout; exit status 0)\n/usr/local/bin/app-current -> /opt/app/current",
    "readlink": "/usr/bin/python3.12",
    "basename": "error.log",
    "dirname": "/var/log/nginx",
    "realpath": "/var/log/syslog",
    "locate": "/etc/nginx/nginx.conf\n/usr/share/man/man5/nginx.conf.5.gz",
    "less": "Jul 14 17:40:11 server systemd[1]: Started api.service.\nJul 14 17:41:02 server api[2911]: request completed status=200\nJul 14 17:43:11 server api[2911]: ERROR database timeout\n/var/log/syslog (END)",
    "head": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin\nsys:x:3:3:sys:/dev:/usr/sbin/nologin\nappuser:x:1001:1001:Application User:/opt/app:/bin/bash",
    "wc": "127 /var/log/syslog",
    "sort": "101 postgres 1.1\n2142 appuser 4.2\n1842 www-data 6.8\n3312 java 12.4",
    "uniq": "     87 200\n     11 404\n      4 502\n      1 503",
    "cut": "root\ndaemon\nwww-data\nappuser\nstudent",
    "paste": "root\t/bin/bash\nwww-data\t/usr/sbin/nologin\nappuser\t/bin/bash",
    "tr": "error",
    "tee": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        40G   28G   10G  74% /\nOutput also copied to /tmp/disk-report.txt",
    "diff": "--- nginx.conf\t2026-07-14 10:10:00 +0000\n+++ nginx.conf.new\t2026-07-14 10:12:00 +0000\n@@ -2,1 +2,1 @@\n-worker_connections 1024;\n+worker_connections 4096;",
    "cmp": "(no stdout; exit status 0 — files are identical)",
    "sed": "Port 22\nPermitRootLogin no\nPasswordAuthentication no\nPubkeyAuthentication yes\nUsePAM yes",
    "awk": "root /bin/bash\nsystemd-network /usr/sbin/nologin\nwww-data /usr/sbin/nologin\nappuser /bin/bash\nstudent /bin/bash",
    "xargs": "access.log\nauth.log\nerror.log\nsyslog",
    "ip addr": "lo               UNKNOWN        127.0.0.1/8 ::1/128\neth0             UP             10.0.2.15/24 fe80::a00:27ff:fe4e:66a1/64",
    "ip route": "1.1.1.1 via 10.0.2.2 dev eth0 src 10.0.2.15 uid 1000\n    cache",
    "ip neigh": "10.0.2.2 dev eth0 lladdr 52:54:00:12:35:02 REACHABLE\n10.0.2.20 dev eth0 lladdr 52:54:00:98:1a:04 STALE",
    "tracepath": " 1?: [LOCALHOST]                      pmtu 1500\n 1:  10.0.2.2                         0.412ms\n 2:  198.51.100.1                     7.181ms\n 3:  example.com                     18.640ms reached",
    "wget": "Spider mode enabled. Check if remote file exists.\nHTTP/1.1 200 OK\nContent-Type: application/json\nRemote file exists.",
    "nc": "Connection to app.example.com (203.0.113.42) 443 port [tcp/https] succeeded!",
    "ethtool": "Settings for eth0:\n\tSpeed: 1000Mb/s\n\tDuplex: Full\n\tAuto-negotiation: on\n\tLink detected: yes",
    "tcpdump": "17:42:01.184223 IP 10.0.2.15.51244 > 203.0.113.42.443: Flags [S], seq 1421\n17:42:01.201940 IP 203.0.113.42.443 > 10.0.2.15.51244: Flags [S.], ack 1422",
    "nmap": "PORT    STATE  SERVICE\n22/tcp  open   ssh\n80/tcp  closed http\n443/tcp open   https\nNmap done: 1 IP address (1 host up) scanned",
    "traceroute": " 1  10.0.2.2       0.421 ms\n 2  198.51.100.1   7.104 ms\n 3  203.0.113.42  18.622 ms",
    "whoami": "appuser",
    "id": "uid=1001(appuser) gid=1001(appgroup) groups=1001(appgroup),1002(operators)",
    "who": "appuser  pts/0  2026-07-14 17:20 (203.0.113.20)\nstudent  pts/1  2026-07-14 17:44 (10.0.2.30)",
    "passwd": "appuser P 2026-06-30 0 99999 7 -1",
    "useradd": "(no stdout; exit status 0)\nCreated user analyst with home /home/analyst and shell /bin/bash",
    "usermod": "(no stdout; exit status 0)\nAdded analyst to supplementary group sudo",
    "groupadd": "(no stdout; exit status 0)\nCreated group appoperators",
    "groups": "appuser : appgroup operators docker",
    "pgrep": "2101 nginx: master process /usr/sbin/nginx\n2103 nginx: worker process",
    "pkill": "(no stdout; exit status 0)\nSIGHUP delivered to matching nginx processes",
    "kill": "(no stdout; exit status 0)\nSIGTERM delivered to PID 2142",
    "killall": "worker-process(3312): terminated by signal 15",
    "nice": "gzip started with niceness 10 (PID 4451)",
    "renice": "2142 (process ID) old priority 0, new priority 5",
    "nohup": "nohup: ignoring input and appending output to 'worker.log'\n[1] 4512",
    "which": "/usr/bin/python3",
    "type": "ls is aliased to `ls --color=auto'\nls is /usr/bin/ls",
    "whereis": "nginx: /usr/sbin/nginx /usr/lib/nginx /etc/nginx /usr/share/man/man8/nginx.8.gz",
    "jobs": "[1]+  4512 Running                 nohup python worker.py > worker.log 2>&1 &",
    "bg": "[1]+ nohup python worker.py > worker.log 2>&1 &",
    "fg": "nohup python worker.py > worker.log 2>&1\n^C",
    "blkid": '/dev/sdb1: UUID="4d50b8c2-9ef9-4d8f-a192-3cf0867a19ab" TYPE="ext4" PARTUUID="b12f-02"',
    "mount": "/dev/sdb1 on /data type ext4 (rw,relatime)",
    "umount": "(no stdout; exit status 0)\n/mnt/backup is no longer mounted",
    "findmnt": "TARGET SOURCE    FSTYPE OPTIONS\n/var   /dev/sda1 ext4   rw,relatime",
    "fdisk -l": "Disk /dev/sda: 80 GiB, 85899345920 bytes\nDevice      Start       End   Sectors Size Type\n/dev/sda1    2048 167770111 167768064  80G Linux filesystem",
    "parted -l": "Model: Virtual Disk (scsi)\nDisk /dev/sda: 85.9GB\nPartition Table: gpt\nNumber  Start   End     Size    File system  Name  Flags\n 1      1049kB 85.9GB  85.9GB  ext4         root",
    "pidstat": "17:48:10 UID   PID  %usr %system %CPU Command\n17:48:11 1001 2142  41.0    5.0 46.0 python\nAverage:  1001 2142  39.5    4.5 44.0 python",
    "mpstat": "17:48:10 CPU %usr %sys %iowait %idle\n17:48:11 all 34.2 8.1 2.0 55.7\n17:48:11   0 46.0 9.0 1.0 44.0",
    "sar": "17:48:10 %user %system %iowait %idle\n17:48:11  34.20    8.10    2.00 55.70\nAverage:  35.10    7.80    2.30 54.80",
    "perf stat": "       1,843.22 msec task-clock\n   5,921,402,118 cycles\n   8,410,229,004 instructions\n       2.002 seconds time elapsed",
    "time": 'Command being timed: "gzip large.log"\nUser time (seconds): 1.42\nSystem time (seconds): 0.18\nMaximum resident set size (kbytes): 4280\nElapsed time: 0:01.63',
    "auditctl": "-w /etc/passwd -p wa -k identity\n-a always,exit -F arch=b64 -S execve -k process_exec",
    "ausearch": 'time->Tue Jul 14 17:31:40 2026\ntype=USER_LOGIN msg=audit(1784050300.214:921): pid=812 uid=0 acct="appuser" hostname=203.0.113.20 res=success',
    "sestatus": "SELinux status:                 enabled\nCurrent mode:                   enforcing\nPolicy from config file:        targeted",
    "getenforce": "Enforcing",
    "restorecon": "Would relabel /var/www/html/index.html from unconfined_u:object_r:user_home_t:s0 to system_u:object_r:httpd_sys_content_t:s0",
    "chgrp": "(no stdout; exit status 0)\nGroup for /opt/app/config.yml changed to appgroup",
    "umask": "0027",
    "getfacl": "# file: srv/shared/report.csv\n# owner: appuser\n# group: appgroup\nuser::rw-\ngroup::r--\nother::---",
    "setfacl": "(no stdout; exit status 0)\nAdded ACL entry user:analyst:r-- to /srv/shared/report.csv",
    "sysctl": "net.ipv4.ip_forward = 0",
    "lsmod": "Module                  Size  Used by\nbr_netfilter           32768  0\nbridge                 421888  1 br_netfilter",
    "modinfo": "filename: /lib/modules/6.8.0/kernel/net/bridge/br_netfilter.ko\nlicense: GPL\ndescription: Linux bridge netfilter module",
    "modprobe": "insmod /lib/modules/6.8.0/kernel/net/llc/llc.ko\ninsmod /lib/modules/6.8.0/kernel/net/bridge/bridge.ko\ninsmod /lib/modules/6.8.0/kernel/net/bridge/br_netfilter.ko",
    "gzip": "(no stdout; exit status 0)\nCreated application.log.gz and retained application.log",
    "gunzip": "(no stdout; exit status 0)\nCreated application.log and retained application.log.gz",
    "zip": "  adding: etc/nginx/nginx.conf (deflated 42%)\n  adding: etc/nginx/conf.d/default.conf (deflated 38%)",
    "unzip": "Archive: config-backup.zip\n Length  Date       Time  Name\n   1440  2026-07-14 10:10 etc/nginx/nginx.conf\n    812  2026-07-14 10:10 etc/nginx/conf.d/default.conf",
    "crontab": "15 2 * * * /usr/local/bin/backup\n*/5 * * * * /usr/local/bin/health-check",
    "at": "warning: commands will be executed using /bin/sh\njob 17 at Tue Jul 14 23:30:00 2026",
    "flock": "report generated; lock /run/report.lock released",
    "dmesg": "[Tue Jul 14 17:35:18 2026] eth0: Link is Up - 1Gbps/Full\n[Tue Jul 14 17:43:09 2026] EXT4-fs warning: mounting fs with errors",
    "logger": "(no stdout; exit status 0)\nMessage submitted to syslog with tag opsready",
    "logrotate": "reading config file /etc/logrotate.conf\nreading config info for /var/log/nginx/*.log\nrotating pattern: /var/log/nginx/*.log weekly (4 rotations)\nlog does not need rotating",
    "strace": 'read(3, "GET /health HTTP/1.1\\r\\n", 4096) = 22\nconnect(7, {sa_family=AF_INET, sin_port=htons(5432)}, 16) = -1 ETIMEDOUT\nwrite(2, "database timeout\\n", 17) = 17',
    "watch": "Every 2.0s: ss -s\nTotal: 412\nTCP:   238 (estab 42, closed 173, orphaned 0, timewait 22)",
    "coredumpctl": "TIME                         PID UID GID SIG COREFILE EXE\nTue 2026-07-14 17:31:12 CEST 3312 1001 1001 11 present /opt/app/worker",
    "docker inspect": '[\n  {"Name":"/app-container","State":{"Status":"running","Pid":4312},"Config":{"Image":"app:latest"}}\n]',
    "docker stats": "CONTAINER ID   NAME            CPU %   MEM USAGE / LIMIT     NET I/O\na34f91c2d110   app-container   2.40%   96MiB / 7.8GiB       1.2MB / 840kB",
    "docker exec": "uid=1001(appuser) gid=1001(appgroup) groups=1001(appgroup)\nPID USER     COMMAND\n  1 appuser  python app.py\n 27 appuser  sh -c id && ps",
    "sudo": "Matching Defaults entries for appuser on opsready-lab:\n    env_reset, secure_path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin\nUser appuser may run the following commands:\n    (root) /usr/bin/systemctl status *",
    "su": "Last login: Tue Jul 14 17:20:03 CEST on pts/0\nappuser@opsready-lab:~$",
    "ulimit": "real-time non-blocking time  (microseconds, -R) unlimited\nopen files                          (-n) 1024\nmax user processes                  (-u) 4096\nstack size              (kbytes, -s) 8192",
    "prlimit": "RESOURCE   DESCRIPTION              SOFT  HARD UNITS\nNOFILE     max number of open files 1024  4096 files\nNPROC      max number of processes  4096  4096 processes",
    "scp": "report.txt                                    100% 1024KB  12.8MB/s   00:00",
    "rsync": "sending incremental file list\n./\ndata.db\nlogs/app.log\nsent 1,048,576 bytes  received 2,048 bytes  total size 8,412,220 (DRY RUN)",
    "nft": "table inet filter {\n chain input {\n  type filter hook input priority filter; policy drop;\n  tcp dport { 22, 443 } ct state new accept\n }\n}",
    "iptables": "Chain INPUT (policy DROP 0 packets, 0 bytes)\nnum pkts bytes target prot opt in out source destination\n1   128  9421 ACCEPT tcp -- * * 0.0.0.0/0 0.0.0.0/0 tcp dpt:443",
    "uname": "Linux opsready-lab 6.8.0-virtual #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux",
    "hostname": "opsready-lab.example.internal",
    "date": "2026-07-14T17:48:10+02:00",
}


def guided_output_for(command: str, example: str, fallback: Any) -> str:
    """Return command-specific reviewed synthetic output."""

    output = _OUTPUTS.get(command)
    if output is not None:
        return output
    text = str(fallback).strip()
    if text:
        return text
    return f"(simulated command completed)\nCommand: {example}"


def overridden_commands() -> frozenset[str]:
    return frozenset(_OUTPUTS)
