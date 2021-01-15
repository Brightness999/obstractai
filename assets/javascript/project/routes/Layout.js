import React from 'react';
import { Link } from "react-router-dom";
import { Grid, Paper} from "@material-ui/core";

function Layout(props) {
  if(props.mygroups.length == 0)
    return (
      <div className="py-6 my-6">
        <Grid container spacing={6} direction="row" justify="center" alignItems="center">
          <Grid item xs={4} className="my-6">
            <Paper elevation={5}>
              <Link className="section button is-fullwidth" to="/pending">
                <h1 className="title is-3">I want to be a staff.</h1>
              </Link>
            </Paper>
          </Grid>
          <Grid item xs={4} className="my-6">
            <Paper elevation={5} >
              <Link className="section button is-fullwidth" to="/customer">
                <h1 className="title is-3">I want to be a customer.</h1>
              </Link>
            </Paper>
          </Grid>
        </Grid>
      </div>
    );
  else{
    return (
      <div className="my-6">
        <h1 className="title is-size-2 has-text-centered py-6">Welcome to Cyobstract</h1>
        {props.mygroups.map(mygroup=>{
          if(mygroup.role == 0)
            return <div className="section app-card has-text-centered" key={mygroup.id}>
              <p className="subtitle is-4">! You have an invitation to <span className="title is-3 has-text-primary">{mygroup.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-4 has-text-danger" to="/intelgroups" >Click here to accept.</Link></p>
            </div> 
        })}
      </div>
    );
  }
}

export default Layout;
