import type { Status } from '../types'

const Leg = ({ leg, status }: { leg: string, status?: Status | null }) => {
    const angles = status?.legs[leg] || [0, 0, 0]
    return <div>Leg: {leg} - {angles.join(', ')}</div>
}

export default Leg