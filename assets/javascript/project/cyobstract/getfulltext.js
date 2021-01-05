import React, { useState, useEffect } from "react";
import { Link, Route, Switch } from "react-router-dom";

import { getAction } from "../../api";
import { API_ROOT } from "../const";


const GetFullText = () => {
    let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
    const client = new coreapi.Client({auth: auth});
    const [data, setData] = useState('');

    useEffect(() => {
        const action = getAction(API_ROOT, ['fulltext', 'fulltext']);
        client.action(window.schema, action).then((result) => {
            console.log(result);
            setData(result.rss.channel.description);
        })
    },[]);

    return (
        <div>
            {data}
        </div>
    );
    
}

export default GetFullText;