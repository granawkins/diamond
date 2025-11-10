import { Text, Line } from '@react-three/drei'

import type { Vec3 } from '../../types'

function Origin({
  position = [0, 0, 0] as Vec3,
  rotation = [0, 0, 0] as Vec3,
}: {
  position?: Vec3
  rotation?: Vec3
}) {
  const length = 2
  const axes = [
    { end: [length, 0, 0] as Vec3, color: '#ff0000', label: 'X' },
    { end: [0, length, 0] as Vec3, color: '#00ff00', label: 'Y' },
    { end: [0, 0, length] as Vec3, color: '#0000ff', label: 'Z' },
  ]

  return (
    <group position={position} rotation={rotation}>
      {axes.map(({ end, color, label }) => (
        <group key={label}>
          <Line points={[[0, 0, 0], end]} color={color} lineWidth={1} />
          <Text position={end} fontSize={0.3} color={color}>
            {label}
          </Text>
        </group>
      ))}
    </group>
  )
}

export default Origin
