const REST_POSITIONS = {
    front_left: [52, 85, 84],
    back_left: [49, 80, 95],
    back_right: [128, 88, 97],
    front_right: [129, 90, 75]
};

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
        const value = this.value;

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

async function resetLeg(legName) {
    const restAngles = REST_POSITIONS[legName];

    // Update UI
    SERVO_ORDER.forEach((servo, index) => {
        const slider = document.querySelector(`[data-leg="${legName}"][data-servo="${servo}"]`);
        slider.value = restAngles[index];
        document.getElementById(`${legName}_${servo}_val`).textContent = restAngles[index] + '°';
    });

    // Update stored angles
    legAngles[legName] = [...restAngles];

    // Send to API
    await sendLegCommand(legName, restAngles);
}

// Battery status update
async function updateBatteryStatus() {
    try {
        const response = await fetch('/api/battery');
        const data = await response.json();

        if (data.available) {
            const percentage = data.percentage || 0;
            document.getElementById('battery-percentage').textContent = percentage.toFixed(0) + '%';
            document.getElementById('battery-bar').style.width = percentage + '%';
        } else {
            document.getElementById('battery-percentage').textContent = '--%';
            document.getElementById('battery-bar').style.width = '0%';
        }
    } catch (error) {
        console.error('Error fetching battery status:', error);
    }
}

// Update battery status on load and every 2 seconds
updateBatteryStatus();
setInterval(updateBatteryStatus, 2000);
