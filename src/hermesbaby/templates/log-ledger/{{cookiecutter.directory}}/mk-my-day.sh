#!/usr/bin/env bash

################################################################
#                                                              #
#  This file is part of HermesBaby                             #
#                       the software engineer's typewriter     #
#                                                              #
#      https://github.com/hermesbaby                           #
#                                                              #
#  Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)    #
#                                                              #
#  License(s)                                                  #
#                                                              #
#  - MIT for contents used as software                         #
#  - CC BY-SA-4.0 for contents used as method or otherwise     #
#                                                              #
################################################################

# Usage: ./mk_my_day

### Set up the environment of this very script ################################

# Exit on error
set -e

# Exit on unset variable
set -u


### Setting feature toggles based on the environemnt


# Identifying the environment
environment=""
if   [ "${USER:-}" = "codespace" ]; then
    environment="codespace"
elif [ "${USER:-}" = "mobile" ]; then
    environment="ipad"
else
    environment="local_pc"
fi


# Setting feature toggles

# Set or unset, that's the question here (not true or false)

feature_scm_pull_upstream_changes=true  # default
if [ "${environment:-}" = "local_pc" ]; then
     unset feature_scm_pull_upstream_changes
fi

### Date utility functions ####################################################

# @see https://chatgpt.com/share/2737383e-32da-4580-b964-124a63d26aa0
get_monday_date() {
    # Get the current date
    current_date=$(date +%Y-%m-%d)

    # Get the current day of the week (1=Monday, 7=Sunday)
    current_day_of_week=$(date +%u)

    # Calculate the date of the Monday of the current ISO calendar week
    if [ $current_day_of_week -eq 1 ]; then
        # If today is Monday, use today's date
        echo $current_date
    else
        # Otherwise, calculate the date of the previous Monday
        echo $(date -d "$current_date - $((current_day_of_week - 1)) days" +%Y-%m-%d)
    fi
}


### Date and it's parts and different ways to express it ######################

year=$(date +"%G")
month=$(date +"%m-%b")
week=$(date +"CW%V")
day=$(date +"%u-%a" | tr 'a-z' 'A-Z')

cal_year=$year
cal_month=$year-$month
cal_week=$year$week
day_with_cal_week=$cal_week"."$day
day_with_month=$(date +"%G-%b-%d")
weekday_name_full=$(date +"%A")

# Avoid splitting weeks across month breaks
month_monday=$(date -d "$(get_monday_date)" +"%m-%b")

### Paths ######################################################################

file_basename='index'
file_extension='md'
filename=$file_basename.$file_extension

dir_root="docs/"
file_root_relpath_wo_extension=$dir_root/$file_basename
file_root_relpath=${file_root_relpath_wo_extension}.$file_extension

dir_year_relpath=$dir_root$year
file_year_relpath_wo_extension=$dir_year_relpath/$file_basename
file_year_relpath=${file_year_relpath_wo_extension}.$file_extension

dir_month_relpath=$dir_year_relpath/$month_monday
file_month_relpath_wo_extension=$dir_month_relpath/$file_basename
file_month_relpath=${file_month_relpath_wo_extension}.$file_extension

dir_week_relpath="$dir_month_relpath/$week"
file_week_relpath_wo_extension=$dir_week_relpath/$file_basename
file_week_relpath=${file_week_relpath_wo_extension}.$file_extension

dir_day_relpath="$dir_week_relpath/$day"
file_day_relpath_wo_extension=$dir_day_relpath/$file_basename
file_day_relpath=${file_day_relpath_wo_extension}.$file_extension


### Expose path of today's directory for usage of other scripts ###############

today_path_file=today-path

cwd=$(pwd)
dayfile="$cwd/$today_path_file"
echo $dir_day_relpath > $today_path_file

echo "info: Updating file ./$today_path_file with path to today's directory."


### Updating VERSION with today's date ########################################

echo "info: Updating file ./VERSION with today's date"

echo $day_with_month > VERSION


### Get upstream changes ######################################################

scm_pull_upstream_changes() {
    printf "info: Pulling upstream changes ... "

    git pull
}

if [ "${feature_scm_pull_upstream_changes:-}" ]; then
scm_pull_upstream_changes
fi

### Add new day to documentation ##############################################

underline() {
    heading="$@"

    underline=""
    i=0
    while [ $i -lt ${#heading} ]; do
        underline="$underline#"
        i=$((i+1))
    done
    echo $underline
}


create_day () {
    printf "info: Creating $filename of today ... "

    if [ ! -f $file_day_relpath ]; then

        heading="$day_with_cal_week : $weekday_name_full, $day_with_month"

        mkdir -p $dir_day_relpath
        echo "# $heading" >> $file_day_relpath

        cat << 'EOF' >> $file_day_relpath

## Table of Contents

```{contents}
:local:
:depth: 2
```

## AGENDA

- [ ] TODO_1
- [ ] TODO_i
- [ ] TODO_n

## TOP-1

EOF

        echo "    $day/$file_basename" >> $file_week_relpath

        echo "done."
    else
        echo "existed already."
    fi

    mkdir -p $dir_day_relpath/_figures
    mkdir -p $dir_day_relpath/_attachments
}
create_day

update_week () {
    echo "info: Rewriting week's $filename to make sure that \
toctree covers all days' $filename of this week."

    heading="$cal_week"

    mkdir -p $dir_week_relpath
    echo "# $heading" > $file_week_relpath
    (echo) >> $file_week_relpath
    echo '```{toctree}' >> $file_week_relpath
    echo ":maxdepth: 1" >> $file_week_relpath
    (echo) >> $file_week_relpath

    day_entries=$( cd $dir_week_relpath ; ls -w1 -d */ | sed 's/\/\//\//')
    for day_entry in $day_entries ; do
        echo "${day_entry}index" >> $file_week_relpath
    done
    echo '```' >> $file_week_relpath
}
update_week


update_month () {
    echo "info: Rewriting months's $filename to make sure that \
toctree covers all weeks' $filename of this month."

    heading="$cal_month"

    mkdir -p $dir_month_relpath
    echo "# $heading" > $file_month_relpath
    (echo) >> $file_month_relpath
    echo '```{toctree}' >> $file_month_relpath
    echo ":maxdepth: 1" >> $file_month_relpath
    (echo) >> $file_month_relpath

    week_entries=$( cd $dir_month_relpath ; ls -w1 -d */ | sed 's/\/\//\//')
    for week_entry in $week_entries ; do
        echo "${week_entry}index" >> $file_month_relpath
    done
    echo '```' >> $file_month_relpath
}
update_month


update_year () {
    echo "info: Rewriting year's $filename to make sure that \
toctree covers all months' $filename of this year."

    heading="$cal_year"

    mkdir -p $dir_year_relpath
    echo "# $heading" > $file_year_relpath
    (echo) >> $file_year_relpath
    echo '```{toctree}' >> $file_year_relpath
    echo ":maxdepth: 1" >> $file_year_relpath
    (echo) >> $file_year_relpath

    month_entries=$( cd $dir_year_relpath ; ls -w1 -d */ | sed 's/\/\//\//')
    for month_entry in $month_entries ; do
        echo "${month_entry}index" >> $file_year_relpath
    done
    echo '```' >> $file_year_relpath
}
update_year


update_root () {
    echo "info: Rewriting docs's $filename to make sure that \
toctree covers all years' $filename of this document."

    heading="Log Ledger"

    mkdir -p $dir_root
    echo "# $heading" > $file_root_relpath
    (echo) >> $file_root_relpath
    echo '```{toctree}' >> $file_root_relpath
    echo ":maxdepth: 1" >> $file_root_relpath
    (echo) >> $file_root_relpath

    year_entries=$( cd $dir_root ; ls -w1 -d */ | sed 's/\/\//\//')
    for year_entry in $year_entries ; do
        echo "${year_entry}index" >> $file_root_relpath
    done
    echo '```' >> $file_root_relpath
}
update_root


### Clean up possible remainings of obsolete things ###########################

# Nothing to do here yet


###############################################################################
### Environment specific actions ##############################################
###############################################################################

# Skip subsequent actions if not on local_pc

if [ "${environment:-}" != "local_pc" ]; then
    echo "info: Skipping subsequent actions because USER=${USER:-} ."
    exit 0
fi


### Hermesbaby/Sphinx #########################################################

echo "info: Customizing hermesbaby environment for usage in diary."

# Set to today's day
export CFG_DIR_SOURCE=$(cat $dayfile)


### Redirect "symlink" today pointing today's folder ##########################

symlink_today_dir=today

symlink_cwd=$(pwd)
symlink_today_path_rel=$(cat today-path)
symlink_today_path_abs=$(echo $symlink_cwd/$symlink_today_path_rel)

if [ "${OS:-linux}" = "Windows_NT" ]; then # === Windows =============================

rm -rf $symlink_today_dir

symlink_today_path_abs_win=\
$(echo $symlink_today_path_abs | sed 's/^\/c/C:/; s/\//\\/g')
symlink_today_path_abs_win_escaped=\
$(echo $symlink_today_path_abs_win | sed 's/\\/\\\\/g')

printf "info: "

sh -c \
"cmd /c\ mklink\ /J\ $symlink_today_dir\ "$symlink_today_path_abs_win_escaped"\&rem\ "

else # === Linux ===============================================================

ln -sfn "$symlink_today_path_rel" "$symlink_today_dir"

fi


##- Open VS code ##############################################################

vs_code_today_file_path=$file_day_relpath

file_with_cursor_pos=$vs_code_today_file_path:$(echo $(cat $vs_code_today_file_path | wc -l))

# In case option "--skip-open-vscode" is given, skip opening VS code
case " $* " in
    *" --skip-open-vscode "*)
        echo "info: Skipping opening VS code due to --skip-open-vscode option."
        ;;
    *)
        echo "info: Opening vscode and setting cursor to end of file $vs_code_today_file_path"
        code . --goto "$file_with_cursor_pos"
        ;;
esac

### EOF #######################################################################
