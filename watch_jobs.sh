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
		killed=$(grep Killed $path_to_log | wc -l)
		crashed=$(grep Exception $path_to_log | wc -l)
		if [ $killed -ne 0 ] || [ $crashed -ne 0 ]
		then
			echo 'job '"$job"' has not finished, restarting now...'
			parameters=$(head -n 1 $path_to_log)
			echo $parameters
			qsub $1 $parameters
		fi
	done
done



