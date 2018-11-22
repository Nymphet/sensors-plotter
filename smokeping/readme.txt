So... to monitor if the networks are working on a computer, the best way i can think of is to use smokeping.

these are just some example config files to make it working with nginx.

first install smokeping and a dependency, fcgiwrap, if you have not already installed it before.

    sudo apt-get install smokeping fcgiwrap

after editing or creating the config files listed in this directory, do a

    systemctl restart smokeping.service
    sudo nginx -s reload

then visit http://smokeping.example.com/ to see if everything is working.

finally, switch to ssl if you like.

