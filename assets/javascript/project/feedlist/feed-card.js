import React from "react";
import { Grid } from "@material-ui/core";

import Styles from "../styles";

const FeedCard = function (props) {
  let tags = [];
  if (props.feed) {
    if (props.feed.tags.trim() != '') {
      if (props.feed.tags.indexOf(",") > -1)
        tags = props.feed.tags.split(',');
      else tags.push(props.feed.tags);
    }
  }

  const enableFeed = () => {
    let params = {
      id: props.feed.id
    };
    fetch('/api/configuredfeeds', {
      method: 'put',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': props.client.transports[0].auth.csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify(params)
    }).then(res => { return res.json() })
      .then(res => {
        props.saveFeed(res);
      })
  }

  const deleteFeed = () => {
    let params = {
      id: props.feed.id
    };
    if (confirm('Are you sure to delete this feed?')) {
      fetch('/api/configuredfeeds', {
        method: 'delete',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': props.client.transports[0].auth.csrfToken
        },
        credentials: 'same-origin',
        body: JSON.stringify(params)
      }).then(res => { return res.json() })
        .then(res => {
          props.saveFeed(res);
        });
    }
  }

  return (
    <section className="section app-card" style={Styles.FeedStoreCard}>
      <div className="columns">
        <div className="column is-one-thirds">
          <Grid container>
            <Grid item xs={12} md={6}>
              <div>
                <span> Name: </span>
                <span> {props.feed ? props.feed.name : ""} </span>
              </div>
              <div>
                <span> Description: </span>
                <span> {props.feed ? props.feed.description : ""} </span>
              </div>
              <div>
                <span> URL: </span>
                <span> {props.feed ? props.feed.feed.url : ""} </span>
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
            <Grid item xs={12} md={4}>
              <div>
                <span> Last polled: </span>
                <span> {props.feed ? new Date(props.feed.feed.updated_at).toLocaleString() : ""} </span>
              </div>
              <div>
                <span> Last data: </span>
                <span> {props.channel ? props.channel.title : ""} </span>
              </div>
              <div>
                <span> Total intel collected: </span>
                <span> {props.count ? props.count : ""} </span>
              </div>
            </Grid>
            <Grid item xs={12} md={2} >
              {props.currentrole.role == 2 && <button className={props.feed.isenable ? "button is-fullwidth" : "button is-fullwidth is-success"} onClick={enableFeed}>
                <span className="is-size-4">{props.feed.isenable ? "Disable" : "Enable"}</span>
              </button>}
              {props.currentrole.role == 2 && <button className="button is-fullwidth is-text" onClick={deleteFeed}>
                <span>Delete</span>
              </button>}
            </Grid>
          </Grid>
        </div>
      </div>
    </section>
  );
}

export default FeedCard;
