# Diamond

Diamond is a quadruped robot, and these are all the files related to its design and software. 

## Electronics
```
Waveshare UPS HAT (2x 18650 cells, 8.4V charger)
                |
                | (HAT pins stack on RPi GPIO)
                |
  |------------------------------|
  |                              |
---PCA9685----GND     9---Raspberry Pi 5 8gb---|
              SCL     5                        |
              SDA     3                  SD 16gb
              VCC     1------------------------|
              V+      2 (5V from UPS HAT)------|
                0     MG90 : front left lower hip
                1     MG90 : front left upper hip
                2     MG90 : front left shoulder
                3     empty
              4-7     ...back left
             8-11     ...back right
------------12-15     ...front right
```

## Web Interface

Diamond runs a FastAPI web server on boot for remote control and debugging. Access it from any device on the local network at `http://<pi-ip>:8000`.

**Managing the service:**
```bash
sudo systemctl status diamond-webapp   # Check status
sudo systemctl restart diamond-webapp  # Restart after code changes
sudo journalctl -u diamond-webapp -f   # View live logs
```

The service auto-starts on boot and auto-restarts on crashes.

## Roadmap
- Better leg design
- Power switch/button
- Full body design
- Control programming
- VLM integration
- VLA / RLing
