import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import Auth from "./components/Auth";
import { Button } from "./components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import {
  Upload,
  FileText,
  Shield,
  Sparkles,
  CheckCircle,
  Clock,
  AlertCircle,
  LogOut,
  User,
  Brain,
  Zap,
} from "lucide-react";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(null);
  const [files, setFiles] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchUser = async () => {
      if (token) {
        try {
          axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
          const response = await axios.get("/api/v1/users/me");
          setUser(response.data);
          localStorage.setItem("token", token);
        } catch (error) {
          localStorage.removeItem("token");
          setToken(null);
          setUser(null);
          delete axios.defaults.headers.common["Authorization"];
        }
      } else {
        localStorage.removeItem("token");
        setUser(null);
        delete axios.defaults.headers.common["Authorization"];
      }
    };
    fetchUser();
  }, [token]);

  useEffect(() => {
    if (
      analysis &&
      analysis.id &&
      (analysis.status === "PENDING" || analysis.status === "IN_PROGRESS")
    ) {
      const poll = async (analysisId) => {
        const interval = setInterval(async () => {
          try {
            const response = await axios.get(`/api/v1/analyses/${analysisId}`);
            if (
              response.data.status === "COMPLETED" ||
              response.data.status === "FAILED"
            ) {
              clearInterval(interval);
              setAnalysis(response.data);
              setLoading(false);
            } else {
              setAnalysis(response.data);
            }
          } catch (err) {
            clearInterval(interval);
            setError("Failed to fetch analysis status.");
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
      setError("Please select at least one file to upload.");
      return;
    }

    const formData = new FormData();
    for (const file of files) {
      formData.append("files", file);
    }

    setLoading(true);
    setError("");
    setMessage("");
    setAnalysis(null);

    try {
      const response = await axios.post("/api/v1/analyses/", formData);

      if (response.data && response.data.length > 0) {
        // The UI is designed to track a single analysis, so we'll track the first one.
        setAnalysis(response.data[0]);
        setMessage(
          `Successfully uploaded ${files.length} file(s). Analysis started for ${response.data[0].file_name}.`
        );
        // Loading will be set to false inside the polling useEffect when analysis is complete/failed.
      } else {
        setError("No analysis data returned from server.");
        setLoading(false);
      }
    } catch (err) {
      console.error("Error uploading file:", err);
      setError("Failed to upload file.");
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
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 p-4 fixed inset-0 overflow-auto">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-indigo-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-purple-400/20 to-pink-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-cyan-400/10 to-blue-600/10 rounded-full blur-3xl animate-pulse"></div>
      </div>

      <div className="relative max-w-6xl mx-auto space-y-8 animate-fade-in">
        {/* Header Section */}
        <div className="text-center mb-8 animate-slide-up">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl mb-4 shadow-lg hover-lift animate-glow">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-200 bg-clip-text text-transparent mb-2">
            AI Contracts Manager
          </h1>
          <p className="text-gray-700 dark:text-gray-300 font-medium">
            Secure, intelligent contract analysis powered by AI
          </p>
        </div>

        {/* Main Dashboard Card */}
        <Card className="auth-card shadow-2xl hover-lift">
          <CardHeader className="space-y-1 pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-blue-600" />
                <CardTitle className="text-2xl font-semibold">
                  Welcome, {user.username || user.email}
                </CardTitle>
              </div>
              <Button
                variant="outline"
                onClick={handleLogout}
                className="flex items-center gap-2 hover:bg-red-50 hover:border-red-200 hover:text-red-600 transition-all duration-200"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </Button>
            </div>
            <CardDescription className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-500" />
              Upload your contract files for intelligent AI analysis
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* File Upload Section */}
            <Card className="border-2 border-dashed border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-700 transition-all duration-200 hover-lift">
              <CardContent className="p-6">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-3">
                    <Label
                      htmlFor="file-upload"
                      className="text-sm font-bold text-slate-800 dark:text-white flex items-center gap-2"
                    >
                      <FileText className="w-4 h-4 text-blue-600" />
                      Contract Files
                    </Label>
                    <div className="relative">
                      <Input
                        id="file-upload"
                        type="file"
                        onChange={handleFileChange}
                        multiple
                        accept=".pdf,.doc,.docx,.txt"
                        className="h-12 transition-all duration-200 focus:ring-2 focus:ring-blue-500/20 bg-white dark:bg-slate-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        disabled={loading}
                      />
                    </div>
                    {files.length > 0 && (
                      <div className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                        {files.length} file(s) selected
                      </div>
                    )}
                  </div>

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full h-12 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <Zap className="mr-2 h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Upload className="mr-2 h-4 w-4" />
                        Analyze Contract
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Status Messages */}
            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg animate-fade-in">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                  <p className="text-sm text-red-600 dark:text-red-400 font-medium">
                    {error}
                  </p>
                </div>
              </div>
            )}

            {message && (
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg animate-fade-in">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                  <p className="text-sm text-green-600 dark:text-green-400 font-medium">
                    {message}
                  </p>
                </div>
              </div>
            )}

            {/* Analysis Results */}
            {analysis && (
              <Card className="auth-card shadow-xl hover-lift animate-fade-in">
                <CardHeader className="pb-4">
                  <div className="flex items-center gap-3">
                    {analysis.status === "COMPLETED" && (
                      <CheckCircle className="w-6 h-6 text-green-500" />
                    )}
                    {(analysis.status === "PENDING" ||
                      analysis.status === "IN_PROGRESS") && (
                      <Clock className="w-6 h-6 text-blue-500 animate-spin" />
                    )}
                    {analysis.status === "FAILED" && (
                      <AlertCircle className="w-6 h-6 text-red-500" />
                    )}
                    <CardTitle className="text-xl font-semibold">
                      Analysis Status:
                      <span
                        className={`ml-2 px-3 py-1 rounded-full text-sm font-medium ${
                          analysis.status === "COMPLETED"
                            ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
                            : analysis.status === "FAILED"
                            ? "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
                            : "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400"
                        }`}
                      >
                        {analysis.status}
                      </span>
                    </CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  {analysis.status === "COMPLETED" && (
                    <div className="space-y-6">
                      <div className="p-6 bg-white dark:bg-slate-800 rounded-xl border-2 border-blue-200 dark:border-blue-700 shadow-lg hover-lift">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
                            <Sparkles className="w-5 h-5 text-white" />
                          </div>
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                            Summary
                          </h3>
                        </div>
                        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-lg border border-blue-100 dark:border-blue-800">
                          <p className="text-gray-800 dark:text-gray-100 leading-relaxed font-medium text-base">
                            {analysis.result.summary}
                          </p>
                        </div>
                      </div>

                      <div className="p-6 bg-white dark:bg-slate-800 rounded-xl border-2 border-purple-200 dark:border-purple-700 shadow-lg hover-lift">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                            <FileText className="w-5 h-5 text-white" />
                          </div>
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                            Key Clauses
                          </h3>
                        </div>
                        <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/30 dark:to-pink-900/30 rounded-lg border border-purple-100 dark:border-purple-800">
                          <ul className="space-y-3">
                            {analysis.result.clauses.map((clause, index) => (
                              <li
                                key={index}
                                className="flex items-start gap-3"
                              >
                                <div className="p-1 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mt-1 flex-shrink-0">
                                  <CheckCircle className="w-3 h-3 text-white" />
                                </div>
                                <span className="text-gray-800 dark:text-gray-100 leading-relaxed font-medium text-base">
                                  {clause}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}

                  {(analysis.status === "PENDING" ||
                    analysis.status === "IN_PROGRESS") && (
                    <div className="text-center py-8">
                      <Clock className="w-12 h-12 text-blue-500 mx-auto mb-4 animate-spin" />
                      <p className="text-gray-600 dark:text-gray-400 font-medium">
                        Your contract is being analyzed. This may take a few
                        moments...
                      </p>
                    </div>
                  )}

                  {analysis.status === "FAILED" && (
                    <div className="text-center py-8">
                      <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                      <p className="text-red-600 dark:text-red-400 font-medium">
                        Analysis failed. Please try uploading your file again.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center">
          <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
            Powered by AI • Secured by design
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
