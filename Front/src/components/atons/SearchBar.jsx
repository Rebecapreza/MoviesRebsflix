import React from "react";
import { FaSearch } from "react-icons/fa";
import "./SearchBar.css";

const SearchBar = () => {
  return (
    <div className="search-container">
      <FaSearch className="search-icon" />
      <input type="text" placeholder="Qual filme deseja?" className="search-input" />
      <button className="search-button">Search</button>
    </div>
  );
};

export default SearchBar;
