#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == $0 ]] 
then
    echo "Must run by source'ing the script" 
    echo "\"source $0\""
fi

unique_env_path ()
{
    echo "${2//$1/}"
}

env_prepend()
{
    eval export "$1="\"$2:\"\$\("unique_env_path \"$2:\"" \$$1\)
}

PATHNAME=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))
env_prepend PATH $PATHNAME

