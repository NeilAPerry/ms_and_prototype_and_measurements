#!/bin/bash

spaces=(5)
devices=(900 1000)
bitlistIntervals=(2000 4000 6000 8000 10000 12000 14000 16000 18000 20000)
rates=(30000)
broadcastTypes=(smart)


for rate in ${rates[*]}
do
	for broadcastType in ${broadcastTypes[*]}
	do
		for uniform in True
		do
			for move in False
			do
				for bitlist in ${bitlistIntervals[*]}
				do
					for space in ${spaces[*]}
					do
						for device in ${devices[*]}
						do
							python3 main.py -s $space -d $device -m 5 -b $bitlist -v $move -u $uniform -r $rate -c $broadcastType -l True
							cd processing
							python3 process_logs.py -t -s $space -d $device -m 5 -b $bitlist -v $move -u $uniform -r $rate -c $broadcastType
							cd ..
							rm ./processing/logs/minutes_5_numDevices_${device}_bitListInterval_${bitlist}_move_${move}_uniform_${uniform}_broadcastType_${broadcastType}_uniformSpacing_${space}_sendRate_${rate}.csv
						done
					done
				done
			done
		done
	done
done

exit 0
