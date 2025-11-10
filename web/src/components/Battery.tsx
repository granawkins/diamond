import type { State } from '../types'

const Battery = ({ state }: { state?: State | null }) => {
  const percentage = state?.battery?.percentage || 0
  const status = state?.battery?.status || 'offline'
  return (
    <div>
      Battery: {percentage}% ({status})
    </div>
  )
}

export default Battery
