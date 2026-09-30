#!/usr/bin/env bash
# Run an OpenFOAM command in a writable reproduction case, preserving host ownership.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "$#" -lt 2 ]; then
    echo 'Usage: bash simulation/foam.sh simulation-runs/four/mesh blockMesh' >&2
    exit 2
fi
case_path="$(realpath -- "$1")"
shift
case_relative="${case_path#"$repo_root"/}"
case "$case_relative" in
    simulation-runs/*) ;;
    *) echo 'Choose a fresh case inside this repository’s simulation-runs directory.' >&2; exit 2 ;;
esac
test -d "$case_path/system"
image='opencfd/openfoam-default@sha256:33fb575aa9980d2bc42fd58c75ae698c489293ba30c991380fe3f899c622f319'
exec docker run --rm --user "$(id -u):$(id -g)" \
    --cpus 8 --memory 12g \
    --mount "type=bind,src=$repo_root,dst=/workspace" \
    "$image" -c 'cd "$1" || exit 1; shift; exec "$@"' bash "/workspace/$case_relative" "$@"
