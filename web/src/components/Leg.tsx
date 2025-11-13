import type { LegState, JointState } from '../types'
import { sendCommand } from '../utils'

const round = (value: number) => {
  return Math.round(value * 10) / 10
}

const fieldStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'row',
  justifyContent: 'space-between',
}

const EditableField = ({
  label,
  value,
  path,
}: {
  label: string
  value: number
  path: string
}) => {
  return (
    <tr style={fieldStyle}>
      {label}:
      <input
        type="number"
        value={round(value)}
        onChange={(e) => sendCommand(`set_${path}_${e.target.value}`)}
        style={{ width: '80px' }}
      />
    </tr>
  )
}

const Joint = ({
  name,
  state,
}: {
  name: string
  state?: JointState | null
}) => {
  const angle = state?.angle || 0
  const actual = state?.actual || 0
  const m = state?.m || 0
  const b = state?.b || 0
  return (
    <tr style={{ border: '1px solid black' }}>
      <td>{name.split('_').slice(2, 4).join('_')}</td>
      <td style={{ width: '100%' }}>
        <EditableField label="angle" value={angle} path={`${name}_angle`} />
        <tr style={fieldStyle}>
          <span>actual:</span>
          <span>{round(actual)}</span>
        </tr>
        <EditableField label="m" value={m} path={`${name}_m`} />
        <EditableField label="b" value={b} path={`${name}_b`} />
      </td>
    </tr>
  )
}

const Leg = ({ name, state }: { name: string; state?: LegState | null }) => {
  return (
    <table style={{ border: '1px solid black', borderCollapse: 'collapse' }}>
      <tbody style={{ verticalAlign: 'top', textAlign: 'left' }}>
        <tr>
          <td>{name}</td>
          <Joint name={`${name}_lower_hip`} state={state?.lower_hip} />
          <Joint name={`${name}_upper_hip`} state={state?.upper_hip} />
          <Joint name={`${name}_shoulder`} state={state?.shoulder} />
        </tr>
      </tbody>
    </table>
  )
}

export default Leg
