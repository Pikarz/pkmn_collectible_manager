import React, { useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import ExpansionList from './components/ExpansionList';
import Collection from './components/Collection';
import AddCard from './components/AddCard';
import SellingCards from './components/SellingCards';
import CardInsertionForm from './components/CardInsertionForm';
import SellingSummary from './components/SellingSummary';
import SoldCards from './components/SoldCards';
import LastSold from './components/LastSold';
import { DarkModeProvider, useDarkMode } from './DarkModeContext';
import { useLocation } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  const { darkMode, toggleDarkMode } = useDarkMode();

  const handleDarkModeToggle = () => {
    toggleDarkMode();
  };

  return (
      <Router>
        <Sidebar />
        <div className="content">
          <div className="header">
            <h1>PokéCards</h1>
          </div>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/my-collection" element={<Collection/>} />
            <Route path="/selecting-cards" element={<AddCard />} />
            { /*<Route path="/selecting-cards/inserting" element={<InsertCards />} />*/}
            <Route path="/expansions" element={<ExpansionList />} />
            {/* Add more routes for other functionalities */}
            <Route path="/selecting-cards/inserting" element={<CardInsertionForm />} />
            <Route path="/insert-selling-cards" element={<SellingCards />} />
            <Route path="/insert-selling-cards/selling-summary" element={<SellingSummary />} />
            <Route path="/isold" element={<SoldCards />} />
            <Route path="/isold/sold-summary" element={<SellingSummary />} />
            <Route path="/last-sold" element={<LastSold />} />
          </Routes>
        </div>
      </Router>
  );
}

function Home() {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const showSuccessToast = queryParams.get('showSuccessToast')
  const message = queryParams.get('message')
  // Display the toast in the Home component

  useEffect(() => {
    if (showSuccessToast) {
      toast.success(message);
    }
  }, [showSuccessToast]);


  return (
    <div>
        <h2>Welcome to PokéCards</h2>
        <ToastContainer autoClose={3000} position="bottom-center" />
    </div>
  );
}

export default App;
