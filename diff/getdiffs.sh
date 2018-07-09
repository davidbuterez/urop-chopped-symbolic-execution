#!/usr/bin/env bash

REPO=$1
PATCH_HASH=$2

git clone "$REPO" temp > /dev/null 2>&1
echo "Cloned repository."

cd temp

git diff "$PATCH_HASH~1" "$PATCH_HASH" -U0 >../diffs
echo "Wrote diff file."
echo

cd ..
rm -rf temp

#Analyze diff
declare -r new_file_regex="\+\+\+ b/(.*)"
declare -r hunk_regex="@@.*\+([0-9]+),([0-9]+) @@"
declare -r hunk_def_regex="@@.*\+([0-9]+) @@"
declare -r target_file_type=".*\.c$|.*\.h$"

DIFF=( )
readarray DIFF < diffs

FIRST_FILE=1

for line in "${DIFF[@]}"; do
  SLINE=0
  if [[ $line =~ $new_file_regex ]]; then
    F=${BASH_REMATCH[1]}
    F=`echo -e $F`
    if [[ $F =~ $target_file_type ]]; then
      if [ $FIRST_FILE -eq 0 ]; then
        echo
      else FIRST_FILE=0
      fi
      echo "Filename: $F"
      echo "New code at lines: "
    fi

  elif [[ $line =~ $hunk_regex ]]; then
    SLINE=${BASH_REMATCH[1]}
    CLINE=${BASH_REMATCH[2]}
    # echo "found new hunk $SLINE $CLINE"

  elif [[ $line =~ $hunk_def_regex ]]; then
    SLINE=${BASH_REMATCH[1]}
    CLINE=1
    # echo "found new dhunk $SLINE $CLINE"

  fi

  if [[ $SLINE -ne 0 ]]; then
    if [[ $F =~ $target_file_type ]]; then
      i=$SLINE
      let "LLINE = SLINE + CLINE"
      while [[ $i -lt $LLINE ]]; do
        echo -n "$i "
        let i++
      done
    fi
  fi
done

echo
echo
echo "Analyzed diff"


