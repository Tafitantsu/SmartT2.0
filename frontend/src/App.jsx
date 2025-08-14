import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// --- Components ---

const TrafficLight = ({ color }) => (
  <div className="traffic-light">
    <div className={`light ${color === 'red' ? 'red' : ''}`}></div>
    <div className={`light ${color === 'yellow' ? 'yellow' : ''}`}></div>
    <div className={`light ${color === 'green' ? 'green' : ''}`}></div>
  </div>
);

const PedestrianLight = ({ color }) => (
    <div className={`ped-light ${color}`}>
        {color === 'green' ? 'WALK' : 'DONT WALK'}
    </div>
);


const Intersection = ({ state }) => {
  if (!state.lights) {
    return <div className="intersection-container">Loading...</div>;
  }

  return (
    <div className="intersection-container">
      <div className="road ns"></div>
      <div className="road ew"></div>

      {/* Traffic Lights */}
      <div className="light-ns-top"><TrafficLight color={state.lights.ns} /></div>
      <div className="light-ns-bottom"><TrafficLight color={state.lights.ns} /></div>
      <div className="light-ew-left"><TrafficLight color={state.lights.ew} /></div>
      <div className="light-ew-right"><TrafficLight color={state.lights.ew} /></div>

      {/* Pedestrian Lights */}
      <div className="ped-light-ns">
          <PedestrianLight color={state.pedestrian_lights.ns} />
      </div>
      <div className="ped-light-ew">
          <PedestrianLight color={state.pedestrian_lights.ew} />
      </div>


      {/* Vehicle Queues */}
      <div className="queue queue-ns-top">NS: {state.queues.ns}</div>
      <div className="queue queue-ew-right">EW: {state.queues.ew}</div>
    </div>
  );
};

const Controls = ({ ws }) => {
  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return (
    <div className="controls-container">
      <div className="control-group">
        <h3>Voitures</h3>
        <button onClick={() => sendMessage({ action: 'add_car', direction: 'NS' })}>Ajouter voiture NS</button>
        <button onClick={() => sendMessage({ action: 'add_car', direction: 'EW' })}>Ajouter voiture EW</button>
      </div>
      <div className="control-group">
        <h3>Piétons</h3>
        <button onClick={() => sendMessage({ action: 'pedestrian_request', direction: 'NS' })}>Demande piéton NS</button>
        <button onClick={() => sendMessage({ action: 'pedestrian_request', direction: 'EW' })}>Demande piéton EW</button>
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
        <Controls ws={ws} />
      </div>
    </>
  );
}

export default App;
