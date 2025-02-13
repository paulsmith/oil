#!/usr/bin/env bash
#
# Usage:
#   services/github-actions.sh <function name>

set -o nounset
set -o pipefail
set -o errexit

# Reuse some stuff
source services/travis.sh

# Relevant docs:
#
# https://man.sr.ht/tutorials/getting-started-with-builds.md
# https://man.sr.ht/builds.sr.ht/#secrets
# https://man.sr.ht/builds.sr.ht/compatibility.md
#
# Basically, it supports up to 4 files called .builds/*.yml.
# And we need to upload an SSH key as secret via the web UI.

keygen() {
  ssh-keygen -t rsa -b 4096 -C "oilshell github-actions" -f rsa_github_actions
}

#
# Run remotely
#

publish-html-assuming-ssh-key() {
  if true; then
    # https://docs.github.com/en/actions/reference/environment-variables

    # Recommended by the docs
    export JOB_URL="$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID"

    deploy-job-results 'github-' \
      JOB_URL \
      GITHUB_WORKFLOW	\
      GITHUB_RUN_ID \
      GITHUB_RUN_NUMBER \
      GITHUB_JOB \
      GITHUB_ACTION \
      GITHUB_REF
  else
    deploy-test-wwz  # dummy data that doesn't depend on the build
  fi

  write-jobs-raw 'github-'

  remote-rewrite-jobs-index 'github-'

  # note: we could speed jobs up by doing this separately?
  remote-cleanup-jobs-index 'github-'

  # toil-worker.sh recorded this for us
  local status
  status=$(cat _tmp/toil/exit-status.txt)

  log "Exiting with saved status $status"

  return $status
}

# Notes on Github secrets:

# - "Secrets are environment variables that are encrypted. Anyone with
#    collaborator access to this repository can use these secrets for Actions."
#
# - "Secrets are not passed to workflows that are triggered by a pull request from a fork"
#
# TODO: We're not following the principle of least privilege!  Really we should
# have an "append-only" capability?  So then pull requests from untrusted forks
# can trigger builds?
#
# Instead of SSH, we should use curl to POST a .zip file to PHP script on
# travis-ci.oilshell.org?

# Overwrites the function in services/travis.sh
publish-html() {
  local privkey=/tmp/rsa_github_actions

  if test -n "${TOIL_KEY:-}"; then
    echo "$TOIL_KEY" > $privkey
  else
    echo '$TOIL_KEY not set'
    exit 1
  fi

  chmod 600 $privkey
  eval "$(ssh-agent -s)"
  ssh-add $privkey

  publish-html-assuming-ssh-key
}

"$@"
