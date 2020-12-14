import React, {useState, useEffect} from 'react';
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link,
} from "react-router-dom";

const CreateIntelgroup = function() {
    console.log('aaa');
    const createNewIntelGroup = function() {
        <div id="fullpage-form-wrapper">
            <div id="fullpage-form">
                <h1 class="title is-size-4">Create new Intel Group</h1>
                <Form method="post">
                    <div class="field">
                        <label class="label">Intel Group name</label>
                        <div class="control">
                            <input type="text" placeholder="www.x.com/rss" />
                        </div>
                    </div>
                    <div class="field">
                        <label class="label">Intel Group desc(optional)</label>
                        <div class="control">
                            <input type="text" placeholder="www.x.com/rss" />
                        </div>
                    </div>
                    <div class="field">
                        <label class="label">Add other users</label>
                        <div class="control">
                            <input type="text" placeholder="www.x.com/rss" />
                        </div>
                    </div>
                    <input class="button is-primary is-fullwidth" type="submit" value="Register"/>
                </Form>
            </div>
        </div>
    }; 
    return (
        <Router basename='/'>
            <Switch>
                <Route path="/">
                    {createNewIntelGroup()}
                </Route>
            </Switch>
        </Router>
    );
};
export default CreateIntelgroup;