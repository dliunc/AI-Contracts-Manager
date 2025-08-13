import { useState } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { User, Lock, Mail, Loader2, Shield, Sparkles } from "lucide-react";

const Auth = ({ setToken }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [loginData, setLoginData] = useState({ username: "", password: "" });
  const [registerData, setRegisterData] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("login");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await axios.post(
        "/api/v1/auth/token",
        new URLSearchParams(loginData),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );
      setToken(response.data.access_token);
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await axios.post("/api/v1/auth/register", registerData, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      setActiveTab("login");
      setError("");
      // Show success message or auto-switch to login
    } catch (err) {
      setError(
        err.response?.data?.detail || "Registration failed. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 p-4 fixed inset-0">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-indigo-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-purple-400/20 to-pink-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-cyan-400/10 to-blue-600/10 rounded-full blur-3xl animate-pulse"></div>
      </div>

      <div className="relative w-full max-w-md animate-fade-in">
        {/* Logo/Brand Section */}
        <div className="text-center mb-8 animate-slide-up">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl mb-4 shadow-lg hover-lift animate-glow">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-200 bg-clip-text text-transparent">
            AI Contracts Manager
          </h1>
          <p className="text-gray-700 dark:text-gray-300 mt-2 font-medium">
            Secure, intelligent contract analysis
          </p>
        </div>

        <Card className="auth-card shadow-2xl hover-lift">
          <CardHeader className="space-y-1 pb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-600" />
              <CardTitle className="text-2xl font-semibold">Welcome</CardTitle>
            </div>
            <CardDescription>
              Sign in to your account or create a new one to get started
            </CardDescription>
          </CardHeader>

          <CardContent>
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="w-full"
            >
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="login" className="text-sm font-medium">
                  Sign In
                </TabsTrigger>
                <TabsTrigger value="register" className="text-sm font-medium">
                  Sign Up
                </TabsTrigger>
              </TabsList>

              <TabsContent value="login" className="space-y-4">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label
                      htmlFor="login-username"
                      className="text-sm font-bold text-slate-800 dark:text-white"
                    >
                      Username
                    </Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 w-4 h-4" />
                      <Input
                        id="login-username"
                        type="text"
                        placeholder="Enter your username"
                        value={loginData.username}
                        onChange={(e) =>
                          setLoginData({
                            ...loginData,
                            username: e.target.value,
                          })
                        }
                        className="pl-10 h-11 transition-all duration-200 focus:ring-2 focus:ring-blue-500/20 bg-white dark:bg-slate-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
                        required
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label
                      htmlFor="login-password"
                      className="text-sm font-bold text-slate-800 dark:text-white"
                    >
                      Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 w-4 h-4" />
                      <Input
                        id="login-password"
                        type="password"
                        placeholder="Enter your password"
                        value={loginData.password}
                        onChange={(e) =>
                          setLoginData({
                            ...loginData,
                            password: e.target.value,
                          })
                        }
                        className="pl-10 h-11 transition-all duration-200 focus:ring-2 focus:ring-blue-500/20 bg-white dark:bg-slate-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
                        required
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <Button
                    type="submit"
                    className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Signing in...
                      </>
                    ) : (
                      "Sign In"
                    )}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="register" className="space-y-4">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="space-y-2">
                    <Label
                      htmlFor="register-username"
                      className="text-sm font-bold text-slate-800 dark:text-white"
                    >
                      Username
                    </Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 w-4 h-4" />
                      <Input
                        id="register-username"
                        type="text"
                        placeholder="Choose a username"
                        value={registerData.username}
                        onChange={(e) =>
                          setRegisterData({
                            ...registerData,
                            username: e.target.value,
                          })
                        }
                        className="pl-10 h-11 transition-all duration-200 focus:ring-2 focus:ring-blue-500/20 bg-white dark:bg-slate-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
                        required
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label
                      htmlFor="register-email"
                      className="text-sm font-bold text-slate-800 dark:text-white"
                    >
                      Email
                    </Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 w-4 h-4" />
                      <Input
                        id="register-email"
                        type="email"
                        placeholder="Enter your email"
                        value={registerData.email}
                        onChange={(e) =>
                          setRegisterData({
                            ...registerData,
                            email: e.target.value,
                          })
                        }
                        className="pl-10 h-11 transition-all duration-200 focus:ring-2 focus:ring-blue-500/20 bg-white dark:bg-slate-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
                        required
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label
                      htmlFor="register-password"
                      className="text-sm font-bold text-slate-800 dark:text-white"
                    >
                      Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 w-4 h-4" />
                      <Input
                        id="register-password"
                        type="password"
                        placeholder="Create a password"
                        value={registerData.password}
                        onChange={(e) =>
                          setRegisterData({
                            ...registerData,
                            password: e.target.value,
                          })
                        }
                        className="pl-10 h-11 transition-all duration-200 focus:ring-2 focus:ring-blue-500/20 bg-white dark:bg-slate-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
                        required
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <Button
                    type="submit"
                    className="w-full h-11 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating account...
                      </>
                    ) : (
                      "Create Account"
                    )}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>

            {error && (
              <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400 text-center">
                  {error}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
            Powered by AI • Secured by design
          </p>
        </div>
      </div>
    </div>
  );
};

export default Auth;
