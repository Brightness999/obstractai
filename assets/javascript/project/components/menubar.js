import React from "react";
import { Link } from "react-router-dom";

const MenuBar = (props) => {
    console.log(props);
    return (
        <div className="container semisection">
            {/* {props.currentgroup != '' && */}
            <div className="navbar-menu" id="nav-menu">
                <div className="navbar-start">
                    <Link to="/grouplist/" className="navbar-item">Intel Group List</Link>
                {(props.currentrole.role == 1 || props.currentrole.role == 2)&&
                    <div className="navbar-item has-dropdown is-hoverable">
                        <a className="navbar-link">
                            <span className="is-show-desktop">View intel</span>
                        </a>
                        <div className="navbar-dropdown is-left">
                            <Link to="/feedlist/" className="navbar-item">Feed List</Link>
                            <Link to="/intelreports/" className="navbar-item">Intel Reports</Link>
                        </div>
                    </div>
                }
                </div>
                {props.currentrole.role == 2 &&
                <div className="navbar-end">
                    <div className="navbar-item has-dropdown is-hoverable">
                        <a className="navbar-link">
                            <span className="is-show-desktop">Manage Feeds</span>
                        </a>
                        <div className="navbar-dropdown is-left">
                            <Link to="/feeds/" className="navbar-item">Feed Store</Link>
                            <Link to="/configuredfeeds/" className="navbar-item">Configured Feeds</Link>
                        </div>
                    </div>
                    <div className="navbar-item has-dropdown is-hoverable">
                        <a className="navbar-link">
                            <span className="is-show-desktop">Manage Group</span>
                        </a>
                        <div className="navbar-dropdown is-left">
                            <Link to="/intelgroup" className="navbar-item">Edit Group</Link>
                            <Link to="/users" className="navbar-item">Manage Users</Link>
                        </div>
                    </div>
                    <div className="navbar-item has-dropdown is-hoverable">
                        <a className="navbar-link">
                            <span className="is-show-desktop">Manage Extractions</span>
                        </a>
                        <div className="navbar-dropdown is-left">
                            {/* <Link to="/categories/" className="navbar-item">Categories</Link> */}
                            <Link to="/extractions/" className="navbar-item">Attributes</Link>
                            <Link to="/whitelist/" className="navbar-item">Whitelist</Link>
                        </div>
                    </div>
                    <a href={`/subscriptions/intelgroup/${props.currentgroup}`} className="navbar-item">Plan</a>
                </div>
                }
            </div>
            {/* } */}
        </div>
    );
}

export default MenuBar;