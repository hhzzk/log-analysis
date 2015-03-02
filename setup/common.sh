#!/bin/bash

# Check argument must be [-d] hostname@ip:[path]
check_arg()
{
  # Check argument number
   if [ -z "$2" ]
    then
        arg=$1
    else
        arg=$2
        if [[ $1 != "-d" ]]
        then
            echo "error : invalid argument"
            exit
        fi
    fi

    # Check argument is valid
    reg="^\w\+@[0-9]\{1,3\}\.\([0-9]\{1,3\}\.\)\{2\}[0-9]\{1,3\}:.*$"
    echo $arg | grep  $reg >/dev/null
    if ! test  $? -eq 0
    then
        echo "error : invalid argument"
        exit
    fi
}

# Check password.if right return 0, wrong return 1 or 2
check_passwd()
{
    host_name=$1
    ip_addr=$2
    password=$3
    expect -c "
    set timeout 2
    spawn ssh -t $host_name@$ip_addr echo
    expect \"*assword\"
    send \"${password}\r\"
    expect {
            eof {exit 0}
            timeout {exit 1}
            \"*ermission denied*\" {exit 2}
            }
    eof
    "
    return $?
}

#chec dir and modify
check_dir()
{
    dir=$1
    if ! [ -z "$dir" ]
    then
        if [ ${dir:0:1} != "/" ]
        then
            dir='/'$dir
        fi

        if [ ${dir:0-1:1} != "/" ]
        then
            dir=$dir'/'
            #dir=${dir#*/}
        fi
    else
        dir='/'
    fi

    echo "$dir"
}

#host_name=$1;ip_addr=$2;cmd=$3;password=$4
ssh_cmd()
{
    host_name=$1
    ip_addr=$2
    cmd=$3
    password=$4

    expect -c "
    set timeout -1
    spawn ssh -t $host_name@$ip_addr $cmd
    expect {
        \"*assword\" {send \"${password}\r\";exp_continue;}
        \"yes/no\" {send \"yes\r\"; exp_continue;}
        \"y/n\" {send \"y\r\"; exp_continue;}
        \"Y/n\" {send \"Y\r\"; exp_continue;}
        \"Y/N\" {send \"Y\r\"; exp_continue;}
        \"YES/NO\" {send \"YES\r\"; exp_continue;}
        eof {exit 0}
       }
    eof"
}

