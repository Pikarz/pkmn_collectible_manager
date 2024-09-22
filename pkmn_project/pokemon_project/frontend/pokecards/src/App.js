import React, { useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import './App.css'; 
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CardInsertionForm from './components/ManageCards/Inserting/CardInsertionForm';
import Trade from './components/ManageCards/Trading/Trade';
import Transactions from './components/Transactions/Transactions';
import HomeButtons from './components/Navigation/HomeButtons';
import Stats from './components/Stats/Stats';
import { useLocation } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ManageCards from './components/ManageCards/ManageCards';
import PendingCards from './components/ManageCards/PendingCards';
import CardListing from './components/ManageCards/Sell/CardListing';
import CardSelling from './components/ManageCards/Sell/CardSelling';
import Header from './components/Navigation/header';
import Footer from './components/Navigation/Footer';

function App() {
  const theme = createTheme({
    typography: {
      fontFamily: 'Roboto, sans-serif',
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
        <Router>
          <Header />
          <div className={"content"}>
            <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/my-collection"
            element={<ManageCards isCollection={true} />}
          />
          <Route
            path="/selecting-cards"
            element={<ManageCards isCollection={false} />}
          />
          <Route
            path="/selecting-cards/inserting"
            element={<CardInsertionForm />}
          />
          <Route path="/insert-selling-cards" element={<CardListing />} />
          <Route path="/isold" element={<CardSelling />} />
          <Route path="/new-trade" element={<Trade />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/stats" element={<Stats />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  </ThemeProvider>
  );
}

function Home() {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const showSuccessToast = queryParams.get('showSuccessToast');
  const message = queryParams.get('message');

  useEffect(() => {
    if (showSuccessToast) {
      toast.success(message);
    }
  }, );

  return (
    <div>
      <h2>Welcome to CardMaster!</h2>
      <p>Your ultimate tool for managing Pokemon TCG cards.</p>
      <ToastContainer autoClose={3000} position="bottom-center" />
      <PendingCards />
      <HomeButtons />
    </div>
  );
}

export default App;
