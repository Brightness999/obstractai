import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Alert, AlertTitle } from "@material-ui/lab";

const MenuBar = (props) => {
    const [currentgroup, setCurrentGroup] = useState(props.currentgroup);
    const [currentrole, setCurrentRole] = useState({});
    useEffect(()=>{
        setCurrentGroup(props.currentgroup);
        if(!props.userinfo.is_staff){
            let params = {id:props.currentgroup};
            if(props.currentgroup != '')
                fetch('/api/currentrole', {
                    method: 'post',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': props.client.transports[0].auth.csrfToken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(params)
                }).then(res=>{return res.json()})
                .then(res=>setCurrentRole(res.currentrole));
        }
    },[props.currentgroup])
    if(!props.userinfo.is_staff)
        return (
            <div className="container">
                {currentgroup != '' &&
                <div className="navbar-menu" id="nav-menu">
                    {currentrole.role != 0 &&
                    <div className="navbar-start">
                        <a className="navbar-item is-size-5 has-text-weight-bold">Member actions:</a>
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="is-show-desktop">View intel</span>
                            </a>
                            <div className="navbar-dropdown is-left">
                                <Link to="/intelgroups/" className="navbar-item">Intel Groups</Link>
                                <Link to="/intelreports/" className="navbar-item">Intel Reports</Link>
                            </div>
                        </div>
                    </div>
                    }
                    {currentrole.role == 2 &&
                    <div className="navbar-end">
                        <a className="navbar-item is-size-5 has-text-weight-bold">Admin actions:</a>
                        <Link to="/feeds/" className="navbar-item">Manage feeds</Link>
                        <Link to="/categories/" className="navbar-item">Categories</Link>
                        <Link to="/extractions/" className="navbar-item">Extractions</Link>
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="is-show-desktop">Indicator</span>
                            </a>
                            <div className="navbar-dropdown is-left">
                                {/* <Link to="/globalindicators/" className="navbar-item">Global Indicators</Link> */}
                                {/* <Link to="/indicators/" className="navbar-item">Indicators</Link> */}
                                <Link to="/whitelist/" className="navbar-item">Whitelist</Link>
                            </div>
                        </div>
                        <a href={`/subscriptions/intelgroup/${currentgroup}`} className="navbar-item">Plan</a>
                    </div>
                    }
                </div>}
                {/* <Alert severity="info" className="my-5">
					<AlertTitle className="subtitle is-4 has-text-weight-bold">Info</AlertTitle>
					<span className="subtitle is-5">Your plan will be downgraded and limited on, to keep all existing features, you must select a plan before this date.</span>
				</Alert> */}
            </div>
        );
    else
        return (
            <div className="container">
                <div className="navbar-menu" id="nav-menu">
                    <div className="navbar-start">
                        <Link to="/feeds/" className="navbar-item">Manage feeds</Link>
                        {/* <Link to="/categories/" className="navbar-item">Categories</Link> */}
                        <Link to="/globalattributes/" className="navbar-item">Extractions</Link>
                        <Link to="/globalindicators/" className="navbar-item">Indicators</Link>
                        {/* <a href={`/subscriptions/intelgroup/${currentgroup}`} className="navbar-item">Plan</a> */}
                    </div>
                </div>
            </div>
        );
}

export default MenuBar;