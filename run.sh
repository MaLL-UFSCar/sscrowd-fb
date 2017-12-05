#!/bin/bash

#Author: Saulo Domingos de Souza Pedro

#A run interface for the SS-Crowd algorithm with Facebook Messenger

option=$1               #option for this runner
exp_name=$2             #name of the experiment
question_list_file=$3        #name of the file with the questions

exp_dir=$(cat conf/global-parameters.conf | grep EXPERIMENTS_DIR | tr -d "'" |cut -f2 -d'=') #path to all experiment's directory

#builds a ss-crowd environment
function build(){
        python webserver/sscrowd_bot/tools.py -b -e $exp_name -q $question_list_file
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

function receive_answers(){
    reset_global_parameters
    python webserver/manage.py runserver
}

function ask_questions(){
    reset_global_parameters
    python webserver/sscrowd_bot/tools.py -e $exp_name -a 
}

#prints the usage of the options
function helpp(){
        echo "SS-Crowd FB Help"
        echo "Usage:"
        echo "-b: build a new SS-Crowd task"
        echo "-a: start asking questions"
}

case $option in
        -b)build;;
        -a)ask_questions;;
        -h)helpp;;
        -r)receive_answers;;
esac

