import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [loggedInUser, setLoggedInUser] = useState('')
  const welcomeRef = useRef(null)

  useEffect(() => {
    // Check if user is already logged in from localStorage
    const storedUser = localStorage.getItem('username')
    if (storedUser) {
      setIsLoggedIn(true)
      setLoggedInUser(storedUser)
    }
  }, [])

  useEffect(() => {
    // VULNERABILITY: Using innerHTML with user input - common mistake when formatting content
    // Developers often do this to add styling or formatting, not realizing the XSS risk
    if (isLoggedIn && welcomeRef.current) {
      // Developer's intent: "Let me format the username nicely with some styling"
      welcomeRef.current.innerHTML = `Hello, <strong>${loggedInUser}</strong>! Welcome back.`
    }
  }, [isLoggedIn, loggedInUser])

  const handleLogin = (e) => {
    e.preventDefault()
    
    // Simple authentication (vulnerable - no real backend)
    if (username && password) {
      setIsLoggedIn(true)
      setLoggedInUser(username)
      // VULNERABILITY: Storing user input in localStorage without sanitization
      localStorage.setItem('username', username)
      setUsername('')
      setPassword('')
    }
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setLoggedInUser('')
    localStorage.removeItem('username')
  }

  if (isLoggedIn) {
    return (
      <div className="container">
        <div className="card">
          <h1>Welcome!</h1>
          {/* VULNERABILITY: Using ref with innerHTML - looks innocent but is dangerous */}
          <p className="welcome-message" ref={welcomeRef}></p>
          <p className="info">You have successfully logged in.</p>
          <button onClick={handleLogout} className="btn btn-logout">
            Logout
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="card">
        <h1>Login</h1>
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="username">Username:</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="Enter username"
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter password"
            />
          </div>
          <button type="submit" className="btn btn-login">
            Login
          </button>
        </form>
        <p className="hint">
          Try logging in with: <code>admin</code> / <code>password</code>
        </p>
      </div>
    </div>
  )
}

export default App

