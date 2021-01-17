import React, { useState, useEffect } from "react";
import { Link, useHistory } from "react-router-dom";
import { TextField, Container, Grid } from "@material-ui/core";
import Alert from '@material-ui/lab/Alert';

const AddWhitelist = (props) => {
    const [isAlert, setIsAlert] = useState(false);
    const [indicator, setIndicator] = useState('');
    const [value, setValue] = useState('');
    const history = useHistory();

    const AddList = () => {
        let params = {indicator: indicator, value: value, enabled:'Disable'};
        if(indicator != '' && value != '')
            fetch('/api/whitelist', {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': props.client.transports[0].auth.csrfToken
                },
                credentials: 'same-origin',
                body: JSON.stringify(params)
            }).then(res=>{return res.json()})
            .then(res=>{
                props.saveWhitelist(res);
                history.push('/whitelist');
                setIsAlert(false);
            })
        else setIsAlert(true);
    }

	return (
		<Container>
            <section className="section">
                <h1 className="title is-3">Add to whitelist</h1>
            </section>
            <section className="section app-card">
                {isAlert && <Alert severity="warning" onClose={()=>setIsAlert(false)}>Please input params exactly!!!</Alert>}
                <Grid container className="column is-two-thirds" direction="row" justify="center" alignItems="center">
                    <Grid item xs={3} className="my-4">
                        <span className="title is-5">Indicator Type</span>
                    </Grid>
                    <Grid item xs={9}>
                        <TextField
                            id="outlined-select-currency-native"
                            fullWidth
							select
							value={indicator}
							onChange={(event) => setIndicator(event.target.value)}
							SelectProps={{
								native: true,
							}}
							variant="outlined"
						>
							<option value=''>Select Indicator</option>
							{props.indicators.map((indicator) => (
								<option key={indicator.id} value={indicator.id}>
									{indicator.globalindicator.value}
								</option>
							))}
						</TextField>
                    </Grid>
                </Grid>
                <Grid container className="column is-two-thirds">
                    <Grid item xs={3}>
                        <span className="title is-5">Indicator value to exclude</span>
                    </Grid>
                    <Grid item xs={9}>
                        <TextField id="outlined-basic" fullWidth variant="outlined" onChange={(e)=>setValue(e.target.value)} />
                    </Grid>
                </Grid>
                <div className="section">
                    <span>
                        <button className="button is-success" onClick={AddList} >
                            <span className="title is-4">Enable</span>
                        </button>
                        <Link to ="/whitelist">
                            <button className="button is-text">
                                <span className="title is-4">back</span>
                            </button>
                        </Link>
                    </span>
                </div>
            </section>
        </Container>
	);
}

export default AddWhitelist;