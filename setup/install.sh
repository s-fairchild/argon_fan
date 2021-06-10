#!/bin/bash
check_root() {
    if [[ "$(whoami)" != "root" ]]; then
        echo -e "\nThis script must be ran as root!\nExiting...\n"
        exit 0
    fi
}
create_user() {
    mkdir -p ${service_dir}/.local/bin
    echo -e "# set PATH so it includes user's private bin if it exists\n \
    if [ -d "${service_dir}/.local/bin" ] ; then\n \
    \tPATH=\"\$HOME/.local/bin:\$PATH\"\n \
    fi" > ${service_dir}.profile
    sudo useradd -c "${service_account} service account" -r -d /opt/fand fand
    usermod -aG ${fand_groups} fand
    chown -R fand: ${service_dir}
}
install_pkgs() {
    apt install ${debpkgs} -y
    echo "Installing python packages for fand user account only."
    echo -e "If you wish to run this program from another user account you will need to either install packages globally, or for that user."
    pip3 install ${pypkgs}
}
install_files() {
    systemd_setup
    if [[ ! -f ${service_dir}/main.py ]]; then
        cp ../main.py ${service_dir}/
    else
        echo "/opt/fand/main.py already installed. Skipping"
    fi
    if [[ ! -f ${service_dir}/fan_monitor.py ]]; then
        cp ../fan_monitor.py ${service_dir}/
    else
        echo "/opt/fand/fan_monitor.py already installed. Skipping"
    fi
    if [[ ! -f ${service_dir}/powerbutton.py ]]; then
        cp ../powerbutton.py ${service_dir}/
    else
        echo "/opt/fand/fan_monitor.py already installed. Skipping"
    fi
    if [[ ! -f ${service_dir}/fand.yaml ]]; then
        cp ../fand.yaml ${service_dir}/
    else
        echo "/opt/fand/fand.yaml already installed. Skipping."
    fi
}
systemd_setup() {
    if [[ -d /usr/lib/systemd/system/ ]]; then
    echo -e "[Unit]\n\
Description=PWM Fan Controller Daemon\n\
After=multi-user.target\n\

[Service]\n\
Type=simple\n\
User=fand\n\
WorkingDirectory=/opt/fand\n\
Environment=PYTHONPATH=/opt/fand/\n\
ExecStart=/usr/bin/python3 -u /opt/fand/main.py\n\
Restart=on-failure\n\

[Install]\n\
WantedBy=multi-user.target" > /usr/lib/systemd/system/fand.service
    systemctl daemon-reload
    systemctl enable fand.service
    echo "Installed fand.service systemd-unit"
    else
        echo "Unable to install fand.service, directory /usr/lib/systemd/system does not exist"
    fi
}
uninstall() {
    check_root
    echo "Databases will not be modified during uninstall"
    unalias rm 2> /dev/null
    systemctl disable --now fand.service
    if [[ -f /usr/lib/systemd/system/fand.service ]]; then
        rm /usr/lib/systemd/system/fand.service
    fi
    userdel -r fand
    if [[ -d ${service_dir}/ ]]; then
        rm -rf ${service_dir}/
    fi
}
usage() {
    echo -e "\nInstaller script usage:\n\n\
          "sudo ./install.sh"          To install run from the setup directory\n\
          --uninstall\
                      Completely remove fand service\n"
}
main() {
    check_root
    if [[ -f setup_settings.env ]]; then
        source setup_settings.env
    else
        echo "setting_settings.env not found, exiting."; exit 0
    fi
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
