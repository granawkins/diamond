
export const sendCommand = async (command: string) => {
    const response = await fetch('/api/command', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ command: command })
    })
    const data = await response.json()
    if (!data.success) {
      console.error('Failed to execute command:', data)
    }
  }