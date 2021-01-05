// import 'date-fns';
import React, { useState } from "react";
import { useHistory } from "react-router-dom";
import { Container, TextField, Grid } from "@material-ui/core";
import {
    MuiPickersUtilsProvider,
    KeyboardDatePicker,
} from '@material-ui/pickers';
import DateFnsUtils from '@date-io/date-fns';

import { getAction } from "../../api";
import { API_ROOT } from "../const";
import Styles from "../styles";

const ManagePlan = (props) => {
    console.log(props);
    const [plan, setPlan] = useState('');
    const [billing, setBilling] = useState('');
    const [billingname, setBillingName] = useState('');
    const [billingemail, setBillingEmail] = useState('');
    const [credit, setCredit] = useState('');
    const [expiry, setExpiry] = useState(new Date('2014-08-18T21:11:54'));
    const [cvv, setCVV] = useState('');
    const history = useHistory();

    const Manage = () => {
        let params = {
            plan: plan,
            billing: billing,
            name: billingname,
            email: billingemail,
            credit: credit,
            expiry: expiry,
            cvv: cvv
        };
        // const action = getAction(API_ROOT, ['plans', 'create']);
        // props.client.action(window.schema, action, params).then((result)=>{
        //     console.log(reuslt);
        //     history.push('/manageplan')
        // })
    }
    return (
        <Container>
            <section className="section" >
                <h1 className="title is-3">Manage Plan</h1>
            </section>
            <section className="section app-card">
                <Grid container className="section" style={Styles.SectionStyle}>
                    <Grid item xs={3}>
                        <span>Plan selected</span>
                    </Grid>
                    <Grid item xs={9}>
                        <TextField
                            id="outlined-select-currency-native"
                            select
                            fullWidth
                            placeholder="Select plan"
                            value={plan}
                            onChange={(e)=>setPlan(e.target.value)}
                            SelectProps={{
                                native: true,
                            }}
                            variant="outlined"
                        >
                            {props.plans.map((plan) => (
                                <option key={plan.id} value={plan.id}>
                                    {plan.name}
                                </option>
                            ))}
                        </TextField>
                    </Grid>
                </Grid>
                <Grid container className="section" style={Styles.SectionStyle}>
                    <Grid item xs={3}>
                        <span>Billing</span>
                    </Grid>
                    <Grid item xs={9}>
                        <TextField
                            id="outlined-select-currency-native"
                            select
                            fullWidth
                            placeholder="Select billing"
                            value={billing}
                            onChange={(e)=>setPlan(e.target.value)}
                            SelectProps={{
                                native: true,
                            }}
                            variant="outlined"
                        >
                            {props.plans.map((plan) => (
                                <option key={plan.id} value={plan.id}>
                                    {'Annual @ $'+plan.annual_price/10+'/mo'}
                                </option>
                            ))}
                        </TextField>
                    </Grid>
                </Grid>
                <Grid container className="section" style={Styles.SectionStyle}>
                    <Grid item xs={3}>
                        <span>Billing name</span>
                    </Grid>
                    <Grid item xs={9}>
                        <TextField fullWidth id="outlined-basic" placeholder="e.g. Billing" variant="outlined" onChange={(e)=>setBillingName(e.target.value)} />
                    </Grid>
                </Grid>
                <Grid container className="section" style={Styles.SectionStyle}>
                    <Grid item xs={3}>
                        <span>Billing email</span>
                    </Grid>
                    <Grid item xs={9}>
                        <TextField fullWidth id="outlined-basic" placeholder="e.g. example@gmail.com" variant="outlined" onChange={(e)=>setBillingEmail(e.target.value)}/>
                    </Grid>
                </Grid>
                <Grid container className="section" style={Styles.SectionStyle}>
                    <Grid item xs={3}>
                        <span>Credit card number</span>
                    </Grid>
                    <Grid item xs={9}>
                        <TextField fullWidth id="outlined-basic" placeholder="e.g. 42424424242" variant="outlined" onChange={(e)=>setCredit(e.target.value)} />
                    </Grid>
                </Grid>
                <Grid container className="section" style={Styles.SectionStyle}>
                    <Grid item xs={3}>
                        <span>Expiry</span>
                    </Grid>
                    <Grid item xs={9}>
                    {/* <MuiPickersUtilsProvider utils={DateFnsUtils}>
                        <KeyboardDatePicker
                            margin="normal"
                            id="date-picker-dialog"
                            label="Date picker dialog"
                            format="MM/dd/yyyy"
                            value={expiry}
                            // onChange={(e)=>setExpiry(e.target.value)}
                            KeyboardButtonProps={{
                                'aria-label': 'change date',
                            }}
                        />
                    </MuiPickersUtilsProvider> */}
                    </Grid>
                </Grid>
                <Grid container className="section" style={Styles.SectionStyle}>
                    <Grid item xs={3}>
                        <span>CVV</span>
                    </Grid>
                    <Grid item xs={9}>
                        <TextField fullWidth id="outlined-basic" placeholder="" variant="outlined" onChange={(e)=>setCVV(e.target.value)} />
                    </Grid>
                </Grid>
                <div className="section columns is-centered">
                <button className="button is-success" onClick={Manage}><span>Upgrade to this plan</span></button>
                </div>
            </section>
        </Container>
    );
}

export default ManagePlan;