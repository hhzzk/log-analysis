#!/bin/bash
. ./common.sh --source-only

check_arg $1

arg=$1
host=$(echo $arg|awk -F '[@:]' '{print $1 }')
ip=$(echo $arg|awk -F '[@:]' '{print $2 }')
dir=$(echo $arg|awk -F '[@:]' '{print $3 }')
dir=$(check_dir $dir)
install_dir=/home/${host}${dir}

# Input password
while :
do
    echo -n "Please input remote host password : "
    read -s password
    echo -e "\r"
    check_passwd ${host} ${ip} ${password} > /dev/null
    if [ $? == 0 ]
    then
        break
    else
        echo "WRONG PASSWORD!!!"
    fi
done

# Check if folder homerminer exist in the local
if [ -d "./homerminer" ]
then
    rm -rf ./homerminer/
fi

# Get source code
git clone --depth 1 git@git.cloudho.me:taiyangc/homerminer.git
rm -rf ./homerminer/.git*

CURDIR=$(echo ${install_dir}homerminer | sed -e 's/[\/&]/\\&/g')
sed -i "s/FullDir/${CURDIR}/g" ./homerminer/setup/miner
sed -i "s/FullDir/${CURDIR}/g" ./homerminer/setup/minerDaemon

ssh_cmd ${host} ${ip} "mkdir ${install_dir}" ${password}

# Send files to remote server
expect -c "
set timeout -1
spawn scp -r ./homerminer ${host}@${ip}:${install_dir}
expect {
        \"*assword\" {send \"${password}\r\";}
        \"yes/no\" {send \"yes\r\"; exp_continue;}
        eof {exit 0}
       }
expect eof"

rm -rf ./homerminer/

install_cmds=("sudo /etc/init.d/miner stop"
              "\"cd ${install_dir}homerminer/setup/; sudo ./gen_daemon.sh\""
              "sudo /etc/init.d/miner start"
             )

for((i=0;i<${#install_cmds[*]};i++))
do
    ssh_cmd ${host} ${ip} "${install_cmds[i]}"  ${password}
done
