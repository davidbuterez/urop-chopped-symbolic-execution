#!/usr/bin/env bash

repo=$1
patch_hash=$2

if [[ ! -d temp ]] ; then
  git clone "$repo" temp > /dev/null 2>&1
  echo "Cloned repository."
else
  need_update=false

  cd temp

  urls=( $(git remote -v) )
  cloned_url="${urls[1]}"

  if [[ "$repo" != "$cloned_url" ]] ; then
    echo "Existing temp directory does not match provided repo."
    cd ..
    rm -r temp
    git clone "$repo" temp > /dev/null 2>&1
    need_update=true
  fi

  current_commit="$(git show -s --format=%H)"
  last_commit_info=( $(git log HEAD^..HEAD) )

  last_commit="${last_commit_info[1]}"

  if [[ "$current_commit" != "$last_commit" ]] ; then
    echo "Repository out of date. Pulling..."
    git pull
    need_update=true
  fi

  if [[ "$need_update" == false ]] ; then
    echo "Everything up-to-date."
  fi

  cd ..
fi

cd temp

git diff "$patch_hash~1" "$patch_hash" -U0 >../diffs
echo "Wrote diff file."
echo

cd ..

#Analyze diff
declare -r new_file_regex="\+\+\+ b/(.*)"
declare -r hunk_regex="@@.*\+([0-9]+),([0-9]+) @@"
declare -r hunk_def_regex="@@.*\+([0-9]+) @@"
declare -r target_file_type=".*\.c$|.*\.h$"

diff_array=( )
readarray diff_array < diffs

first_file=1

for line in "${diff_array[@]}"; do
  sline=0
  if [[ $line =~ $new_file_regex ]]; then
    F=${BASH_REMATCH[1]}
    F=`echo -e $F`
    if [[ $F =~ $target_file_type ]]; then
      if [ $first_file -eq 0 ]; then
        echo
      else first_file=0
      fi
      echo "Filename: $F"
      echo "New code at lines: "
    fi

  elif [[ $line =~ $hunk_regex ]]; then
    sline=${BASH_REMATCH[1]}
    cline=${BASH_REMATCH[2]}
    # echo "found new hunk $sline $cline"

  elif [[ $line =~ $hunk_def_regex ]]; then
    sline=${BASH_REMATCH[1]}
    cline=1
    # echo "found new dhunk $sline $cline"

  fi

  if [[ $sline -ne 0 ]]; then
    if [[ $F =~ $target_file_type ]]; then
      i=$sline
      let "LLINE = sline + cline"
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


