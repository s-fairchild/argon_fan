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
setup_db() {
    echo -e "Creating ${db_name} database\n"
    mysql -e "CREATE DATABASE IF NOT EXISTS ${db_name};"
    echo "creating user ${mariadb_user} in mariadb"
    mysql -e "CREATE USER IF NOT EXISTS '${mariadb_user}'@'localhost' IDENTIFIED BY '${db_userpass}';"
    mysql -e "CREATE TABLE IF NOT EXISTS ${db_name}.${table}( \
    ID BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,\
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
    cpu_tempC DECIMAL(4, 2) NOT NULL,\
    fanspeed INT(100) \
    );"
    mysql -e "GRANT ALL PRIVILEGES ON \`${db_name}\`.* TO '${mariadb_user}'@localhost;"
    mysql -e "FLUSH PRIVILEGES;"
}
install_pkgs() {
    for pkg in ${debpkgs[@]}; do
        apt install ${pkg} -y
    done
    echo "Installing python packages for fand user account only."
    echo -e "If you wish to run this program from another user account you will need to either install packages globally, or for that user."
    for pkg in ${pypkgs[@]}; do
        pip3 install ${pkg}
    done
}
install_files() {
    echo "Installing fand.service file now."
    if [[ -f ./fand.service ]] && [[ -d /usr/lib/systemd/system/ ]]; then
        cp ./fand.service /usr/lib/systemd/system/
        systemctl daemon-reload
        systemctl enable fand.service
    else
        echo "fand not installed."
    fi
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
          "sudo ./start_install.sh"          To install run from the setup directory\n\
          --uninstall\
                      Completely remove fand service\n"
}
main() {
    check_root
    create_user
    install_pkgs
    setup_db
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
