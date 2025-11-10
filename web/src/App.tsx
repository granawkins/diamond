import { useEffect, useState } from 'react'

import Battery from './components/Battery'
import Leg from './components/Leg'
import { sendCommand } from './utils'

function App() {
  const [state, setState] = useState(null)

  const fetchState = async () => {
    const response = await fetch('/api/state')
    const data = await response.json()
    console.log(data)
    setState(data)
  }

  useEffect(() => {
    fetchState()
    const interval = setInterval(() => {
      fetchState()
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <>
      <h1>Diamond</h1>
      <button onClick={() => sendCommand('reset')}>Reset</button>
      <Battery state={state} />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <div>
          <h2>Front Left</h2>
          <Leg leg="front_left" state={state} />
        </div>
        <div>
          <h2>Front Right</h2>
          <Leg leg="front_right" state={state} />
        </div>
        <div>
          <h2>Back Left</h2>
          <Leg leg="back_left" state={state} />
        </div>
        <div>
          <h2>Back Right</h2>
          <Leg leg="back_right" state={state} />
        </div>
      </div>
    </>
  )
}

export default App
