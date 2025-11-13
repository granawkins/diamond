import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import Origin from './Origin'

const Graph = ({
  showAxes,
  showGrid,
  children,
}: {
  showAxes: boolean
  showGrid: boolean
  children: React.ReactNode
}) => {
  return (
    <Canvas
      camera={{ position: [200, 120, 180], fov: 50 }}
      gl={{ alpha: true }}
    >
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <OrbitControls enableDamping dampingFactor={0.05} />
      <group rotation={[-Math.PI / 2, 0, Math.PI / 2]}>
        {showAxes && <Origin />}
        {showGrid && (
          <gridHelper
            args={[100, 10, '#444444', '#222222']}
            rotation={[-Math.PI / 2, 0, 0]}
          />
        )}
        {children}
      </group>
    </Canvas>
  )
}

export default Graph
