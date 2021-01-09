import React, { useState, useEffect } from 'react';
import { BrowserRouter, Route ,Switch } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from "./store";
import { getAction } from "../../api";
import { API_ROOT } from "../const";
import HomePage from '../Home';
import TopNavbar from '../components/topnavbar';
import MenuBar from '../components/menubar';
import IntelGroup from '../intelgroups';
import Feeds from '../feeds';
import Categories from '../categories';
import Extractions from '../extractions';
import IntelReports from '../intelreports';
import GlobalIndicators from '../indicators';
import WhiteLists from '../whitelist';
import Plan from '../plans';
import CurrentPlan from '../plans/current-plan';
import { useScrollTrigger } from '@material-ui/core';
import GetFullText from '../cyobstract/getfulltext';
import Account from '../profile';


const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const App = () => {
  let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
	const client = new coreapi.Client({auth: auth});
	const [isLoading, setIsLoading] = useState(true);
  const [mygroups, setMyGroups] = useState([]);
  const [users, setUsers] = useState([]);
	const [currentgroup, setCurrentGroup] = useState('');
  const intelgroup_action = getAction(API_ROOT, ['intelgroups', 'list']);
  const customer_action = getAction(API_ROOT, ['customers', 'list']);
	useEffect(() => {
		client.action(window.schema, intelgroup_action).then((result) => {
			setMyGroups(result.results);
			client.action(window.schema, customer_action).then((result) => {
				setUsers(result.results);
				setIsLoading(false);
			});
		});
  },[]);
  
  const currentIntelgroup = (intelgroup) => {
    setCurrentGroup(intelgroup);
  }
  const intelgroupSave = (intelgroup) => {
    let flag = false;
    const newIntelgroup = [];
		for (let group of mygroups) {
			if (group.id === intelgroup.id) {
				newIntelgroup.push(intelgroup);
				flag = true;
			} else {
				newIntelgroup.push(group);
			}
		}
		if (!flag) {
			newIntelgroup.push(intelgroup);
		}
		setMyGroups(newIntelgroup);
  }
  const deleteIntelGroup = (intelgroups) => {
    setMyGroups(intelgroups);
  }

  if(isLoading)
    return <Loading/>
  else
    return (
      <Provider store={store}>
        <BrowserRouter basename='/home/'>
          <TopNavbar mygroups={mygroups} client={client} currentIntelgroup={(intelgroup)=>currentIntelgroup(intelgroup)} />
          <MenuBar currentgroup={currentgroup} client={client} />
          <Switch>
            <Route exact path="/">
              <HomePage mygroups={mygroups} client={client} users={users} intelgroupSave={(data)=>intelgroupSave(data)} />
            </Route>
            <Route path="/intelgroups" >
              <IntelGroup client={client} intelgroupSave={(data)=>intelgroupSave(data)} deleteIntelGroup={(data)=>deleteIntelGroup(data)}/>
            </Route>
            <Route path="/feeds">
              <Feeds currentgroup={currentgroup} client={client}/>
            </Route>
            <Route path="/categories" >
              <Categories client={client} />
            </Route>
            <Route path="/extractions">
              <Extractions client={client} currentgroup={currentgroup} />
            </Route>
            <Route path="/intelreports" >
              <IntelReports client={client} />
            </Route>
            <Route path="/globalindicators" >
              <GlobalIndicators client={client} />
            </Route>
            <Route path="/whitelist" >
              <WhiteLists client={client} currentgroup={currentgroup} />
            </Route>
            {/* <Route path="/plans" component={Plan} /> */}
            {/* <Route path="/manageplan" component={CurrentPlan} /> */}
            {/* <Route path="/getfulltext" component={GetFullText} /> */}
            <Route path="/account" >
              <Account client={client} deleteIntelGroup={(intelgroups)=>deleteIntelGroup(intelgroups)} />
            </Route>
          </Switch>
        </BrowserRouter>
      </Provider>
    );
}

export default App;