import React from "react";
import {Link} from "react-router-dom";
import {
  Grid
} from "@material-ui/core";

import Styles from "../styles";

const FeedCard = function (props) {
  let tags = [];
  if(props.feed){
    if(props.feed.tags.indexOf(",") > -1)
      tags = props.feed.tags.split(',');
    else tags.push(props.feed.tags);
  }

  const enableFeed = () => {
    let params = {id: props.feed.id};
    if(props.feed.manage_enabled=='false')
      params['manage_enabled'] = 'true';
    else params['manage_enabled'] = 'false';
    fetch('/api/feedenable', {
      method: 'put',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': props.client.transports[0].auth.csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify(params)
    }).then(res=>{return res.json()})
    .then(res=>{
      props.saveFeed(res);
    })
  }

  return (
    <section className="section app-card" style={Styles.FeedStoreCard}>
      <div className="columns">
        <div className="column is-one-thirds">
          <Grid container>
            <Grid item xs={12} md={10}>
              <div>
                <span> Name: </span>
                <span> {props.feed? props.feed.name : ""} </span>
              </div>
              <div>
                <span> Description: </span>
                <span> {props.feed? props.feed.description: ""} </span>
              </div>
              <div>
                <span> URL: </span>
                <span> {props.feed? props.feed.url : ""} </span>
              </div>
              <div>
                <span>
                  <button className="button is-primary is-rounded mx-1" >
                    <span>{props.feed.category ? props.feed.category.name : ""}</span>
                  </button>
                  {
                    tags.map((tag, index) => {
                      return (
                        <button key={index} className="button is-info is-rounded mx-1" >
                          <span>{tag}</span>
                        </button>
                      );
                    })
                  }
                </span>
              </div>
            </Grid>
            <Grid item xs={12} md={2} >
              <Link to="/feeds" >
                <button className={props.feed.manage_enabled=='true' ? "button is-fullwidth is-success" : "button is-fullwidth is-outlined"} onClick={enableFeed}>
                  <span>{props.feed.manage_enabled == 'true'? "Enable": "Disable"}</span>
                </button>
              </Link>
              <Link to={`/feeds/edit/${props.feed.id}`} className="button is-text">
                <span>{props.feed.manage_enabled == 'true'? "Edit settings and enable" : "Edit settings"}</span>
              </Link>
            </Grid>
          </Grid>
        </div>
      </div>
    </section>
  );
}

export default FeedCard;
