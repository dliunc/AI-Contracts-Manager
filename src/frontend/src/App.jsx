import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Auth from './components/Auth';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [files, setFiles] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      if (token) {
        try {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          const response = await axios.get('/api/v1/users/me');
          setUser(response.data);
          localStorage.setItem('token', token);
        } catch (error) {
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
          delete axios.defaults.headers.common['Authorization'];
        }
      } else {
        localStorage.removeItem('token');
        setUser(null);
        delete axios.defaults.headers.common['Authorization'];
      }
    };
    fetchUser();
  }, [token]);

  useEffect(() => {
    if (analysis && analysis.id && (analysis.status === 'PENDING' || analysis.status === 'IN_PROGRESS')) {
      const poll = async (analysisId) => {
        const interval = setInterval(async () => {
          try {
            const response = await axios.get(`/api/v1/analyses/${analysisId}`);
            if (response.data.status === 'COMPLETED' || response.data.status === 'FAILED') {
              clearInterval(interval);
              setAnalysis(response.data[0]);
              setLoading(false);
            } else {
              setAnalysis(response.data[0]);
            }
          } catch (err) {
            clearInterval(interval);
            setError('Failed to fetch analysis status.');
            setLoading(false);
          }
        }, 3000); // Poll every 3 seconds
        return () => clearInterval(interval);
      };
      poll(analysis.id);
    }
  }, [analysis]);

  const handleFileChange = (event) => {
    if (event.target.files && event.target.files.length > 0) {
      setFiles(Array.from(event.target.files));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (files.length === 0) {
      setError('Please select at least one file to upload.');
      return;
    }

    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }
 
    setLoading(true);
    setError('');
    setMessage('');
    setAnalysis(null);

    try {
      const response = await axios.post('/api/v1/analyses/', formData);

      if (response.data && response.data.length > 0) {
        // The UI is designed to track a single analysis, so we'll track the first one.
        setAnalysis(response.data[0]);
        setMessage(`Successfully uploaded ${files.length} file(s). Analysis started for ${response.data[0].file_name}.`);
        // Loading will be set to false inside the polling useEffect when analysis is complete/failed.
      } else {
        setError('No analysis data returned from server.');
        setLoading(false);
      }
    } catch (err) {
      console.error('Error uploading file:', err);
      setError('Failed to upload file.');
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
  };

  if (!user) {
    return <Auth setToken={setToken} />;
  }

  return (
    <>
      <h1>AI Contracts Manager</h1>
      <div className="card">
        <p>Welcome, {user.email}</p>
        <button onClick={handleLogout}>Logout</button>
        <form onSubmit={handleSubmit}>
          <input type="file" onChange={handleFileChange} multiple />
          <button type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze Contract'}
          </button>
        </form>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {message && <p style={{ color: 'green' }}>{message}</p>}
        {analysis && (
          <div>
            <h2>Analysis Status: {analysis.status}</h2>
            {analysis.status === 'COMPLETED' && (
              <div>
                <h3>Summary:</h3>
                <p>{analysis.result.summary}</p>
                <h3>Key Clauses:</h3>
                <ul>
                  {analysis.result.clauses.map((clause, index) => (
                    <li key={index}>{clause}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}

export default App