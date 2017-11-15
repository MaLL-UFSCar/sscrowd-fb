#!/bin/bash

#Author: Saulo Domingos de Souza Pedro

#A run interface for the SS-Crowd algorithm with Facebook Messenger

option=$1               #option for this runner
exp_name=$2             #name of the experiment
disclaimer=$3           #name of the file with the disclaimer for users
question_list=$4        #name of the file with the questions

exp_dir=$(cat conf/global-parameters.conf | grep EXPERIMENTS_DIR | tr -d "'" |cut -f2 -d'=') #path to all experiment's directory
root_dir=$(echo $exp_dir/$exp_name)     #path to the experiment directory
logs_dir=$(echo $root_dir/logs)         #path to logs directory
data_dir=$(echo $root_dir/data)         #path to data directory
answer_dir=$(echo $data_dir/answers)    #path to answers directory

#builds a ss-crowd environment
function build(){

        mkdir -p $root_dir
        mkdir -p $logs_dir
        mkdir -p $data_dir
        mkdir -p $answer_dir

        cp $disclaimer $data_dir/disclaimer.raw        #rename dislaimer message file
        cp $question_list $data_dir/questionlist.raw   #rename questionlist message file
         
        #configure webserver settings with sscrowd configuration file

        touch $logs_dir/script.log
        touch $logs_dir/error.log

        sh scripts/log_sender -m $root_dir "created the experiment $exp_name"

        rm -f $disclaimer
        rm -f $question_list
}

function set_global_parameters(){

    settings_file='webserver/webserver/settings.py' 
    cat conf/global-parameters.conf >> $settings_file
}

function unset_global_parameters(){
    settings_file='webserver/webserver/settings.py' 

    sed -i '/ACCESS_TOKEN/d' $settings_file
    sed -i '/EXPERIMENTS_DIR/d' $settings_file
    sed -i '/ALLOWED_HOSTS/d' $settings_file
    sed -i '/SECRET_KEY/d' $settings_file
}

function reset_global_parameters(){
    unset_global_parameters
    set_global_parameters
}

function run(){
    reset_global_parameters
    
    python webserver/manage.py runserver
}

#prints the usage of the options
function helpp(){
        echo "SS-Crowd FB Help"
        echo "Usage:"
        echo "-b: build a new SS-Crowd task"
}

case $option in
        -b)build;;
        -h)helpp;;
        -r)run;;
esac

