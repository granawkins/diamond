import { useEffect, useState } from 'react'

import Battery from './components/Battery'
import Leg from './components/Leg'
import { sendCommand } from './utils'
import DHEditor from './components/3d/DHParamsTable'
import Graph from './components/3d/Graph'
import KinematicChain from './components/3d/KinematicChain'
import type { State } from './types'

function App() {
  const [state, setState] = useState<State | null>(null)
  const [editor, setEditor] = useState<boolean>(false)

  const fetchState = async () => {
    const response = await fetch('/api/state')
    const data = await response.json()
    setState(data)
  }

  useEffect(() => {
    fetchState()
    const interval = setInterval(() => {
      fetchState()
    }, 1000 / 24)
    return () => clearInterval(interval)
  }, [])

  const command = (cmd: string) => {
    sendCommand(cmd)
  }

  return (
    <>
      <h1>Diamond</h1>
      <Battery state={state} />
      <button onClick={() => command('reset')}>Reset</button>
      <button onClick={() => command('up')}>Up</button>
      <button onClick={() => command('down')}>Down</button>
      <button onClick={() => command('walk_forward')}>Walk Forward</button>
      <button onClick={() => command('stop')}>Stop</button>
      <input
        type="checkbox"
        checked={editor}
        onChange={() => setEditor(!editor)}
      />
      {editor ? (
        <DHEditor />
      ) : (
        <div style={{ width: '800px', height: '400px' }}>
          <Graph showAxes={true} showGrid={true}>
            {state?.legs && (
              <>
                <KinematicChain
                  positions={state.legs.front_left.positions}
                  key="front_left"
                />
                <KinematicChain
                  positions={state.legs.front_right.positions}
                  key="front_right"
                />
                <KinematicChain
                  positions={state.legs.back_left.positions}
                  key="back_left"
                />
                <KinematicChain
                  positions={state.legs.back_right.positions}
                  key="back_right"
                />
              </>
            )}
          </Graph>
        </div>
      )}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '10px',
          maxWidth: '800px',
        }}
      >
        <Leg name="front_left" state={state?.legs?.front_left} />
        <Leg name="front_right" state={state?.legs?.front_right} />
        <Leg name="back_left" state={state?.legs?.back_left} />
        <Leg name="back_right" state={state?.legs?.back_right} />
      </div>
    </>
  )
}

export default App
