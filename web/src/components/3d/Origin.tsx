import { Text, Line } from '@react-three/drei'

import type { Vec3 } from '../../types'

function Origin({
  position = [0, 0, 0] as Vec3,
  rotation = [0, 0, 0] as Vec3,
}: {
  position?: Vec3
  rotation?: Vec3
}) {
  const length = 20
  const axes = [
    { end: [length, 0, 0] as Vec3, color: '#ff0000', label: 'X' },
    { end: [0, length, 0] as Vec3, color: '#00ff00', label: 'Y' },
    { end: [0, 0, length] as Vec3, color: '#0000ff', label: 'Z' },
  ]

  return (
    <group position={position} rotation={rotation}>
      {axes.map(({ end, color, label }) => {
        const labelPos = end.map((c: number) => c > 0 ? c * 1.1 : c) as Vec3
        return (          
          <group key={label}>
            <Line points={[[0, 0, 0], end]} color={color} lineWidth={2} />
            <Text position={labelPos} fontSize={3} color={'black'}>
              {label}
            </Text>
          </group>
        )
      })}
    </group>
  )
}

export default Origin
