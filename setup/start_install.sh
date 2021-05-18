if [[ "${1}" = "--uninstall" ]]; then
    /bin/bash -c "source setup_settings.env; exec /bin/bash main.sh --uninstall"
elif [[ "${1}" == "" ]]; then
    /bin/bash -c "source setup_settings.env; exec /bin/bash main.sh"
else
    /bin/bash -c "source setup_settings.env; exec /bin/bash main.sh --usage"
fi