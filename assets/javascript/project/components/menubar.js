import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

const MenuBar = (props) => {
    const [currentgroup, setCurrentGroup] = useState(props.currentgroup);

    useEffect(()=>{
        setCurrentGroup(props.currentgroup);
    },[props.currentgroup])

    return (
        // <div className="navbar" role="navigation" aria-label="main navigation">
            <div className="container">
                <div className="navbar-menu" id="nav-menu">
                    <div className="navbar-start">
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="is-show-desktop">Intel</span>
                            </a>
                            <div className="navbar-dropdown is-left">
                                <Link to="/intelgroups/" className="navbar-item">Intel Groups</Link>
                                <Link to="/intelreports/" className="navbar-item">Intel Reports</Link>
                            </div>
                        </div>
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="is-show-desktop">Feeds</span>
                            </a>
                            <div className="navbar-dropdown is-left">
                                <Link to="/feeds/" className="navbar-item">Custom</Link>
                                {/* <Link to="/feeds/" className="navbar-item">Configure</Link> */}
                            </div>
                        </div>
                        <Link to="/categories/" className="navbar-item">Categories</Link>
                        <Link to="/extractions/" className="navbar-item">Extractions</Link>
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="is-show-desktop">Indicator</span>
                            </a>
                            <div className="navbar-dropdown is-left">
                                <Link to="/indicators/" className="navbar-item">Indicators</Link>
                                <Link to="/whitelist/" className="navbar-item">Whitelist</Link>
                            </div>
                        </div>
                        {currentgroup!=''&& <a href={`/subscriptions/intelgroup/${currentgroup}`} className="navbar-item">Plan</a>}
                    </div>
                </div>
            </div>
        // </div>
    );
}

export default MenuBar;