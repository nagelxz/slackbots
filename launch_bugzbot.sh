BUGZBOTDIR=/home/webapps/tenthwavebots/bugzbot

cd $BUGZBOTDIR && \
     . bin/activate && \
     python bugzbot.py &

