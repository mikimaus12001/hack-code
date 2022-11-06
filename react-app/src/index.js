import React from 'react';
//import ReactDOM from 'react-dom';
import * as ReactDOMClient from 'react-dom/client';
import App from './App';

//const root = ReactDOM.createRoot(document.getElementById('root'));
const root = ReactDOMClient.createRoot(document.getElementById('root'));
root.render(
  <App />
);
