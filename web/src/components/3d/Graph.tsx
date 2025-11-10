import { useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Line } from '@react-three/drei'
import Origin from './Origin'
import type { Vec3 } from '../../types'
import DHParamsTable from './DHParamsTable'

const COLORS = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']

const KinematicChain = ({ positions }: { positions: Vec3[] }) => {
  return (
    <group>
      {positions.map((pos, i) => (
        <mesh key={`joint-${i}`} position={pos}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial color={i === 0 ? '#ffffff' : COLORS[(i - 1) % COLORS.length]} />
        </mesh>
      ))}
      {positions.slice(1).map((pos, i) => {
        const start = positions[i]
        const color = COLORS[i % COLORS.length]
        return (
          <Line
            key={`line-${i}`}
            points={[start, pos]}
            color={color}
            lineWidth={3}
          />
        )
      })}
    </group>
  )
}

const Graph = () => {
  const [showAxes, setShowAxes] = useState(true)
  const [showGrid, setShowGrid] = useState(true)
  const [positions, setPositions] = useState<Vec3[]>([])

  return (
    <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
      <div>
        <div style={{ marginBottom: '10px' }}>
          <label style={{ marginRight: '15px' }}>
            <input
              type="checkbox"
              checked={showAxes}
              onChange={(e) => setShowAxes(e.target.checked)}
            />
            {' '}Axes
          </label>
          <label>
            <input
              type="checkbox"
              checked={showGrid}
              onChange={(e) => setShowGrid(e.target.checked)}
            />
            {' '}Grid
          </label>
        </div>
        <div style={{ width: '600px', height: '600px' }}>
          <Canvas camera={{ position: [4, 4, 6], fov: 50 }} gl={{ alpha: true }}>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} />
            {showAxes && <Origin />}
            <KinematicChain positions={positions} />
            <OrbitControls enableDamping dampingFactor={0.05} />
            {showGrid && <gridHelper args={[10, 10, '#444444', '#222222']} />}
          </Canvas>
        </div>
      </div>

      <DHParamsTable setPositions={setPositions} />
    </div>
  )
}

export default Graph