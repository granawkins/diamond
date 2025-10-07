# Diamond

Diamond is a quadruped robot, and these are all the files related to its design and software. 

## Electronics
```
 Battery: Lithium Ion 3C 2200 mAh
                |
             UBEC 5V
                |
  |------------------------------|
  |                              |
---PCB 9685---GND     9---Raspberry Pi 5 8gb---|
              SCL     5                        |
              SDA     3                  SD 16gb
              VCC     1------------------------|
                0     SG90 : front left lower hip
                1     SG90 : front left upper hip
                2     SG90 : front left shoulder
                3     empty
              4-7     ...front right
             8-11     ...back left
------------12-15     ...back right
```

## Roadmap
- Better leg design
- Full body design
- Control programming
- VLM integration
- VLA / RLing
