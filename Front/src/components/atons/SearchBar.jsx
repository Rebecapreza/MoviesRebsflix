import React, { useState } from "react";
import { FaSearch } from "react-icons/fa";
import "./SearchBar.css";

const SearchBar = ({ onSearch }) => { // Recebe a função onSearch da Home
  const [term, setTerm] = useState("");

  const handleSearch = () => {
    if (onSearch) {
      onSearch(term); // Envia o termo para o componente pai (Home)
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="search-container">
      <FaSearch className="search-icon" />
      <input 
        type="text" 
        placeholder="Qual filme deseja?" 
        className="search-input" 
        value={term}
        onChange={(e) => setTerm(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button className="search-button" onClick={handleSearch}>Search</button>
    </div>
  );
};

export default SearchBar;