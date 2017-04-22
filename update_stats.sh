#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/home/rey44
array=( "polish" "german" "english" "japanese" "indonesian" "ctb" "taiko" "osumania" "modhelp" "hungarian" "chinese" "korean" "french" "russian" "spanish" "dutch" "videogames" "modreqs" "help" "finnish" "skandinavian" "italian" "filipino" "romanian" "czechoslovak" "cantonese" "hebrew" "malaysian" "balkan" "bulgarian" "arabic" "turkish" "portuguese" "greek" "thai" )
for i in "${array[@]}"
do
	python /home/rey44/irciostats/main.py /home/rey44/irciostats/yearly2016.cfg \#$i ;
done
