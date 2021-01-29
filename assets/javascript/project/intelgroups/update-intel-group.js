import React, {useState} from "react";
import { Link, useHistory } from "react-router-dom";
import ReactTags from 'react-tag-autocomplete';
import { Tooltip, TextField, Grid } from "@material-ui/core";
import HelpIcon from '@material-ui/icons/Help';
import { yellow } from '@material-ui/core/colors';

const UpdateIntelGroup = function(props) {
  console.log(props);
  const [id, setId] = useState(props.intelgroup_id || null);
  const [name, setName] = useState(props.intelgroup? props.intelgroup.name: '');
  const [description, setDescription] = useState(props.intelgroup? props.intelgroup.description : '');
  const [tags, setTags] = useState([]);
  const editMode = Boolean(id);
  const history = useHistory();  
  const userOptions = props.users.map((user)=>({
    id: user.id,
    name: user.email
  }));

  const reacttag= React.createRef();
  const onDelete= (i)=> {
      var temp = tags.slice(0)
      temp.splice(i, 1)
      setTags(temp)
    }
  
  const onAddition = (tag)=> {
    let mailformat = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
    if(tag.name.match(mailformat)){
      var temp = [].concat(tags, tag)
      setTags(temp)
    }
  }

  const saveIntelgroup = function() {
    const userids = [];
    const emails = [];
    tags.forEach(tag => {
      if(Boolean(tag.id)) {
        userids.push(tag.id)
      }
      else {
        emails.push(tag.name)
      }
    });
    let params = {
      name: name,
      description: description,
      userids: userids,
      emails: emails
    };
    if(name != '' && description != '' && (userids != []) || emails != []){
      if (editMode) {
        params['id'] = id;
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
          props.intelgroupSaved(res);
          history.goBack();
        })
      } else {
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
          props.intelgroupSaved(res);
          history.goBack();
        })
      }
    }
  };

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
      {!editMode &&
        <div style={{zIndex:1}}>
          <label className="label mb-5">Invite Users</label>
          <Grid container>
            <Grid item xs={9}>
              <ReactTags
                ref={reacttag}
                tags={tags}
                suggestions={userOptions}
                onDelete={onDelete}
                onAddition={onAddition}
                allowNew={true}
              />
            </Grid>
            <Grid item xs={3}>
              <Tooltip title="Users you want to invite" arrow><HelpIcon className="mt-2" style={{color:yellow[900]}} fontSize="large"/></Tooltip>
            </Grid>
          </Grid>
        </div>
      }
      </div>
      <div className="field is-grouped">
        <div className="control">
          <button type='button' className={`button is-primary ${editMode ? 'is-outlined' : ''}`}
                  onClick={() => saveIntelgroup()} >
            <span>{editMode ? 'Save intel group' : 'Create intel group'}</span>
          </button>
        </div>
        <div className="control">
            <button className="button is-text" onClick={()=>{history.goBack()}}>
              <span>Cancel</span>
            </button>
        </div>
      </div>
    </section>
  );
};

export default UpdateIntelGroup;
