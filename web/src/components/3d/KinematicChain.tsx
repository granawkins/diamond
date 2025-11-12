import { Line } from '@react-three/drei'

import type { Vec3 } from '../../types'

const KinematicChain = ({
  positions,
  key,
}: {
  positions: Vec3[]
  key: string
}) => {
  if (!positions || positions.length === 0) return null
  return (
    <group>
      {positions.map((pos, i) => (
        <mesh key={`joint-${i}-${key}`} position={pos}>
          <sphereGeometry args={[1, 16, 16]} />
          <meshStandardMaterial color={"red"}/>
        </mesh>
      ))}
      {positions.slice(1).map((pos, i) => {
        const start = positions[i]
        return (
          <Line
            key={`line-${i}-${key}`}
            points={[start, pos]}
            color={"black"}
            lineWidth={3}
          />
        )
      })}
    </group>
  )
}

export default KinematicChain
