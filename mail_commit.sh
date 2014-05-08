#!/bin/bash
#
# primary: bkennedy
# secondary:
#

if ! which post-review > /dev/null; then
  echo "rbtools not installed, run:"
  echo "sudo apt-get install --yes python-setuptools"
  echo "sudo easy_install -U RBTools"
  exit
fi

function usage() {
  echo "Mails or updates a commit and fills in required fields"
  echo "flags:"
  echo " -h help"
  echo " -u update review   (will create if omitted)"
  echo " -j [ jira ticket ] (required for post)"
  echo " -t [ testing ]     (required for post)"
  echo " -r [ reviewers ]   (required for post)"
  echo " -b [ backport ] "
  cat <<< "
Example Usage:

create a review
  mail_commit.sh -j PBL-1000 -t unit -r reviewer1,reviewer2,reviewer3

update a review (on reviewboard)
  mail_commit.sh -u

update a review and change the testing field
  mail_commit.sh -u -t unit,component

udpate a review and change the jira ticket
  mail_commmit.sh -u -j PBL-1005
"
  exit $1
}

function update() {
  echo "TODO"
  exit 0
}

function update() {
  local msg="$1"
  local field="$2"
  local value="$3"
  if [[ -z "$value" ]]; then
    echo -n "$msg"
    return
  fi

  echo "$msg" | sed -e "/^$field:/d"
  if ! echo "$msg" | tail -n 1 | grep "^[A-Za-z]*:" > /dev/null; then
    echo ""
  fi
  echo "$field: $value"
}

while getopts "ht:j:b:r:u" OPTION; do
  case $OPTION in
    "h")
    usage 0
    ;;

    "u")
    update=1
    ;;

    "t")
    testing=$OPTARG
    ;;

    "j")
    jira=$OPTARG
    ;;

    "b")
    backport=$OPTARG
    ;;

    "r")
    reviewers=$OPTARG
    ;;

    ?)
    usage 1
    ;;
  esac
done

# if update, get review num
# else open review, get num
if [[ -z "$update" ]]; then
  echo "Opening new review..."
  txt=$(post-review)
  num=$(echo "$txt" | grep "Review" | sed -e 's/.*#//' -e 's/ .*//')
  url="https://reviewboard.insnw.net/r/$num/"
  echo "Opened review $num"

  commit_txt="$(git log -n 1 --pretty=format:%B)"
  commit_txt="$(update "$commit_txt" "Review" "$url")"
  commit_txt="$(update "$commit_txt" "Testing" "$testing")"
  commit_txt="$(update "$commit_txt" "Tickets" "$jira")"
  commit_txt="$(update "$commit_txt" "Backport" "$backport")"
  echo -e "Updated commit message to:\n$commit_txt"
  git commit --amend --message "$commit_txt"
else
  orig_commit_txt="$(git log -n 1 --pretty=format:%B)"
  commit_txt="$orig_commit_txt"
  num=$( \
    echo -n "$commit_txt" | grep Review | sed -e 's/[^0-9]*\([0-9]*\).*/\1/')
  echo "Using review num: $num"

  commit_txt="$(update "$commit_txt" "Testing" "$testing")"
  commit_txt="$(update "$commit_txt" "Tickets" "$jira")"
  commit_txt="$(update "$commit_txt" "Backport" "$backport")"
  if [[ "$orig_commit_txt" != "$commit_txt" ]]; then
    echo -e "Updated commit message to:\n$commit_txt"
    git commit --amend --message "$commit_txt"
  fi
fi

# push diff
echo ""
echo "Updating review: $num"
post-review \
  --parent=HEAD^               \
  --guess-description          \
  --guess-summary              \
  --target-groups=dev          \
  --target-people=$reviewers   \
  -r $num \
  -p
