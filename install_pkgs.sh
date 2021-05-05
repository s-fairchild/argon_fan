#!/bin/bash
check_root() {
    if [[ "$(whoami)" != "root" ]]; then
        echo -e "\nThis script must be ran as root!\nExiting...\n"
        exit 0
    fi
}
create_user() {
    grep fand /etc/passwd > /dev/null
    if [[ ! "$?" -eq 0 ]]; then
        service_account="fand"
        sudo useradd -c "fand service account" -r -b /opt/fand fand
        if [ ! -d /opt/fand ]; then
            mkdir -p /opt/fand
            chown -R fand: /opt/fand
        fi
    else
        echo "fand account already exists. Skipping."
    fi
}
install_pkgs() {
        pkgs=('gpiozero' 'pyyaml')
    for pkg in ${pkgs[@]}; do
        pip3 install ${pkg}
    done
}
install_files() {
    echo "Installing fand.service file now."
    if [[ -f ./fand.service ]] && [[ ! -f /usr/lib/systemd/system/fand.service ]]; then
        cp ./fand.service /usr/lib/systemd/system/
        systemctl daemon-reload
        systemctl enable fand.service
    else
        echo "fand not installed."
    fi
    if [[ ! -f /opt/fand/main.py ]]; then
        cp ./main.py /opt/fand/
    else
        echo "/opt/fand/main.py already installed. Skipping"
    fi
    if [[ ! -f /opt/fand/fan_monitor.py ]]; then
        cp ./fan_monitor.py /opt/fand/
    else
        echo "/opt/fand/fan_monitor.py already installed. Skipping"
    fi
    if [[ ! -f /opt/fand/powerbutton.py ]]; then
        cp ./powerbutton.py /opt/fand/
    else
        echo "/opt/fand/fan_monitor.py already installed. Skipping"
    fi
    if [[ ! -f /opt/fand/fand.yaml ]]; then
        cp ./fand.yaml /opt/fand/
    else
        echo "/opt/fand/fand.yaml already installed. Skipping."
    fi
}

check_root
create_user
install_pkgs
install_files

exit 0