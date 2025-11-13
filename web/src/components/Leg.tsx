import type { LegState, JointState } from '../types'
import { sendCommand } from '../utils'

const round = (value: number) => {
  return Math.round(value * 10) / 10
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
    <tr>
      <td>{name.split('_').slice(2, 4).join('_')}</td>
      <td>
        <tr>
          <button
            onClick={() => sendCommand(`set_${name}_angle_${round(angle - 1)}`)}
          >
            -
          </button>
          {`angle: ${round(angle)}`}
          <button
            onClick={() => sendCommand(`set_${name}_angle_${round(angle + 1)}`)}
          >
            +
          </button>
        </tr>
        <tr>{`actual: ${round(actual)}`}</tr>
        <tr>{`m: ${m}`}</tr>
        <tr>{`b: ${b}`}</tr>
      </td>
    </tr>
  )
}

const Leg = ({ name, state }: { name: string; state?: LegState | null }) => {
  return (
    <table style={{ border: '1px solid black' }}>
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
