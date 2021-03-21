import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const MenuBar = (props) => {
    const [currentrole, setCurrentRole] = useState({});
    useEffect(() => {
        if (props.currentgroup != '') {
            let params = { id: props.currentgroup };
            fetch('/api/currentrole', {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': props.client.transports[0].auth.csrfToken
                },
                credentials: 'same-origin',
                body: JSON.stringify(params)
            }).then(res => { return res.json() })
                .then(res => {
                    setCurrentRole(res.currentrole);
                })

        }
    }, [props.currentgroup])

    return (
        <div className="container semisection">
            <div className="navbar-menu" id="nav-menu">
                <div className="navbar-start">
                    <Link to="/grouplist/" className="navbar-item">Intel Group List</Link>
                    {(!props.addgroup && (currentrole.role == 1 || currentrole.role == 2)) &&
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="is-show-desktop">View intel</span>
                            </a>
                            <div className="navbar-dropdown is-left">
                                <Link to={`/intel_group/${currentrole.intelgroup_id}/feedlist/`} className="navbar-item">Feed List</Link>
                                <Link to={`/intel_group/${currentrole.intelgroup_id}/intelreports/`} className="navbar-item">Intel Reports</Link>
                            </div>
                        </div>
                    }
                </div>
                {(!props.addgroup && currentrole.role == 2) &&
                    <div className="navbar-end">
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="is-show-desktop">Manage Feeds</span>
                            </a>
                            <div className="navbar-dropdown is-left">
                                <Link to="/feeds/" className="navbar-item">Feed Store</Link>
                                <Link to={`/intel_group/${currentrole.intelgroup_id}/configuredfeeds/`} className="navbar-item">Configured Feeds</Link>
                            </div>
                        </div>
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="is-show-desktop">Manage Group</span>
                            </a>
                            <div className="navbar-dropdown is-left">
                                <Link to={`/intel_group/${currentrole.intelgroup_id}/edit`} className="navbar-item">Edit Group</Link>
                                <Link to={`/intel_group/${currentrole.intelgroup_id}/users`} className="navbar-item">Manage Users</Link>
                            </div>
                        </div>
                        <div className="navbar-item has-dropdown is-hoverable">
                            <a className="navbar-link">
                                <span className="is-show-desktop">Manage Extractions</span>
                            </a>
                            <div className="navbar-dropdown is-left">
                                <Link to={`/intel_group/${currentrole.intelgroup_id}/extractions/`} className="navbar-item">Observables</Link>
                                <Link to={`/intel_group/${currentrole.intelgroup_id}/whitelist/`} className="navbar-item">Whitelist</Link>
                            </div>
                        </div>
                        <a href={`/subscriptions/intelgroup/${currentrole.intelgroup_id}`} className="navbar-item">Plan</a>
                    </div>
                }
            </div>
        </div>
    );
}

export default MenuBar;