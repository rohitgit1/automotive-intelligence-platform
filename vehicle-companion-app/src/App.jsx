import { useState, useEffect } from 'react'
import { Activity } from 'lucide-react'
import DigitalTwin from './DigitalTwin'

function App() {
  const [otaStatus, setOtaStatus] = useState('nominal'); // nominal, detecting, receiving, applied
  const [temperature, setTemperature] = useState(-18.5);
  const [batteryHealth] = useState(98);
  const [otaPayload, setOtaPayload] = useState(null);
  const [time, setTime] = useState(new Date());

  // Clock
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Telemetry fluctuation
  useEffect(() => {
    const tempInterval = setInterval(() => {
      setTemperature(prev => {
        const variance = (Math.random() - 0.5) * 0.2;
        return Number((prev + variance).toFixed(1));
      });
    }, 2000);
    return () => clearInterval(tempInterval);
  }, []);

  const triggerSnowflakeOTA = () => {
    setOtaStatus('detecting');
    setTimeout(() => {
      setOtaPayload({
        version: "v4.8.2-bms",
        hash: "3e93f38af3c2b651f7edf0f5d0fe2b43e2bf2878a41ac5a6a921651fc9",
        timestamp: new Date().toISOString(),
      });
      setOtaStatus('receiving');
      
      setTimeout(() => {
        setOtaStatus('applied');
        setTemperature(5.2); 
      }, 7000);
    }, 3000);
  };

  const isCriticalTemp = temperature < -15 && otaStatus === 'nominal';

  return (
    <div className="modular-grid animate-fade-in">
      
      {/* Top Navigation - Spans all 12 columns */}
      <div className="grid-cell" style={{ gridColumn: 'span 12', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: '1.5rem 2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: '#EDEDED', borderRadius: '50%' }}></div>
          <span className="font-semibold tracking-widest text-sm" style={{ letterSpacing: '0.2em' }}>ACME AUTOMOTIVE</span>
        </div>
        <div style={{ display: 'flex', gap: '3rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div className="animate-pulse-subtle" style={{ width: '6px', height: '6px', backgroundColor: 'var(--color-success)', borderRadius: '50%' }}></div>
            <span className="text-xs text-secondary tracking-widest font-mono uppercase">Snowflake Core</span>
          </div>
          <span className="font-medium text-lg tracking-widest">{time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
        </div>
      </div>

      {/* Main Content Area */}
      {/* Left Module: Energy Subsystem */}
      <div className="grid-cell" style={{ gridColumn: 'span 4' }}>
        <div className="text-xs text-secondary tracking-widest uppercase mb-12">Energy Subsystem</div>
        
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div className="font-light text-6xl tracking-tight mb-2">{batteryHealth}<span className="text-2xl text-secondary">%</span></div>
          <div className="text-sm text-secondary tracking-wide uppercase">NMC811 Core Health</div>
          
          <div style={{ marginTop: '4rem', display: 'flex', gap: '3rem' }}>
            <div>
              <div className="text-xs text-secondary tracking-widest uppercase mb-1">Range</div>
              <div className="font-medium text-2xl tracking-tight">284 <span className="text-sm font-normal text-secondary">km</span></div>
            </div>
            <div>
              <div className="text-xs text-secondary tracking-widest uppercase mb-1">Voltage</div>
              <div className="font-medium text-2xl tracking-tight">384.2 <span className="text-sm font-normal text-secondary">V</span></div>
            </div>
          </div>
        </div>

        {/* Minimalist Battery Bar */}
        <div style={{ width: '100%', height: '2px', backgroundColor: 'var(--color-accent)', marginTop: 'auto' }}>
          <div style={{ width: `${batteryHealth}%`, height: '100%', backgroundColor: 'var(--color-text-primary)' }}></div>
        </div>
      </div>

      {/* Center Module: 3D Digital Twin */}
      <div className="grid-cell" style={{ gridColumn: 'span 4', position: 'relative', padding: 0 }}>
        
        {/* The 3D Canvas Background */}
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1 }}>
          <DigitalTwin temperature={temperature} otaStatus={otaStatus} />
        </div>

        {/* Overlay UI */}
        <div style={{ position: 'relative', zIndex: 2, padding: '2rem', display: 'flex', flexDirection: 'column', height: '100%', pointerEvents: 'none' }}>
          <div className="text-xs text-secondary tracking-widest uppercase mb-12">Thermal Dynamics</div>
          
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-start' }}>
            <div className={`font-light text-6xl tracking-tight mb-2 ${isCriticalTemp ? 'text-error animate-pulse-subtle' : 'text-primary'}`}>
              {temperature}<span className="text-2xl text-secondary">°C</span>
            </div>
            <div className="text-sm text-secondary tracking-wide uppercase">Ambient & Core Average</div>

            {/* Alert Status */}
            <div style={{ marginTop: 'auto', height: '60px' }}>
              {isCriticalTemp && (
                <div className="animate-slide-up" style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', color: 'var(--color-error)' }}>
                  <Activity size={18} style={{ marginTop: '2px' }} />
                  <div>
                    <div className="text-xs tracking-widest uppercase font-semibold mb-1">Critical Fault: P1794</div>
                    <div className="text-xs font-mono opacity-80" style={{ textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>Cathode impedance threshold exceeded.</div>
                  </div>
                </div>
              )}
              {otaStatus === 'applied' && (
                <div className="animate-slide-up" style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', color: 'var(--color-success)' }}>
                  <Activity size={18} style={{ marginTop: '2px' }} />
                  <div>
                    <div className="text-xs tracking-widest uppercase font-semibold mb-1">Thermal Mitigation Active</div>
                    <div className="text-xs font-mono opacity-80" style={{ textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>PTC pre-heating engaged.</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Right Module: System & Secure Terminal */}
      <div className="grid-cell" style={{ gridColumn: 'span 4', backgroundColor: 'var(--color-bg)' }}>
        <div className="text-xs text-secondary tracking-widest uppercase mb-12">Network & Operations</div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
          
          {otaStatus === 'nominal' && (
            <div className="animate-fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div className="text-xs text-secondary font-mono mb-4">sys_status: OK</div>
              <div className="font-light text-2xl tracking-tight mb-8">Firmware v4.8.1</div>
              <p className="text-sm text-secondary font-light leading-relaxed mb-12">
                Vehicle is connected to the Snowflake Automotive Intelligence Data Cloud. All systems nominal.
              </p>
              
              <button onClick={triggerSnowflakeOTA} className="btn-premium" style={{ alignSelf: 'flex-start' }}>
                Simulate Autonomous OTA
              </button>
            </div>
          )}

          {otaStatus === 'detecting' && (
            <div className="animate-fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', color: 'var(--color-text-primary)' }}>
              <div className="text-xs text-secondary font-mono mb-4">sys_status: INTERRUPT</div>
              <div className="font-light text-2xl tracking-tight mb-8 animate-pulse-subtle">Establishing Secure Handshake...</div>
              <div className="font-mono text-xs text-secondary" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <span className="typewriter">&gt; AUTHENTICATING VEHICLE ID...</span>
                <span className="typewriter" style={{ animationDelay: '0.5s' }}>&gt; VERIFYING RSA-4096 KEYS...</span>
                <span className="typewriter" style={{ animationDelay: '1.0s' }}>&gt; CONNECTING TO SNOWFLAKE CORE...</span>
              </div>
            </div>
          )}

          {otaStatus === 'receiving' && otaPayload && (
            <div className="animate-slide-up" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
              <div className="text-xs text-alert font-mono mb-4" style={{ color: 'var(--color-alert)' }}>sys_status: FLASHING_ROM</div>
              <div className="font-light text-2xl tracking-tight mb-6">CRITICAL OTA PAYLOAD</div>
              
              <div className="font-mono text-xs" style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', padding: '1.5rem', flex: 1 }}>
                <div style={{ color: 'var(--color-success)', marginBottom: '1rem' }}>&gt; DECRYPTED_PAYLOAD_READY</div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '100px 1fr', gap: '0.5rem', marginBottom: '1.5rem' }}>
                  <span className="text-secondary">VERSION:</span><span>{otaPayload.version}</span>
                  <span className="text-secondary">TIMESTAMP:</span><span>{otaPayload.timestamp}</span>
                  <span className="text-secondary">SHA256:</span><span style={{ wordBreak: 'break-all' }}>{otaPayload.hash}</span>
                </div>

                <div style={{ color: 'var(--color-secondary)', marginBottom: '0.5rem' }}>&gt; INJECTING_PARAMETERS:</div>
                <div style={{ color: 'var(--color-text-primary)', marginLeft: '1rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <span className="typewriter" style={{ animationDelay: '0s' }}>PTC_OFFSET_C = +12.5</span>
                  <span className="typewriter" style={{ animationDelay: '1s' }}>MAX_C_RATE_LIMIT = 0.45</span>
                  <span className="typewriter" style={{ animationDelay: '2s' }}>DELTA_V_CUTOFF = 38.0mV</span>
                </div>
              </div>
              
              <div style={{ marginTop: '2rem' }}>
                <div className="text-xs font-mono text-secondary mb-2" style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>FLASH PROGRESS</span>
                  <span className="animate-pulse-subtle">WRITING...</span>
                </div>
                <div style={{ width: '100%', height: '1px', backgroundColor: 'var(--color-accent)' }}>
                  <div style={{ width: '100%', height: '100%', backgroundColor: 'var(--color-success)', transformOrigin: 'left', animation: 'typing 7s linear forwards' }}></div>
                </div>
              </div>
            </div>
          )}

          {otaStatus === 'applied' && (
            <div className="animate-fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div className="text-xs text-success font-mono mb-4">sys_status: REBOOT_SUCCESS</div>
              <div className="font-light text-2xl tracking-tight mb-8">Firmware {otaPayload.version}</div>
              <p className="text-sm text-secondary font-light leading-relaxed">
                OTA successfully flashed and verified via Snowflake Intelligence Cloud. Thermal anomaly mitigations are active.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
