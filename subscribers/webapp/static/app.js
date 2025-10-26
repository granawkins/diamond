const SERVO_ORDER = ['lower_hip', 'upper_hip', 'shoulder'];

// Store current angles for each leg
const legAngles = {
    front_left: [90, 90, 90],
    front_right: [90, 90, 90],
    back_left: [90, 90, 90],
    back_right: [90, 90, 90]
};

async function command(command) {
    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command })
        });
    } catch (error) {
        console.error('Error:', error);
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
