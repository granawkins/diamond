import { useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Text } from '@react-three/drei'

type Vec3 = [number, number, number]

const AXES = [
  { dir: [1, 0, 0] as Vec3, color: '#ff0000', label: 'X', rot: [0, 0, Math.PI / 2] as Vec3 },
  { dir: [0, 1, 0] as Vec3, color: '#00ff00', label: 'Y', rot: [0, 0, 0] as Vec3 },
  { dir: [0, 0, 1] as Vec3, color: '#0000ff', label: 'Z', rot: [Math.PI / 2, 0, 0] as Vec3 },
]

function Axes() {
  const length = 2
  return (
    <group>
      {AXES.map(({ dir: [x, y, z], color, label, rot }) => (
        <group key={label}>
          <mesh position={[x * length / 2, y * length / 2, z * length / 2]} rotation={rot}>
            <cylinderGeometry args={[0.02, 0.02, length, 8]} />
            <meshBasicMaterial color={color} />
          </mesh>
          <Text position={[x * 2.3, y * 2.3, z * 2.3]} fontSize={0.3} color={color}>
            {label}
          </Text>
        </group>
      ))}
    </group>
  )
}

const Graph = () => {
  const [showAxes, setShowAxes] = useState(true)
  const [showGrid, setShowGrid] = useState(true)

  return (
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
          {showAxes && <Axes />}
          <OrbitControls enableDamping dampingFactor={0.05} />
          {showGrid && <gridHelper args={[10, 10, '#444444', '#222222']} />}
        </Canvas>
      </div>
    </div>
  )
}

export default Graph