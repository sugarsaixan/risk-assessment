import { Routes, Route } from "react-router-dom";

/**
 * Main application component with route configuration.
 * Routes will be added as pages are implemented.
 */
function App() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Routes>
        {/* Public assessment routes will be added here */}
        <Route path="/" element={<Home />} />
        {/* Placeholder routes - to be implemented */}
        {/* <Route path="/a/:token" element={<AssessmentForm />} /> */}
        {/* <Route path="/a/:token/results" element={<Results />} /> */}
        {/* <Route path="/expired" element={<ExpiredLink />} /> */}
        {/* <Route path="/used" element={<UsedLink />} /> */}
        {/* <Route path="*" element={<NotFound />} /> */}
      </Routes>
    </div>
  );
}

/**
 * Temporary home component - will be removed when routes are implemented.
 */
function Home() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Эрсдэлийн үнэлгээний систем</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Risk Assessment Survey System
        </p>
      </div>
    </div>
  );
}

export default App;
