#!/usr/bin/env bash

PERMITTED_HOOKS="pre-commit;commit-msg"
PATH_HOOKS="$(
  cd "$(dirname "$0")" >/dev/null 2>&1 || exit
  pwd -P
)"
PATH_ROOT="${PATH_HOOKS%/*}"
PRE_COMMIT_BIN="${PATH_ROOT}/venv/bin/pre-commit"

installFunction() {
  for CONFIGFILE in $(ls -a "${PATH_HOOKS}"); do
    if [[ "${CONFIGFILE}" =~ ^[\.].*-config.yaml$ ]]; then
      echo "Configuration file ${CONFIGFILE} found."
      HOOK_TYPE=$(echo "${CONFIGFILE}" | cut -d"." -f2 | sed 's/-config//')
      if [[ "$PERMITTED_HOOKS" =~ .*$HOOK_TYPE.* ]]; then
        printf 'HOOK_TYPE %s is valid.\nInstalling:\n' "${HOOK_TYPE}"
        "${PRE_COMMIT_BIN}" install -t "$HOOK_TYPE" --config "${PATH_HOOKS}/${CONFIGFILE}"
        printf '\n\n'
      else
        printf 'HOOK_TYPE %s is invalid.\nAborting.\n\n' "${HOOK_TYPE}"
      fi
    else
      printf 'Filename %s not matching the regex.\nSkipping.\n\n' "${CONFIGFILE}"
    fi
  done
  exit 0
}

showInstalledFunction() {
  INSTALLED_HOOKS=""
  for HOOK in $(ls -a "${PATH_HOOKS}/../.git/hooks/"); do
    if ! [[ "${HOOK}" =~ (.*sample$|^[\.]*$) ]]; then
      INSTALLED_HOOKS="${INSTALLED_HOOKS}${HOOK};"
    fi
  done
  printf 'Currently installed hooks are: %s\n\n' "$(echo "${INSTALLED_HOOKS}" | tr ";" " ")"
}

uninstallFunction() {
  showInstalledFunction
  for HOOK in $(echo "${INSTALLED_HOOKS}" | tr ";" "\n"); do
    "${PRE_COMMIT_BIN}" uninstall -t "${HOOK}"
  done
}

helpFunction() {
  echo ""
  echo "Usage: [-i|u] [ARGS]"
  echo -e "\tARGS Names of hooks to uninstall separated by a ,"
  echo -e "\t-i Installs hooks based on the config files found in ${PATH_HOOKS}"
  echo -e "\t-u Uninstalls hooks"
  exit 1
}

while getopts "uih" opt; do
  case $opt in
  i) installFunction ;;
  u) uninstallFunction ;;
  h) helpFunction ;;
  \?) helpFunction ;;
  esac
done
