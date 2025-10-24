#!/bin/sh

update_haproxy_extensions() {
    proxy_host="${1:-proxy}"
    proxy_port="${2:-9999}"
    shift 2

    if [ $# -eq 0 ]
    then
        echo "Error: You must provide at least one extension" >&2
        return 1
    fi

    acl_info=$(echo "show acl" | socat stdio tcp-connect:${proxy_host}:${proxy_port} | grep "virt@extensions.txt")
    acl_id=$(echo "$acl_info" | head -n1 | grep -o '^[^ ]*' | grep -o '[0-9]*')

    if [ -z "$acl_id" ]
    then
        echo "Error: Could not get ACL ID for virt@extensions.txt" >&2
        return 1
    fi

    result=$(echo "prepare acl #${acl_id}" | socat stdio tcp-connect:${proxy_host}:${proxy_port})

    new_version=$(echo "$result" | grep -o 'New version created: [0-9]*' | grep -o '[0-9]*$')

    if [ -z "$new_version" ]
    then
        echo "Error: Could not create a new ACL version" >&2
        return 1
    fi

    echo "clear acl @${new_version} #${acl_id}" | socat stdio tcp-connect:${proxy_host}:${proxy_port}

    for ext in "$@"
    do
        clean_ext="${ext##*/}"

        case "$clean_ext" in
            .*) ;;
            *) clean_ext=".$clean_ext" ;;
        esac

        echo "add acl @${new_version} #${acl_id} $clean_ext" | socat stdio tcp-connect:${proxy_host}:${proxy_port}
    done

    echo "commit acl @${new_version} #${acl_id}" | socat stdio tcp-connect:${proxy_host}:${proxy_port}

    echo ""
    echo "Final virt@extensions.txt content:"
    echo "show acl #${acl_id}" | socat stdio tcp-connect:${proxy_host}:${proxy_port}

    return 0
}


EXTENSIONS="$(curl -X GET proxy:8001/services/extensions)"

for ip in $(getent hosts tasks.proxy | awk '{print $1}')
do
    update_haproxy_extensions "$ip" "9999" $EXTENSIONS
done
