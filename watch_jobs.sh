#!/bin/bash
# 1st argument: job to submit, 2nd argument: job name, 3rd argument: directory of error logs (needs tailing /)


while true
do
	echo ''
	date

	# grab list of current jobs
	current_jobs=$(qstat | grep ann | grep '[0-9]\{6\}' -o)

	# give them some time to run
	sleep 10m

	# check whether any of them has been killed
	for job in $current_jobs
	do
		path_to_log="$3""$2"'.e'"$job"
		if $(grep Killed $path_to_log | wc -l)
		then
			echo 'job '"$job"' has been killed, restarting now...'
			parameters=$(head -n 1 $path_to_log)
			echo $parameters
			qsub $1 $parameters
		fi
	done
done



