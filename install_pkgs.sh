#!/bin/bash
check_root() {
    if [[ "$(whoami)" != "root" ]]; then
        echo -e "\nThis script must be ran as root!\nExiting...\n"
        exit 0
    fi
}
create_user() {
    fand_groups="i2c,spi,video"
    mkdir -p /opt/fand/.local/bin
    echo -e "# set PATH so it includes user's private bin if it exists\n \
if [ -d "$HOME/.local/bin" ] ; then\n \
\tPATH=\"\$HOME/.local/bin:\$PATH\"\n \
fi" > /opt/fand/.profile
    sudo useradd -c "fand service account" -r -d /opt/fand fand
    usermod -aG ${fand_groups} fand
    chown -R fand: /opt/fand
}
install_pkgs() {
    debpkgs=('python3-pip' 'i2c-tools' 'libmariadb3' 'libmariadb-dev')
    for pkg in ${debpkgs[@]}; do
        apt install ${pkg} -y
    done

    pypkgs=('gpiozero' 'pyyaml' 'RPi.GPIO' 'smbus' 'mariadb')
    echo "Installing python packages for fand user account only."
    echo -e "If you wish to run this program from another user account you will need to either install packages globally, or for that user."
    for pkg in ${pypkgs[@]}; do
        su fand -c "pip3 install ${pkg}"
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
uninstall() {
    check_root
    unalias rm 2> /dev/null
    systemctl disable --now fand.service
    if [[ -f /usr/lib/systemd/system/fand.service ]]; then
        rm /usr/lib/systemd/system/fand.service
    fi
    userdel -r fand
    if [[ -d /opt/fand ]]; then
        rm -rf /opt/fand
    fi
}
usage() {
    echo -e "Installer script usage:\n   No arguements to run installer\n   --uninstall            Completely remove fand service"
}
main() {
    check_root
    create_user
    install_pkgs
    install_files
}
if [[ ! -z "$1" ]] && [[ "$1" == "--uninstall" ]]; then
    uninstall
elif [[ ! -z "$1" ]]; then
    usage
else
    main
fi
exit 0
