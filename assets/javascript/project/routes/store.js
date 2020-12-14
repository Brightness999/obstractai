import {createStore} from "redux";
import state from "./state";
import reducers from "./reducers";

const store = createStore(reducers,state);

export default store;
