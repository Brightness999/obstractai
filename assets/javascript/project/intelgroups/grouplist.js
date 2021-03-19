import React, { useState, useEffect } from 'react';
import { Link, useHistory } from "react-router-dom";
import { Container, Dialog } from "@material-ui/core";
import { Table, Thead, Tbody, Tr, Th, Td } from 'react-super-responsive-table';
import { Alert, AlertTitle } from '@material-ui/lab';

const Loading = function () {
    return (
        <div className='app-card has-text-centered'>
            <div className="lds-ripple"><div></div><div></div></div>
            <p className="heading has-text-primary">Loading...</p>
        </div>
    )
}

const GroupList = (props) => {
    console.log(props);
    const [isLoading, setIsLoading] = useState(true);
    const [groups, setGroups] = useState([]);
    const [request, setRequest] = useState(false);
    const history = useHistory();

    useEffect(() => {
        if (!Boolean(localStorage.getItem('groupid'))) {
            localStorage.setItem('groupid', props.currentgroup);
            if (props.currentgroup == '') {
                localStorage.setItem('groupid', 1);
            }
            fetch('/api/grouplist', {
                method: 'get',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
            }).then(res => { return res.json() })
                .then(res => {
                    setGroups(res);
                    setIsLoading(false);
                });
        }
        else {
            localStorage.removeItem('groupid');
            history.push('/intelreports');
        }
    }, [props.currentgroup]);

    const requestinvite = (index) => {
        let params = { id: groups[index].id }
        fetch('/api/grouplist', {
            method: 'post',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify(params)
        }).then(res => { return res.json() })
            .then(res => {
                setGroups(res);
                setRequest(true);
                setIsLoading(false);
            });
    }

    if (isLoading) {
        return <Loading />
    }
    else {
        return (
            <Container>
                <Dialog
                    maxWidth="md"
                    fullWidth
                    open={request}
                    onClose={() => setRequest(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <Alert severity="success" className="my-5">
                        <AlertTitle className="subtitle is-4 has-text-weight-bold">Info</AlertTitle>
                        <span className="subtitle is-5">Your request has been sent.</span>
                    </Alert>
                </Dialog>

                <section className="section app-card">
                    <div className="section">
                        <label className="title is-3">Intel Group List</label>
                        <Link to={'/account'}>
                            <button className="button is-info mx-4" >
                                <span>Manage</span>
                            </button>
                        </Link>
                        <button className="button is-outlined is-pulled-right mx-4" onClick={() => history.goBack()}>
                            <span>Back</span>
                        </button>
                    </div>
                    <Table className="table is-striped is-fullwidth has-vcentered-cells">
                        <Thead>
                            <Tr>
                                <Th>Name</Th>
                                <Th>Description</Th>
                                <Th>Action</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {
                                props.mygroups.map((group, index) => {
                                    return <Tr index={index} key={group.id}>
                                        <Td>{group.intelgroup.name}</Td>
                                        <Td>{group.intelgroup.description}</Td>
                                        <Td>
                                            <div className="button is-static">
                                                <span>{group.role == 2 ? "Admin" : "Member"}</span>
                                            </div>
                                        </Td>
                                    </Tr>
                                })
                            }
                            {
                                groups.map((group, index) => {
                                    return <Tr index={index} key={group.id}>
                                        <Td>{group.name}</Td>
                                        <Td>{group.description}</Td>
                                        <Td>
                                            <div className="button is-success">
                                                <a className="a has-text-white" onClick={() => requestinvite(index)}>
                                                    <span>Invite Request</span>
                                                </a>
                                            </div>
                                        </Td>
                                    </Tr>
                                })
                            }
                        </Tbody>
                    </Table>
                </section>
            </Container>
        );
    }
};
export default GroupList;