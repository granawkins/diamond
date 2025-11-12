import type { State } from '../types'

const Joint = ({ name, angle }: { name: string; angle: number }) => {
  return (
    <div>
      {name}: {angle}
    </div>
  )
}

const Leg = ({ leg, state }: { leg: string; state?: State | null }) => {
  const angles = state?.legs[leg as keyof typeof state.legs] || {
    lower_hip: 0,
    upper_hip: 0,
    shoulder: 0,
  }
  return (
    <>
      <Joint name="lower_hip" angle={angles.lower_hip} />
      <Joint name="upper_hip" angle={angles.upper_hip} />
      <Joint name="shoulder" angle={angles.shoulder} />
    </>
  )
}

export default Leg
