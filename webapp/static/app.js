const servoNames = {
    0: "Front Left - Lower Hip",
    1: "Front Left - Upper Hip",
    2: "Front Left - Shoulder",
    3: "Front Left - (empty)",
    4: "Back Left - Lower Hip",
    5: "Back Left - Upper Hip",
    6: "Back Left - Shoulder",
    7: "Back Left - (empty)",
    8: "Back Right - Lower Hip",
    9: "Back Right - Upper Hip",
    10: "Back Right - Shoulder",
    11: "Back Right - (empty)",
    12: "Front Right - Lower Hip",
    13: "Front Right - Upper Hip",
    14: "Front Right - Shoulder",
    15: "Front Right - (empty)"
};

const servosContainer = document.getElementById('servos');

// Create servo controls
for (let i = 0; i < 16; i++) {
    const row = document.createElement('div');
    row.className = 'servo-row' + (servoNames[i].includes('empty') ? ' empty' : '');

    const channel = document.createElement('div');
    channel.className = 'channel';
    channel.textContent = `CH ${i}`;

    const name = document.createElement('div');
    name.className = 'name';
    name.textContent = servoNames[i];

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.min = 0;
    slider.max = 180;
    slider.value = 90;
    slider.className = 'slider';
    slider.id = `servo-${i}`;

    const value = document.createElement('div');
    value.className = 'value';
    value.textContent = '90°';
    value.id = `value-${i}`;

    // Add event listener for real-time updates
    slider.addEventListener('input', function() {
        value.textContent = this.value + '°';
    });

    slider.addEventListener('change', async function() {
        const channel = i;
        const angle = parseInt(this.value);

        try {
            const response = await fetch('/api/servo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ channel, angle })
            });

            if (!response.ok) {
                console.error('Failed to set servo position');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    row.appendChild(channel);
    row.appendChild(name);
    row.appendChild(slider);
    row.appendChild(value);
    servosContainer.appendChild(row);
}

// Battery status update function
async function updateBatteryStatus() {
    try {
        const response = await fetch('/api/battery');
        const data = await response.json();

        if (data.available) {
            document.getElementById('battery-voltage').textContent = data.voltage + 'V';
            document.getElementById('battery-current').textContent = data.current + 'A';
            document.getElementById('battery-power').textContent = data.power + 'W';

            const statusBadge = document.getElementById('battery-status');
            statusBadge.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
            statusBadge.className = 'battery-status-badge status-' + data.status;
        } else {
            document.getElementById('battery-voltage').textContent = '--';
            document.getElementById('battery-current').textContent = '--';
            document.getElementById('battery-power').textContent = '--';
            document.getElementById('battery-status').textContent = 'Unavailable';
            document.getElementById('battery-status').className = 'battery-status-badge status-unavailable';
        }
    } catch (error) {
        console.error('Error fetching battery status:', error);
    }
}

// Update battery status on load and every 2 seconds
updateBatteryStatus();
setInterval(updateBatteryStatus, 2000);
