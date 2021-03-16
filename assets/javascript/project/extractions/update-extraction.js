import React, { useState } from "react";
import { Link, useHistory } from 'react-router-dom';
import { Container, TextField, Dialog } from "@material-ui/core";
import { Alert, AlertTitle } from '@material-ui/lab';
import { Steps } from 'intro.js-react';

const UpdateExtraction = (props) => {
    const [type, setType] = useState(props.attribute || '');
    const [typeError, setTypeError] = useState(false);
    const [value, setValue] = useState(props.value || '');
    const [valueError, setValueError] = useState(false);
    const [words, setWords] = useState(props.words_matched || '');
    const [wordsError, setWordsError] = useState(false);
    const [bannerAdd, setBannerAdd] = useState(false);
    const [bannerCustom, setBannerCustom] = useState(false);
    const history = useHistory();
    const [stepsEnabled, setStepsEnabled] = useState(true);
    const steps = [{
        element: '#type',
        intro: 'Type of Attribute'
    }, {
        element: '#value',
        intro: 'Value of Attribute'
    }, {
        element: '#words',
        intro: 'Words to match on'
    }, {
        element: '#button',
        intro: 'Click to create new attribute'
    }]

    const saveExtraction = () => {
        if (props.customobservable) {
            let params = {
                attribute: type.trim(),
                value: value.trim(),
                words_matched: words.trim(),
                isenable: true,
                currentgroup: props.currentgroup
            }
            if (props.currentgroup == '') setGroupError(true);
            if (type == '' || value == '' || words == '') setIsAlert(true);
            if (type != '' && value != '' && words != '' && props.currentgroup != '') {
                fetch('/api/attributes', {
                    method: 'post',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': props.client.transports[0].auth.csrfToken,
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(params)
                }).then(res => { return res.json() })
                    .then(res => {
                        if (Boolean(res.message)) {
                            setBannerAdd(true);
                        }
                        else {
                            props.saveExtraction(res);
                            history.push('/extractions');
                        }
                    })
            }
        }
        if (props.isAutoDown || !props.customobservable) {
            setBannerCustom(true);
        }
    }

    const setOnboarding = () => {
        fetch('/api/onboarding', {
            method: 'get',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': props.client.transports[0].auth.csrfToken,
            },
            credentials: 'same-origin',
        }).then(res => { return res.json(); })
            .then(res => {
                setStepsEnabled(false);
                window.location.href = "/app"
            })
    }

    return (
        <Container>
            {props.onboarding &&
                <Steps
                    enabled={stepsEnabled}
                    steps={steps}
                    initialStep={0}
                    options={{ skipLabel: 'Skip' }}
                    onBeforeChange={(nextIndex) => {
                        if (nextIndex == 0 || (nextIndex == 1 && type.trim() != '')) {
                            return true;
                        }
                        else if (nextIndex == 2 && value.trim() != '') {
                            return true;
                        }
                        else if (nextIndex == 3 && words.trim() != '') {
                            return true
                        }
                        else {
                            return false;
                        }
                    }}
                    onAfterChange={(nextIndex, newElement) => {
                        document.querySelector('.introjs-skipbutton').addEventListener('click', function () {
                            setOnboarding();
                        })
                        if (nextIndex == 3) {
                            document.querySelector('.introjs-donebutton').style.display = 'none';
                            newElement.addEventListener('click', function () {
                                setStepsEnabled(false);
                                window.location.href = "/app/whitelist"
                            })
                        }
                    }}
                    onBeforeExit={(index) => {
                        if (index == 1) {
                            setOnboarding();
                        }
                        return false;
                    }}
                    onExit={() => { }}
                />}
            <section className="section app-card">
                <Dialog
                    maxWidth="md"
                    fullWidth
                    open={bannerAdd}
                    onClose={() => setBannerAdd(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <Alert severity="error" className="my-5 has-text-centered">
                        <AlertTitle className="subtitle is-4 has-text-weight-bold">Error</AlertTitle>
                        <span className="subtitle is-5">The attribute already exists! Please find out it and edit.</span>
                    </Alert>
                </Dialog>
                <Dialog
                    maxWidth="md"
                    fullWidth
                    open={bannerCustom}
                    onClose={() => setBannerCustom(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <Alert severity="error" className="my-5 has-tet-centered">
                        <AlertTitle className="subtitle is-4 has-text-weight-bold">Error</AlertTitle>
                        <span className="subtitle is-5">Sorry, your plan does not currently cover custom attribute abstractions. You can upgrade now to enable this feature here.</span>
                    </Alert>
                </Dialog>
                <div className="columns">
                    <div className="column">
                        <TextField
                            label="Type"
                            id="type"
                            fullWidth
                            placeholder="Type of attribute e.g. Threat type"
                            margin="normal"
                            InputLabelProps={{
                                shrink: true,
                            }}
                            variant="outlined"
                            value={type}
                            onChange={(e) => { setType(e.target.value); setTypeError(false); }}
                        />
                        {typeError && <p className="help is-danger"><span>This field may not be blank.</span></p>}
                        <TextField
                            label="Value"
                            id="value"
                            fullWidth
                            placeholder="Value of attribute e.g. Data Breach"
                            margin="normal"
                            InputLabelProps={{
                                shrink: true,
                            }}
                            variant="outlined"
                            value={value}
                            onChange={(e) => { setValue(e.target.value); setValueError(false); }}
                        />
                        {valueError && <p className="help is-danger"><span>This field may not be blank.</span></p>}
                        <TextField
                            label="Words"
                            id="words"
                            fullWidth
                            placeholder="Words to match on e.g. data breach, leak, exposed"
                            margin="normal"
                            InputLabelProps={{
                                shrink: true,
                            }}
                            variant="outlined"
                            value={words}
                            onChange={(e) => { setWords(e.target.value); setWordsError(false); }}
                        />
                        {wordsError && <p className="help is-danger"><span>This field may not be blank.</span></p>}
                    </div>
                </div>
                <button className="button is-primary" id="button" onClick={() => saveExtraction()}>
                    Save
                </button>
                <Link to="/extractions">
                    <button className="button is-text">
                        <span>Cancel</span>
                    </button>
                </Link>
            </section>
        </Container>
    );
}

export default UpdateExtraction;