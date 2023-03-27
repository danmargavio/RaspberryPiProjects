# REV Color Sensor to NT

## Setup Instructions

* Install Updates 
    
    `sudo apt update && sudo apt upgrade`
* Install Dependencies

    `sudo apt install openbox xinit python3-pip python3-tk lxterminal`
* Update pip

    `sudo python -m pip install --upgrade pip`
* Clone the repository

    `git clone https://github.com/danmargavio/RaspberryPiProjects`
* Install python dependencies

    `cd RaspberryPiProjects && pip install -r requirements.txt`
* Autostart
    
    * `crontab -e`
    * Add the following
        
       `@reboot python /home/pi/RaspberryPiProjects/Color_Sensor.py -ip 10.63.69.2 -ir -p -rw 3.8 -gw 3 -bw 3.4 -iw 5`
* Reboot
    
    `sudo reboot`