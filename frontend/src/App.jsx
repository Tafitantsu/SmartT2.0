import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// --- Components ---

const PedestrianLight = ({ color }) => {
    const isWalk = color === 'green';
    return (
        <div className={`pedestrian-light ${isWalk ? 'walk' : 'dont-walk'}`}>
            {isWalk ? 'WALK' : "DON'T WALK"}
        </div>
    );
};

const Car = () => <div className="car"></div>;

const CarQueue = ({ count, direction }) => (
  <div className={`car-queue ${direction}`}>
    {Array.from({ length: Math.min(count, 20) }, (_, i) => <Car key={i} />)}
  </div>
);

const Intersection = ({ state }) => {
  if (!state.lights || !state.queues || !state.pedestrian_lights) {
    return <div className="intersection">Loading...</div>;
  }

  const nsLight = state.lights.ns;
  const ewLight = state.lights.ew;
  const nsPedLight = state.pedestrian_lights.ns;
  const ewPedLight = state.pedestrian_lights.ew;

  const nsQueue = state.queues.ns || 0;
  const ewQueue = state.queues.ew || 0;

  return (
    <div className="intersection">
        <div className="road-horizontal"></div>
        <div className="road-vertical"></div>

        {/* Car Queues */}
        <CarQueue count={Math.floor(nsQueue / 2)} direction="ns-top" />
        <CarQueue count={Math.ceil(nsQueue / 2)} direction="ns-bottom" />
        <CarQueue count={Math.floor(ewQueue / 2)} direction="ew-left" />
        <CarQueue count={Math.ceil(ewQueue / 2)} direction="ew-right" />


        <div className="corner top-left">
            {/* Pedestrians crossing NS road */}
            <PedestrianLight color={nsPedLight} />
            <div className="traffic-light">
                <small>F1</small>
                <div className={`light ${nsLight === 'red' ? 'red' : ''}`}></div>
                <div className={`light ${nsLight === 'yellow' ? 'yellow' : ''}`}></div>
                <div className={`light ${nsLight === 'green' ? 'green' : ''}`}></div>
            </div>
        </div>

        <div className="corner top-right">
            {/* Pedestrians crossing EW road */}
            <PedestrianLight color={ewPedLight} />
            <div className="traffic-light">
                <small>F2</small>
                <div className={`light ${ewLight === 'red' ? 'red' : ''}`}></div>
                <div className={`light ${ewLight === 'yellow' ? 'yellow' : ''}`}></div>
                <div className={`light ${ewLight === 'green' ? 'green' : ''}`}></div>
            </div>
        </div>

        <div className="corner bottom-left">
            {/* Pedestrians crossing EW road */}
            <PedestrianLight color={ewPedLight} />
            <div className="traffic-light">
                <small>F3</small>
                <div className={`light ${ewLight === 'red' ? 'red' : ''}`}></div>
                <div className={`light ${ewLight === 'yellow' ? 'yellow' : ''}`}></div>
                <div className={`light ${ewLight === 'green' ? 'green' : ''}`}></div>
            </div>
        </div>

        <div className="corner bottom-right">
            {/* Pedestrians crossing NS road */}
            <PedestrianLight color={nsPedLight} />
            <div className="traffic-light">
                <small>F4</small>
                <div className={`light ${nsLight === 'red' ? 'red' : ''}`}></div>
                <div className={`light ${nsLight === 'yellow' ? 'yellow' : ''}`}></div>
                <div className={`light ${nsLight === 'green' ? 'green' : ''}`}></div>
            </div>
        </div>
    </div>
  );
};

const Controls = ({ ws, demands, semiAutomaticMode }) => {
  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  const nsDemand = demands?.ns === 1;
  const ewDemand = demands?.ew === 1;

  return (
    <div className="controls-container">
      <div className="control-group">
        <h3>Voitures</h3>
        <button onClick={() => sendMessage({ action: 'add_car', direction: 'NS' })}>Ajouter voiture NS</button>
        <button onClick={() => sendMessage({ action: 'add_car', direction: 'EW' })}>Ajouter voiture EW</button>
      </div>
      <div className="control-group">
        <h3>Piétons</h3>
        <button
          onClick={() => sendMessage({ action: 'pedestrian_request', direction: 'NS' })}
          className={nsDemand ? 'demand-active' : ''}
          disabled={nsDemand}
        >
          Demande piéton NS {nsDemand && '...'}
        </button>
        <button
          onClick={() => sendMessage({ action: 'pedestrian_request', direction: 'EW' })}
          className={ewDemand ? 'demand-active' : ''}
          disabled={ewDemand}
        >
          Demande piéton EW {ewDemand && '...'}
        </button>
      </div>
      <div className="control-group">
        <h3>Système</h3>
        <button
          onClick={() => sendMessage({ action: 'toggle_semi_automatic_mode' })}
          className={semiAutomaticMode ? 'demand-active' : ''}
        >
          Mode semi-auto {semiAutomaticMode ? 'Activé' : 'Désactivé'}
        </button>
      </div>
    </div>
  );
};


// --- Main App Component ---

function App() {
  const [simulationState, setSimulationState] = useState({});
  const ws = useRef(null);

  useEffect(() => {
    // Connect to the WebSocket server
    ws.current = new WebSocket('ws://localhost:8000/ws');

    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setSimulationState(data);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
    };

    ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    // Cleanup on component unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  return (
    <>
      <h1>Simulation d'Intersection</h1>
      <div className="simulation-container">
        <Intersection state={simulationState} />
        <Controls ws={ws} demands={simulationState.demands} semiAutomaticMode={simulationState.semi_automatic_mode} />
      </div>
    </>
  );
}

export default App;
