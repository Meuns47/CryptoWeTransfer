import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./HomePage";
import DownloadsPage from "./DownloadsPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/download/:id" element={<DownloadsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
