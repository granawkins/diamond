import type { Status } from '../types'

const Battery = ({ status }: { status?: Status | null }) => {
    const percentage = status?.battery?.percentage || 0
    const batteryStatus = status?.battery?.status || 'offline'
    return <div>Battery: {percentage}% ({batteryStatus})</div>
  }

  export default Battery