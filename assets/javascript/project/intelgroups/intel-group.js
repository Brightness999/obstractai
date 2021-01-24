import React, {useState, useEffect} from "react";
import { Link, useHistory } from "react-router-dom";
import { Tooltip, TextField, Dialog, DialogTitle, DialogContent, DialogContentText } from "@material-ui/core";
import HelpIcon from '@material-ui/icons/Help';
import { yellow } from '@material-ui/core/colors';

const Loading = function() {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	)
}

const IntelGroup = function(props) {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [currentrole, setCurrentRole] = useState({});
    const [open, setOpen] = useState(false);
    const history = useHistory();  
  
    useEffect(()=>{
        if(props.currentgroup == '') history.push('/');
        else{
            let params = {id:props.currentgroup};
            fetch('/api/intelgroups',{
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': props.client.transports[0].auth.csrfToken
                },
                credentials: 'same-origin',
                body: JSON.stringify(params)
            }).then(res=>{return res.json()})
            .then(res=>{
                setName(res.name);
                setDescription(res.description);
                setCurrentRole(res.currentrole);
                setIsLoading(false);
            })

        }
    },[props.currentgroup]);

    const saveIntelgroup = function() {
        let params = {
            name: name.trim(),
            description: description.trim(),
            userids: [],
            emails: []
        };
        if(name.trim() != '' && description.trim() != ''){
            params['id'] = props.currentgroup;
            fetch('/api/intelgroups', {
            method: 'put',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken
            },
            credentials: 'same-origin',
            body:JSON.stringify(params)
            }).then(res=>{return res.json()})
            .then(res=>{
                if(Boolean(res.id)){
                    setOpen(true);
                }
            })
        }
    };
    if(isLoading){
        return <Loading/>
    }
    else{
        if(currentrole.role ==0)
            return (
                <div className='app-card has-text-centered'>
                    <div className="lds-ripple"><div></div><div></div></div>
                    <p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{currentrole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3" to="/intelgroups" >Click here to accept.</Link></p>
                </div>
            )
        if(currentrole.role == 1)
            return(
                <div className='section has-text-centered'>
                    <p className="subtitle is-3">! You are now a member of <span className="title is-3 has-text-primary">{currentrole.intelgroup.name}</span>.</p>
                </div>
            )
        if(currentrole.role == 2)
            return (
                <section className="section app-card">
                    <h2 className="subtitle">Intel Group Details</h2>
                    <div className="field column is-two-thirds">
                        <label className="label">Name</label>
                        <TextField
                        placeholder="write a name of feed"
                        className="column is-three-quarters"
                        margin="normal"
                        InputLabelProps={{
                            shrink: true,
                        }}
                        variant="outlined"
                        value={name}
                        onChange={(event) => setName(event.target.value)}
                        /><Tooltip title="Name to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
                    
                        <label className="label">Description</label>
                        <TextField
                        placeholder="write about description of feed"
                        className="column is-three-quarters"
                        margin="normal"
                        InputLabelProps={{
                            shrink: true,
                        }}
                        variant="outlined"
                        value={description}
                        onChange={(event) => setDescription(event.target.value)}
                        /><Tooltip title="Description to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
                    </div>
                    <div className="field is-grouped">
                        <div className="control">
                        <button type='button' className="button is-primary is-outlined" onClick={() => saveIntelgroup()} >
                            <span>Save intel group</span>
                        </button>
                        </div>
                        <div className="control">
                            <button className="button is-text" onClick={()=>{history.goBack()}}>
                            <span>Cancel</span>
                            </button>
                        </div>
                    </div>
                    <div>
                        <Dialog
                            maxWidth="md"
                            fullWidth
                            open={open}
                            onClose={()=>setOpen(false)}
                            aria-labelledby="alert-dialog-title"
                            aria-describedby="alert-dialog-description"
                        >
                            <DialogTitle id="alert-dialog-title">{"Information"}</DialogTitle>
                            <DialogContent >
                            <DialogContentText id="alert-dialog-description">
                                Your intel group is successfully changed!!!
                            </DialogContentText>
                            </DialogContent>
                        </Dialog>
                    </div>
                </section>
                
            );
    }
};

export default IntelGroup;
