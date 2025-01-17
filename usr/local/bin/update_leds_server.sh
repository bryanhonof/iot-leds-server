#! /usr/bin/env bash

set -exuo pipefail

function main() {
    local -r repo='bryanhonof/iot-leds-server'
    local -r latest_release_version="$(curl -s https://api.github.com/repos/$repo/releases/latest | jq -r '.tag_name')"
    local -r currently_installed_version="$(dpkg-query --showformat='${Version}' --show leds-server)"
    local -r should_update="$(python -c "from packaging.version import Version; print(Version('$currently_installed_version') < Version('$latest_release_version'))")"

    [[ 'True' != "$should_update" ]] && exit 0

    systemctl kill leds-server.service
    systemctl stop leds-server.service

    pushd "$(mktemp -d)"
    curl -L -o ./leds-server.deb "https://github.com/$repo/releases/download/$latest_release_version/leds-server.deb"
    dpkg -i ./leds-server.deb
    apt-get --yes --fix-broken install ./leds-server.deb
    popd

    systemctl daemon-reload
    systemctl restart leds-server.service

   exit 0
}

main "$@"
