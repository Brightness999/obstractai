import React from 'react';
import { BrowserRouter, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import Layout from './Layout';
import store from "./store";

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter basename="/">
        <Route component={Layout} />
      </BrowserRouter>
    </Provider>
  );
}

export default App;