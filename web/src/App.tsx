import { useEffect, useState } from 'react'

import Battery from './components/Battery'
import Leg from './components/Leg'
import { sendCommand } from './utils'

function App() {
  const [status, setStatus] = useState(null)

  const fetchStatus = async () => {
    const response = await fetch('/api/status')
    const data = await response.json()
    setStatus(data)
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(() => {
      fetchStatus()
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <>
      <h1>Diamond</h1>
      <button onClick={() => sendCommand('reset')}>Reset</button>
      <Battery status={status} />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <div>
          <h2>Front Left</h2>
          <Leg leg="front_left" status={status} />
        </div>
        <div>
          <h2>Front Right</h2>
          <Leg leg="front_right" status={status} />
        </div>
        <div>
          <h2>Back Left</h2>
          <Leg leg="back_left" status={status} />
        </div>
        <div>
          <h2>Back Right</h2>
          <Leg leg="back_right" status={status} />
        </div>
      </div>
    </>
  )
}

export default App
