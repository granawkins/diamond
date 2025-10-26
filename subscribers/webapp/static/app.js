const SERVO_ORDER = ['lower_hip', 'upper_hip', 'shoulder'];

// Store current angles for each leg
const legAngles = {
    front_left: [90, 90, 90],
    front_right: [90, 90, 90],
    back_left: [90, 90, 90],
    back_right: [90, 90, 90]
};

// Handle slider input (real-time display update)
document.querySelectorAll('.slider').forEach(slider => {
    slider.addEventListener('input', function() {
        const leg = this.dataset.leg;
        const servo = this.dataset.servo;
        const value = Math.round(this.value);

        document.getElementById(`${leg}_${servo}_val`).textContent = value + '°';
    });

    slider.addEventListener('change', async function() {
        const leg = this.dataset.leg;
        const servo = this.dataset.servo;
        const value = parseInt(this.value);

        // Update stored angle
        const servoIndex = SERVO_ORDER.indexOf(servo);
        legAngles[leg][servoIndex] = value;

        // Send to API
        await sendLegCommand(leg, legAngles[leg]);
    });
});

async function sendLegCommand(legName, angles) {
    try {
        const response = await fetch('/api/leg', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ leg_name: legName, angles: angles })
        });

        if (!response.ok) {
            console.error('Failed to set leg position');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function commandLeg(legName, command) {
    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ leg_name: legName, command: command })
        });

        if (!response.ok) {
            console.error('Failed to execute command');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function resetAll() {
    const legs = ['front_left', 'front_right', 'back_left', 'back_right'];
    for (const leg of legs) {
        await commandLeg(leg, 'reset');
    }
}

async function upAll() {
    const legs = ['front_left', 'front_right', 'back_left', 'back_right'];
    for (const leg of legs) {
        await commandLeg(leg, 'up');
    }
}

// Update status (battery and leg positions)
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // Update battery
        if (data.battery && data.battery.available) {
            const percentage = data.battery.percentage || 0;
            document.getElementById('battery-percentage').textContent = percentage.toFixed(0) + '%';
            document.getElementById('battery-bar').style.width = percentage + '%';
        } else {
            document.getElementById('battery-percentage').textContent = '--%';
            document.getElementById('battery-bar').style.width = '0%';
        }

        // Update leg positions
        if (data.legs) {
            Object.keys(data.legs).forEach(legName => {
                const angles = data.legs[legName];
                legAngles[legName] = angles;

                SERVO_ORDER.forEach((servo, index) => {
                    const slider = document.querySelector(`[data-leg="${legName}"][data-servo="${servo}"]`);
                    if (slider) {
                        slider.value = angles[index];
                        document.getElementById(`${legName}_${servo}_val`).textContent = Math.round(angles[index]) + '°';
                    }
                });
            });
        }
    } catch (error) {
        console.error('Error fetching status:', error);
    }
}

// Update status on load and every 2 seconds
updateStatus();
setInterval(updateStatus, 2000);
