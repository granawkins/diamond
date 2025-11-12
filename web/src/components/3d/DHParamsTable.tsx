import { useState, useEffect, useCallback } from 'react'
import Graph from './Graph'
import KinematicChain from './KinematicChain'
import type { Vec3, DHParams } from '../../types'

const DEFAULT_DH_PARAMS = [
  { alpha: 0, a: 0, d: 15.5, theta: Math.PI / 2 },
  { alpha: -Math.PI / 2, a: -9.3, d: 21.1, theta: -2.1 },
  { alpha: 0, a: 63.25, d: 0, theta: -2 },
  { alpha: 0, a: 82.5, d: 0, theta: 0 },
]

const DHParamsTable = ({
  setPositions,
}: {
  setPositions: (positions: Vec3[]) => void
}) => {
  const [dhParams, setDhParams] = useState<DHParams[]>(DEFAULT_DH_PARAMS)

  const fetchKinematics = useCallback(async () => {
    const response = await fetch('/api/kinematics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dh_params: dhParams }),
    })
    const data = await response.json()
    setPositions(data.positions || [])
  }, [dhParams, setPositions])

  useEffect(() => {
    fetchKinematics()
  }, [fetchKinematics])

  const updateDHParam = (
    rowIndex: number,
    field: keyof DHParams,
    value: string
  ) => {
    const numValue = parseFloat(value)
    if (isNaN(numValue)) return

    const newParams = [...dhParams]
    newParams[rowIndex] = { ...newParams[rowIndex], [field]: numValue }
    setDhParams(newParams)
  }

  return (
    <div>
      <h3>DH Parameters</h3>
      <button onClick={() => setDhParams(DEFAULT_DH_PARAMS)}>Reset</button>
      <table>
        <thead>
          <tr>
            <th>Link</th>
            <th>alpha (rad)</th>
            <th>a</th>
            <th>d</th>
            <th>theta (rad)</th>
          </tr>
        </thead>
        <tbody>
          {dhParams.map((params, i) => {
            const label = i === 3 ? 'E' : (i + 1).toString()
            return (
              <tr key={i}>
                <td>{label}</td>
                {(['alpha', 'a', 'd', 'theta'] as const).map((field) => (
                  <td key={field}>
                    <input
                      type="number"
                      step="0.1"
                      value={params[field]}
                      onChange={(e) => updateDHParam(i, field, e.target.value)}
                      style={{ width: '80px' }}
                    />
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

const DHEditor = () => {
  const [showAxes, setShowAxes] = useState(true)
  const [showGrid, setShowGrid] = useState(true)
  const [positions, setPositions] = useState<Vec3[]>([])

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'row',
        gap: '10px',
        border: '1px solid black',
        height: '600px',
      }}
    >
      <div style={{ width: '50%' }}>
        <DHParamsTable setPositions={setPositions} />
      </div>
      <div style={{ width: '50%', position: 'relative' }}>
        <div
          style={{ position: 'absolute', top: '0', left: '0', zIndex: 1000 }}
        >
          <label style={{ marginRight: '15px' }}>
            <input
              type="checkbox"
              checked={showAxes}
              onChange={(e) => setShowAxes(e.target.checked)}
            />{' '}
            Axes
          </label>
          <label>
            <input
              type="checkbox"
              checked={showGrid}
              onChange={(e) => setShowGrid(e.target.checked)}
            />{' '}
            Grid
          </label>
        </div>
        <Graph showAxes={showAxes} showGrid={showGrid}>
          <KinematicChain positions={positions} key="dh-editor" />
        </Graph>
      </div>
    </div>
  )
}

export default DHEditor
