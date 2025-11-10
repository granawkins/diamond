import { useState, useEffect, useCallback } from 'react'
import type { Vec3, DHParams } from '../../types'

const DEFAULT_DH_PARAMS = [
  { alpha: 0, a: 1, d: 0, theta: 0 },
  { alpha: 0, a: 1, d: 0, theta: 0 },
  { alpha: 0, a: 1, d: 0, theta: 0 },
  { alpha: 0, a: 1, d: 0, theta: 0 },
]

 const DHParamsTable = ({ setPositions }: { setPositions: (positions: Vec3[]) => void }) => {
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

  const updateDHParam = (rowIndex: number, field: keyof DHParams, value: string) => {
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

 export default DHParamsTable