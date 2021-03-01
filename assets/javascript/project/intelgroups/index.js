import React, {useState, useEffect} from "react";
import { useHistory } from "react-router-dom";
import ReactTags from 'react-tag-autocomplete';
import { Tooltip, TextField, Grid, Container } from "@material-ui/core";
import HelpIcon from '@material-ui/icons/Help';
import { yellow } from '@material-ui/core/colors';

const IntelGroups = function(props) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState([]);
  const history = useHistory();  
  
  const reacttag= React.createRef();
  const onDelete= (i)=> {
      var temp = tags.slice(0)
      temp.splice(i, 1)
      setTags(temp)
    }
  
  const onAddition = (tag)=> {
    let mailformat = /^([A-Za-z0-9_\-\.\+])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
    if(tag.name.match(mailformat)){
      var temp = [].concat(tags, tag)
      setTags(temp)
    }
  }

  const saveIntelgroup = function() {
    const emails = [];
    tags.forEach(tag => {
      emails.push(tag.name);
    });
    let params = {
      name: name,
      description: description,
      emails: emails
    };
    if(name != '' && description != '' && emails.length > 0){
      fetch('/api/intelgroups', {
        method: 'post',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': props.client.transports[0].auth.csrfToken
        },
        credentials: 'same-origin',
        body: JSON.stringify(params)
      }).then(res=>{return res.json()})
      .then(res=>{
        props.intelgroupSave(res)
        history.goBack();
      })
    }
  };

  if(props.currentrole.role ==0){
      return (
          <div className='app-card has-text-centered'>
              <div className="lds-ripple"><div></div><div></div></div>
              <p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3" to="/account" >Click here to accept.</Link></p>
          </div>
      )
  }
  if(props.currentrole.role == 4){
      return(
          <div className='section has-text-centered'>
              <p className="subtitle is-3">Your request for <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span> Intel Group has not been accepted yet.</p>
          </div>
      )
  }
  else {
    return (
      <Container>
      <section className="section app-card">
        <h2 className="subtitle">Create New Intel Group</h2>
        <div className="field column is-two-thirds">
          <label className="label">Name</label>
          <TextField
            placeholder="Name of intel group"
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
            placeholder="Description of intel group"
            className="column is-three-quarters"
            margin="normal"
            InputLabelProps={{
              shrink: true,
            }}
            variant="outlined"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          /><Tooltip title="Description to be displayed in UI" arrow><HelpIcon className="mt-5" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
          <div style={{zIndex:1}}>
            <label className="label mb-5">Invite Users</label>
            <Grid container>
              <Grid item xs={9}>
                <ReactTags
                  ref={reacttag}
                  tags={tags}
                  onDelete={onDelete}
                  placeholderText="Comma separated list of emails for users to invite"
                  onAddition={onAddition}
                  addOnBlur={true}
                  allowNew={true}
                  delimiters={['Enter', 'Tab', ',', ' ']}
                />
              </Grid>
              <Grid item xs={3}>
                <Tooltip title="Users you want to invite" arrow><HelpIcon className="mt-2" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
              </Grid>
            </Grid>
          </div>
        </div>
        <div className="field is-grouped">
          <div className="control">
            <button type='button' className="button is-primary" onClick={() => saveIntelgroup()} >
              <span>Create intel group</span>
            </button>
          </div>
          <div className="control">
              <button className="button is-text" onClick={()=>{history.goBack()}}>
                <span>Cancel</span>
              </button>
          </div>
        </div>
      </section>
      </Container>
    );
  }
};

export default IntelGroups;
