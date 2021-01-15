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
import GlobalAttributes from '../globalattributes';
import Layout from './Layout';
import Pending from '../staff/pending';


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
  const [intelgroups, setIntelGroups] = useState([]);
  const [users, setUsers] = useState([]);
  const [currentgroup, setCurrentGroup] = useState('');
  const [userinfo, setUserInfo] = useState({});
	useEffect(() => {
    fetch('/api/home', {
      method: 'get',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    }).then((res)=>{return res.json()})
    .then(res=>{
      console.log(res);
      setMyGroups(res.mygroups);
      setIntelGroups(res.intelgroups);
      setUsers(res.users);
      setUserInfo(res.userinfo);
      setIsLoading(false);
    })
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
          {!userinfo.is_staff &&
          <>
          <TopNavbar mygroups={mygroups} client={client} currentIntelgroup={(intelgroup)=>currentIntelgroup(intelgroup)} userinfo={userinfo} />
          <MenuBar currentgroup={currentgroup} client={client} userinfo={userinfo} />
          <Switch>
            <Route exact path="/">
              <Layout mygroups={mygroups} />
            </Route>
            <Route path="/customer">
              <HomePage mygroups={mygroups} client={client} users={users} intelgroupSave={(data)=>intelgroupSave(data)} />
            </Route>
            <Route path="/intelgroups" >
              <IntelGroup client={client} intelgroupSave={(data)=>intelgroupSave(data)} deleteIntelGroup={(data)=>deleteIntelGroup(data)}/>
            </Route>
            <Route path="/feeds">
              <Feeds currentgroup={currentgroup} client={client}/>
            </Route>
            <Route path="/categories" >
              <Categories client={client} currentgroup={currentgroup} />
            </Route>
            <Route path="/extractions">
              <Extractions client={client} currentgroup={currentgroup} />
            </Route>
            <Route path="/intelreports" >
              <IntelReports client={client} currentgroup={currentgroup} mygroups={mygroups} />
            </Route>
            <Route path="/globalindicators" >
              <GlobalIndicators client={client} currentgroup={currentgroup}/>
            </Route>
            <Route path="/whitelist" >
              <WhiteLists client={client} currentgroup={currentgroup} />
            </Route>
            <Route path="/globalattributes" >
              <GlobalAttributes client={client} currentgroup={currentgroup} />
            </Route>
            {/* <Route path="/plans" component={Plan} /> */}
            {/* <Route path="/manageplan" component={CurrentPlan} /> */}
            {/* <Route path="/getfulltext" component={GetFullText} /> */}
            <Route path="/account" >
              <Account client={client} deleteIntelGroup={(intelgroups)=>deleteIntelGroup(intelgroups)} />
            </Route>
            <Route path="/pending">
              <Pending />
            </Route>
          </Switch></>}
          {userinfo.is_staff && 
          <>
          <TopNavbar mygroups={intelgroups} client={client} currentIntelgroup={(intelgroup)=>currentIntelgroup(intelgroup)} userinfo={userinfo} />
          <MenuBar currentgroup={currentgroup} client={client} userinfo={userinfo} />
          
          </>
          }
        </BrowserRouter>
      </Provider>
    );
}

export default App;