import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Environment, Float, Sparkles } from '@react-three/drei'
import * as THREE from 'three'

// The core 3D battery object
function BatteryCore({ isCritical, otaStatus }) {
  const group = useRef()
  const innerCore = useRef()
  
  // Dynamic colors based on state
  const targetColor = useMemo(() => {
    if (otaStatus === 'applied') return new THREE.Color('#4ADE80') // Success Green
    if (otaStatus === 'receiving') return new THREE.Color('#FBBF24') // Alert Yellow
    if (isCritical) return new THREE.Color('#F87171') // Error Red
    return new THREE.Color('#0EA5E9') // Nominal Cyan
  }, [isCritical, otaStatus])

  useFrame((state, delta) => {
    // Smooth color transition
    if (innerCore.current) {
      innerCore.current.material.color.lerp(targetColor, 0.05)
      innerCore.current.material.emissive.lerp(targetColor, 0.05)
    }

    // Dynamic rotation based on state
    if (group.current) {
      const baseSpeed = 0.5
      let speedMult = 1
      
      if (isCritical && otaStatus === 'nominal') {
        speedMult = 4.0 // Erratic fast spinning when hot
        group.current.rotation.x = Math.sin(state.clock.elapsedTime * 15) * 0.04 // Vibration shake without drift
      } else if (otaStatus === 'receiving') {
        speedMult = 0.1 // Slow down for firmware flash
        group.current.rotation.x = THREE.MathUtils.lerp(group.current.rotation.x, 0, 0.1)
      } else {
        group.current.rotation.x = THREE.MathUtils.lerp(group.current.rotation.x, 0, 0.1)
      }
      
      group.current.rotation.y += delta * baseSpeed * speedMult
    }
  })

  return (
    <group ref={group}>
      <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
        
        {/* Outer Holographic Shell */}
        <mesh>
          <boxGeometry args={[3, 1, 4]} />
          <meshBasicMaterial color="#ffffff" wireframe={true} transparent opacity={0.1} />
        </mesh>
        
        {/* Inner Battery Modules */}
        <mesh ref={innerCore} position={[0, 0, 0]}>
          <boxGeometry args={[2.6, 0.6, 3.6]} />
          <meshStandardMaterial 
            color="#0EA5E9"
            emissive="#0EA5E9"
            emissiveIntensity={isCritical ? 2 : 0.5}
            transparent 
            opacity={0.8}
            roughness={0.2}
            metalness={0.8}
          />
        </mesh>

        {/* Ambient energy particles */}
        <Sparkles 
          count={50} 
          scale={5} 
          size={isCritical ? 6 : 2} 
          speed={isCritical ? 0.8 : 0.2} 
          opacity={0.5} 
          color={targetColor}
        />

      </Float>
    </group>
  )
}

export default function DigitalTwin({ temperature, otaStatus }) {
  const isCritical = temperature < -15 && otaStatus === 'nominal'

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      
      {/* 3D Canvas */}
      <Canvas camera={{ position: [5, 3, 5], fov: 45 }}>
        <color attach="background" args={['#060608']} /> {/* Matches Deep Onyx bg */}
        
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <spotLight position={[-10, 10, -10]} intensity={0.5} color="#0EA5E9" />
        
        <BatteryCore isCritical={isCritical} otaStatus={otaStatus} />
        
        {/* Minimal interaction */}
        <OrbitControls 
          enableZoom={false} 
          enablePan={false} 
          minPolarAngle={Math.PI / 4} 
          maxPolarAngle={Math.PI / 2.5} 
          autoRotate={false}
        />
        
        <Environment preset="city" />
      </Canvas>

      {/* Overlay UI for the 3D View */}
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', pointerEvents: 'none', display: 'flex', justifyContent: 'space-between' }}>
        <div className="font-mono text-xs text-secondary tracking-widest">
          TWIN_SYNC: <span style={{ color: isCritical && otaStatus==='nominal' ? 'var(--color-error)' : 'var(--color-success)'}}>LIVE</span>
        </div>
        <div className="font-mono text-xs text-secondary tracking-widest">
          MODEL: NMC811_STRUCTURAL
        </div>
      </div>

    </div>
  )
}
