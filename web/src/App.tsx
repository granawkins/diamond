import { useEffect, useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  const [ping, setPing] = useState(null)
  useEffect(() => {
    fetch('/api/ping')
      .then(response => response.json())
      .then(data => setPing(data.message))
  }, [])

  return (
    <>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
      <p>Ping: {ping}</p>
    </>
  )
}

export default App
